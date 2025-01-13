"""Module containing the Builder class."""
from __future__ import annotations
from os import PathLike
from sys import stdout

import build123d as _
from tabulate import tabulate

from .mutation import Mutation
from .colors import ColorLike
from .shapes import Hash, FaceListLike, EdgeListLike, FaceDict, EdgeDict


class Builder:
    """A class used to manipulated Build123d objects that keeps track of each
    performed mutation and manage shape colors."""

    debug_alpha = 0.2
    "The alpha values used for translucent shapes in debug mode."

    default_color: ColorLike = "orange"
    "The default color to be used when a color is passed to a mutation"

    def __init__(self, part: _.Part, color: ColorLike|None=None, debug=False):
        self.object = part
        self.mutations: list[Mutation] = []
        self.debug_faces: dict[Hash, ColorLike] = {}
        self.mutate(self.__class__.__name__, part, color, debug)

    def __getitem__(self, mut_idx: int):
        return self.mutations[mut_idx]

    def __call__(self) -> list[_.Face]:
        faces = self.mutations[-1].faces
        faces_color = self.get_faces_color()

        for debug_hash in self.debug_faces:
            if debug_hash not in faces:
                faces[debug_hash] = self.get_face(debug_hash)

        for face_hash, face in faces.items():
            face.color = faces_color[face_hash] or self.default_color
            face.label = face_hash[:6]

        return list(faces.values())

    def __iadd__(self, part: Builder|_.Part):
        self.add(part)
        return self

    def __isub__(self, part: Builder|_.Part):
        self.sub(part)
        return self

    def __imul__(self, location: _.Location):
        self.move(location)
        return self

    def __iand__(self, part: Builder|_.Part):
        self.intersect(part)
        return self

    def get_face(self, face_hash: Hash, from_end=True) -> _.Face:
        """Return a face based on its hash by iterating over all the mutations,
        allowing to find removed faces, either from begining or from the end."""
        mutations = reversed(self.mutations) if from_end else self.mutations

        for mutation in mutations:
            if face_hash in mutation.faces:
                return mutation.faces[face_hash]

        raise KeyError

    def get_face_mutation(self, face: _.Face|Hash) -> Mutation:
        """Retrieve the mutation who created the given face."""

        _hash = Mutation.hash_shape(face) if isinstance(face, _.Face) else face
        for mutation in self.mutations:
            if _hash in mutation.faces:
                return mutation
        raise ValueError

    def get_edge_mutation(self, edge: _.Edge|Hash) -> Mutation:
        """Retrieve the mutation who created the given edge."""

        _hash = Mutation.hash_shape(edge) if isinstance(edge, _.Edge) else edge
        for mutation in self.mutations:
            if _hash in mutation.edges:
                return mutation
        raise ValueError

    def get_faces_color(self) -> dict[Hash, ColorLike|None]:
        """Return a dictionnary containing the color of each face of the current
        object."""

        faces_color: dict[Hash, ColorLike|None] = {}

        for mut in self.mutations:

            for face_hash in mut.faces_added:
                color = mut.color
                if mut.faces_alias:
                    old_hash = mut.faces_alias[face_hash]
                    color = faces_color[old_hash]

                faces_color[face_hash] = color

            rm_colors = {faces_color[rm_hash] for rm_hash in mut.faces_removed}

            if len(rm_colors) == 1:
                rm_color = rm_colors.pop() if len(rm_colors) == 1 else None
                for face_hash in mut.faces_altered:
                    faces_color[face_hash] = rm_color
            else:
                for al_hash, al_face in mut.faces_altered.items():
                    for rm_hash, rm_face in mut.faces_removed.items():
                        if Mutation.is_altered_faces(al_face, rm_face):
                            faces_color[al_hash] = faces_color[rm_hash]

        if self.debug_faces:
            for face_hash, color in faces_color.items():
                if face_hash in self.debug_faces:
                    faces_color[face_hash] = self.debug_faces[face_hash]
                else:
                    r, v, b = self.cast_color(color).to_tuple()[:3]
                    faces_color[face_hash] = _.Color(r, v, b, self.debug_alpha)

        return faces_color

    def get_mutation(self, mutation_id: str) -> Mutation|None:
        """Return the mutation identified by the given id."""

        for mutation in self.mutations:
            if mutation.id == mutation_id:
                return mutation
        return None

    @classmethod
    def _cast_faces(cls, faces: FaceListLike, fake_hashes=False) -> FaceDict:
        """Cast the given faces to a FaceDict. If hashes are not used, set
        `fake_hashes` to True for better performance."""

        if isinstance(faces, FaceDict):
            return faces

        if isinstance(faces, _.Face):
            face_hash = 'f' if fake_hashes else Mutation.hash_shape(faces)
            return FaceDict({face_hash: faces})

        faces_dict = FaceDict({})
        for idx, face in enumerate(faces):
            face_hash = str(idx) if fake_hashes else Mutation.hash_shape(face)
            faces_dict[face_hash] = face
        return faces_dict

    @classmethod
    def _cast_edges(cls, edges: EdgeListLike, fake_hashes=False) -> EdgeDict:
        """Cast the given edges an EdgeDict. If hashes are not used, set
        `fake_hashes` to True for better performance."""

        if isinstance(edges, EdgeDict):
            return edges

        if isinstance(edges, _.Edge):
            edge_hash = 'f' if fake_hashes else Mutation.hash_shape(edges)
            return EdgeDict({edge_hash: edges})

        edges_dict = EdgeDict({})
        for idx, edge in enumerate(edges):
            edge_hash = str(idx) if fake_hashes else Mutation.hash_shape(edge)
            edges_dict[edge_hash] = edge
        return edges_dict

    @classmethod
    def _cast_part(cls, part: Builder|_.Part) -> _.Part:
        """Cast an EdgeListLike to a Edge iterable."""
        return part if isinstance(part, _.Part) else part.object

    @classmethod
    def cast_color(cls, color: ColorLike) -> _.Color:
        """Cast a ColorLike to a Color"""
        return color if isinstance(color, _.Color) else _.Color(color)

    @classmethod
    def _part_color(cls, part: Builder|_.Part) -> ColorLike|None:
        """Retrieve the color of the current object."""

        if isinstance(part, Builder) and len(part.mutations) == 1:
            return part.mutations[-1].color
        return None

    def mutate(
            self,
            name: str,
            obj: _.Part,
            color: ColorLike|None,
            debug: bool,
            faces_alias: dict[Hash, Hash]|None=None
        ) -> Mutation:
        """Base mutation: mutate the current object to the given one by applying
        a mutation with the given name, color and debug mode."""

        self.object = obj

        mutation = Mutation(
            obj,
            self.mutations[-1] if self.mutations else None,
            name,
            len(self.mutations),
            color,
            faces_alias
        )

        if debug:
            for face_hash in mutation.faces_added:
                self.debug_faces[face_hash] = color

        self.mutations.append(mutation)
        return mutation

    def move(self, location: _.Location, color: ColorLike|None=None, debug=False) -> Mutation:
        """Mutation: move the object to the given location, keeping the colors.
        with the given color and debug mode.
        If not color is defined, keep the previous ones for each face."""

        obj = location * self.object
        faces_alias: dict[Hash, Hash] = {}

        for face in self.object.faces():
            old_hash = Mutation.hash_shape(face)
            new_hash = Mutation.hash_shape(location * face)
            faces_alias[new_hash] = old_hash

        return self.mutate('move', obj, color, debug, faces_alias)

    def add(
            self,
            part: Builder|_.Part,
            color: ColorLike|None=None,
            debug=False
        ) -> Mutation:
        """Mutation: fuse the given part to the current object.
        with the given color and debug mode."""

        obj = self.object + self._cast_part(part)
        return self.mutate('add', obj, color or self._part_color(part), debug)

    def sub(
            self,
            part: Builder|_.Part,
            color: ColorLike|None=None,
            debug=False
        ) -> Mutation:
        """Mutation: substract the given part from the current object,
        with the given color and debug mode."""

        obj = self.object - self._cast_part(part)
        return self.mutate('sub', obj, color or self._part_color(part), debug)

    def intersect(
            self,
            part: Builder|_.Part,
            color: ColorLike|None=None,
            debug=False
        ) -> Mutation:
        """Mutation: intersects the given part to the current object,
        with the given color and debug mode."""

        obj = self.object & self._cast_part(part)
        return self.mutate('inter', obj, color or self._part_color(part), debug)

    def fillet(
            self,
            edges: EdgeListLike,
            radius: float,
            color: ColorLike|None=None,
            debug=False
        ) -> Mutation:
        """Mutation: apply a fillet of the given radius to the given edges of
        the current object, with the given color and debug mode."""

        edges = self._cast_edges(edges, fake_hashes=True)()
        obj = self.object.fillet(radius, edges)
        return self.mutate('fillet', obj, color, debug)

    def chamfer(
            self,
            edges: EdgeListLike,
            length: float,
            length2: float|None=None,
            face: _.Face|None=None,
            color: ColorLike|None=None,
            debug=False
        ) -> Mutation:
        """Mutation: apply a chamfer of the given length to the given edges of
        the current object, with the given color and debug mode."""

        edges = self._cast_edges(edges, fake_hashes=True)()
        obj = self.object.chamfer(length, length2, edges, face) # type: ignore
        return self.mutate('chamfer', obj, color, debug)

    def info(self, file=None, style="fancy_grid"):
        """Print the list of mutations to the given file (stdout by default)."""

        def row(mutation: Mutation) -> tuple[str, str, str, str]:
            return (
                str(mutation.index),
                mutation.id,
                mutation.name,
                str(mutation.color),
            )

        headers=["Idx", "Id", "Type", "Color"]
        table = [row(mutation) for mutation in self.mutations]
        print(tabulate(table, headers, tablefmt=style), file=file or stdout)

    def debug(self, faces: FaceListLike, color: ColorLike="red"):
        """Set a face for debugging, so it will appear in the given color while
        the rest of the object will be translucent."""

        for face_hash in self._cast_faces(faces):
            self.debug_faces[face_hash] = color

    def export(
            self,
            exporter: _.Export2D,
            file_path: PathLike|bytes|str,
            include_part=True
        ):
        """Export the current object using the given exporter in the given file
        path. If `include_part` is false, do not include the object."""

        if include_part:
            exporter.add_shape(self.object) # type: ignore
        exporter.write(file_path) # type: ignore

    def export_stl(
            self,
            file_path: PathLike|bytes|str,
            tolerance: float = 0.001,
            angular_tolerance: float = 0.1,
            ascii_format: bool = False
        ):
        """Export the current object in STL format to the given file path,
        with the given tolerance, angular tolerance and ascii format mode."""
        _.export_stl(self.object, file_path, tolerance, angular_tolerance, ascii_format)
