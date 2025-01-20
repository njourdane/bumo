"""Module containing the Builder class."""
from __future__ import annotations
from os import PathLike
from sys import stdout

import build123d as _
from tabulate import tabulate

from .mutation import Mutation
from .mode import Mode, ModeType, AUTO
from .colors import ColorLike, cast_color, color_to_str, get_rvb
from .shapes import Hash, FaceListLike, EdgeListLike, FaceDict, EdgeDict, add_face_hash, add_edge_hash, ShapeList
from . import config


class Builder:
    """A class used to manipulate Build123d objects that keeps track of each
    mutation and manage shape colors."""

    def __init__(self):

        self.object = _.Part(None)
        self.mutations: list[Mutation] = []
        self.faces_modes: dict[Hash, Mode] = {}
        self.faces = FaceDict({})

    def __getitem__(self, mut_idx: int):
        return self.mutations[mut_idx]

    def get_faces_colors(self) -> dict[Hash, _.Color]:
        palette = config.COLOR_PALETTE.build_palette(len(self.mutations))
        faces_mutations = self.get_faces_mutations()
        faces_last: list[Hash] = list(self.mutations[-1].faces.keys())

        def get_color(face_hash):
            mode = self.faces_modes[face_hash]
            mut_idx = faces_mutations[face_hash]
            return mode.get_color(palette[mut_idx])

        faces_debug = {
            face_hash: mode.color
            for face_hash, mode in self.faces_modes.items()
            if mode.mode_type == ModeType.DEBUG
        }

        if faces_debug:
            ghost_colors = {
                fg_h: _.Color(*get_rvb(get_color(fg_h)), config.DEBUG_ALPHA)
                for fg_h in faces_last
            }
            return {
                **ghost_colors,
                **faces_debug,
            }

        return {fl_h: get_color(fl_h) for fl_h in faces_last}

    def __call__(self) -> list[_.Face]:
        if not self.mutations:
            raise ValueError("No mutation to show.")

        faces_colors = self.get_faces_colors()
        faces_to_show: list[_.Face] = []

        for face_hash, face_color in faces_colors.items():
            face = self.faces[face_hash]
            face.color = face_color
            face.label = face_hash[:6]
            faces_to_show.append(face)

        return faces_to_show


    def __iadd__(self, part: Builder | _.Part):
        self.add(part)
        return self

    def __isub__(self, part: Builder | _.Part):
        self.sub(part)
        return self

    def __imul__(self, location: _.Location):
        self.move(location)
        return self

    def __iand__(self, part: Builder | _.Part):
        self.intersect(part)
        return self

    # def get_face(self, face_hash: Hash, from_end=True) -> _.Face:
    #     """Return a face based on its hash by iterating over all the mutations,
    #     allowing to find removed faces, either from begining or from the end."""
    #     mutations = reversed(self.mutations) if from_end else self.mutations

    #     for mutation in mutations:
    #         if face_hash in mutation.faces:
    #             return mutation.faces[face_hash]

    #     raise KeyError

    def get_face_mutation(self, face: _.Face | Hash) -> Mutation:
        """Retrieve the mutation who created the given face."""

        _hash = add_face_hash(face).label if isinstance(face, _.Face) else face
        for mutation in self.mutations:
            if _hash in mutation.faces:
                return mutation
        raise ValueError

    def get_edge_mutation(self, edge: _.Edge | Hash) -> Mutation:
        """Retrieve the mutation who created the given edge."""

        _hash = add_edge_hash(edge).label if isinstance(edge, _.Edge) else edge
        for mutation in self.mutations:
            if _hash in mutation.edges:
                return mutation
        raise ValueError

    def get_faces_mutations(self) -> dict[Hash, int]:
        """Return a dictionnary containing for each face hash, the mutation that
        created the face."""

        # TODO: store dict in builder and apply on each mutation?
        faces_mutations: dict[Hash, int] = {}

        for mutation in self.mutations:

            for face_hash in mutation.faces_added:
                faces_mutations[face_hash] = (
                    faces_mutations[mutation.faces_alias[face_hash]]
                    if mutation.faces_alias
                    else mutation.index
                )

            rm_muts = {faces_mutations[rm_h] for rm_h in mutation.faces_removed}

            if len(rm_muts) == 1:
                rm_color = rm_muts.pop()

                for face_hash in mutation.faces_altered:
                    faces_mutations[face_hash] = rm_color
            else:
                for al_hash, al_face in mutation.faces_altered.items():
                    for rm_hash, rm_face in mutation.faces_removed.items():
                        if Mutation.is_altered_faces(al_face, rm_face):
                            faces_mutations[al_hash] = faces_mutations[rm_hash]

        return faces_mutations

    def get_mutation(self, mutation_id: str) -> Mutation:
        """Return the mutation identified by the given id."""

        for mutation in self.mutations:
            if mutation.id == mutation_id:
                return mutation
        raise KeyError

    @classmethod
    def _cast_faces(cls, faces: FaceListLike) -> FaceDict:
        """Cast the given faces to a FaceDict."""

        if isinstance(faces, FaceDict):
            return faces

        if isinstance(faces, _.Face):
            face = add_face_hash(faces)
            return FaceDict({face.label: face})

        faces_dict = FaceDict({})
        for face in faces:
            face = add_face_hash(face)
            faces_dict[face.label] = face
        return faces_dict

    @classmethod
    def _cast_edges(cls, edges: EdgeListLike) -> EdgeDict:
        """Cast the given edges an EdgeDict."""

        if isinstance(edges, EdgeDict):
            return edges

        if isinstance(edges, _.Edge):
            edge = add_edge_hash(edges)
            return EdgeDict({edge.label: edge})

        edges_dict = EdgeDict({})
        for edge in edges:
            edge = add_edge_hash(edge)
            edges_dict[edge.label] = edge
        return edges_dict

    @classmethod
    def _cast_part(cls, part: Builder | _.Part) -> _.Part:
        """Cast an EdgeListLike to a Edge iterable."""
        return part if isinstance(part, _.Part) else part.object

    # @classmethod
    # def _part_color(cls, part: Builder | _.Part) -> _.Color|None:
    #     """Retrieve the color of the given object."""

    #     if isinstance(part, Builder) and len(part.mutations) == 1:
    #         return part.mutations[-1].color
    #     return None

    def mutate(
            self,
            name: str,
            obj: _.Part,
            mode: Mode,
            faces_alias: dict[Hash, Hash] | None=None
        ) -> Mutation:
        """Base mutation: mutate the current object to the given one by applying
        a mutation with the given name, color and debug mode."""

        self.object = obj
        # _color = cast_color(color)

        # TODO: remove faces_alias from mutation?
        # Pass them to builder faces dict instead?
        mutation = Mutation(
            obj,
            self.mutations[-1] if self.mutations else None,
            name,
            len(self.mutations),
            faces_alias,
        )

        for face_hash, face in mutation.faces.items():
            if face_hash not in self.faces:
                self.faces[face_hash] = face

            self.faces_modes[face_hash] = mode

        # if debug:
        #     for face_hash in mutation.faces_added:
        #         self.debug_faces[face_hash] = (
        #             _color if color else config.DEFAULT_DEBUG_COLOR
        #         )

        self.mutations.append(mutation)
        return mutation

    def move(
            self,
            location: _.Location,
            mode: Mode = AUTO,
        ) -> Mutation:
        """Mutation: move the object to the given location, keeping the colors.
        with the given color and debug mode.
        If not color is defined, keep the previous ones for each face."""

        obj = location * self.object
        faces_alias: dict[Hash, Hash] = {}

        for face in ShapeList(self.object.faces()):
            face_moved = add_face_hash(location * face)
            faces_alias[face_moved.label] = face.label

        return self.mutate('move', obj, mode, faces_alias)

    def add(
            self,
            part: Builder | _.Part,
            mode: Mode = AUTO,
        ) -> Mutation:
        """Mutation: fuse the given part to the current object.
        with the given color and debug mode."""

        obj = self.object + self._cast_part(part)
        return self.mutate('add', obj, mode)

    def sub(
            self,
            part: Builder | _.Part,
            mode: Mode = AUTO,
        ) -> Mutation:
        """Mutation: substract the given part from the current object,
        with the given color and debug mode."""

        obj = self.object - self._cast_part(part)
        return self.mutate('sub', obj, mode)

    def intersect(
            self,
            part: Builder | _.Part,
            mode: Mode = AUTO,
        ) -> Mutation:
        """Mutation: intersects the given part to the current object,
        with the given color and debug mode."""

        obj = self.object & self._cast_part(part)
        return self.mutate('inter', obj, mode)

    def fillet(
            self,
            edges: EdgeListLike,
            radius: float,
            mode: Mode = AUTO,
        ) -> Mutation:
        """Mutation: apply a fillet of the given radius to the given edges of
        the current object, with the given color and debug mode."""

        edges = self._cast_edges(edges)()
        obj = self.object.fillet(radius, edges)
        return self.mutate('fillet', obj, mode)

    def chamfer(
            self,
            edges: EdgeListLike,
            length: float,
            length2: float | None=None,
            face: _.Face | None=None,
            mode: Mode = AUTO,
        ) -> Mutation:
        """Mutation: apply a chamfer of the given length to the given edges of
        the current object, with the given color and debug mode."""

        edges = self._cast_edges(edges)()
        obj = self.object.chamfer(length, length2, edges, face) # type: ignore
        return self.mutate('chamfer', obj, mode)

    def info(self, file=None):
        """Print the list of mutations to the given file (stdout by default)."""

        palette = config.COLOR_PALETTE.build_palette(len(self.mutations))

        def row(mut: Mutation) -> tuple:
            color = palette[mut.index] # FIXME
            r, g, b = [int(c * 255) for c in color.to_tuple()[:3]]

            start = f"\033[38;2;{ r };{ g };{ b }m"
            end = "\033[0m"

            columns = {
                "idx": str(mut.index),
                "label": mut.id,
                "type": mut.name,
                "color_hex": color_to_str(color, True),
                "color_name": color_to_str(color, False),
                "f+": str(len(mut.faces_added)),
                "f~": str(len(mut.faces_altered)),
                "f-": str(len(mut.faces_removed)),
                "e+": str(len(mut.edges_added)),
                "e~": str(len(mut.edges_altered)),
                "e-": str(len(mut.edges_removed)),
            }

            return tuple(
                (f"{ start }{ col }{ end }" if config.INFO_COLOR else col)
                for header, col in columns.items()
                if header in config.COLUMNS_MUTATIONS
            )

        str_table = tabulate(
            [row(mutation) for mutation in self.mutations],
            [header.title() for header in config.COLUMNS_MUTATIONS],
            config.INFO_TABLE_FORMAT
        )
        print(str_table, file=file or stdout)

    def debug(self, faces: FaceListLike, color: ColorLike | None=None):
        """Set a face for debugging, so it will appear in the given color while
        the rest of the object will be translucent."""

        _color = cast_color(color) if color else config.DEFAULT_DEBUG_COLOR
        for face_hash in self._cast_faces(faces).keys():
            self.faces_modes[face_hash] = Mode(ModeType.DEBUG, _color)

    def export(
            self,
            exporter: _.Export2D,
            file_path: PathLike | bytes | str,
            include_part=True
        ):
        """Export the current object using the given exporter in the given file
        path. If `include_part` is false, do not include the object."""

        if include_part:
            exporter.add_shape(self.object) # type: ignore
        exporter.write(file_path) # type: ignore

    def export_stl(
            self,
            file_path: PathLike | bytes | str,
            tolerance: float = 0.001,
            angular_tolerance: float = 0.1,
            ascii_format: bool = False
        ):
        """Export the current object in STL format to the given file path,
        with the given tolerance, angular tolerance and ascii format mode."""
        _.export_stl(
            self.object,
            file_path,
            tolerance,
            angular_tolerance,
            ascii_format
        )
