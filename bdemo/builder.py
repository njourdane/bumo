from __future__ import annotations
from os import PathLike
from typing import Iterable

import build123d as _

from .operation import Operation
from .utils import ColorLike, Hash
from .shapes import EdgeListLike, EdgeDict, FaceDict


class Builder:
    debug_alpha = 0.2
    default_color: ColorLike = "orange"

    def __init__(self, part: _.Part, color: ColorLike|None=None, debug=False):
        self.object = part
        self.operations: list[Operation] = []
        self.debug_faces: dict[Hash, ColorLike] = {}
        self.mutate(self.__class__.__name__, part, color, debug)

    def __getitem__(self, opr_idx: int):
        return self.operations[opr_idx]

    def __call__(self) -> list[_.Face]:
        faces = self.operations[-1].faces
        faces_color = self.get_faces_color()

        for face_hash, face in faces.items():
            face.color = faces_color[face_hash] or self.default_color
            face.label = face_hash[:6]

        return list(faces.values())

    def __mul__(self, location: _.Location) -> Builder:
        return Builder(location * self.object)

    def get_face_operation(self, face: _.Face|Hash) -> Operation:
        _hash = Operation.hash_shape(face) if isinstance(face, _.Face) else face
        for operation in self.operations:
            if _hash in operation.faces:
                return operation
        raise ValueError

    def get_edge_operation(self, edge: _.Edge|Hash) -> Operation:
        _hash = Operation.hash_shape(edge) if isinstance(edge, _.Edge) else edge
        for operation in self.operations:
            if _hash in operation.edges:
                return operation
        raise ValueError

    def get_faces_color(self) -> dict[Hash, ColorLike|None]:
        faces_color: dict[Hash, ColorLike|None] = {}

        for opr in self.operations:

            for face_hash in opr.faces_added:
                color = opr.color
                if opr.faces_alias:
                    old_hash = opr.faces_alias[face_hash]
                    color = faces_color[old_hash]

                faces_color[face_hash] = color

            rm_colors = {faces_color[rm_hash] for rm_hash in opr.faces_removed}

            if len(rm_colors) == 1:
                rm_color = rm_colors.pop() if len(rm_colors) == 1 else None
                for face_hash in opr.faces_altered:
                    faces_color[face_hash] = rm_color
            else:
                for al_hash, al_face in opr.faces_altered.items():
                    for rm_hash, rm_face in opr.faces_removed.items():
                        if Operation.is_altered_faces(al_face, rm_face):
                            faces_color[al_hash] = faces_color[rm_hash]

        if self.debug_faces:
            for face_hash, color in faces_color.items():
                if face_hash in self.debug_faces:
                    faces_color[face_hash] = self.debug_faces[face_hash]
                else:
                    r, v, b = self.cast_color(color).to_tuple()[:3]
                    faces_color[face_hash] = _.Color(r, v, b, self.debug_alpha)

        return faces_color

    def get_operation(self, opr_id: str) -> Operation|None:
        for operation in self.operations:
            if operation.id == opr_id:
                return operation
        return None

    def debug(self, faces: FaceDict, color: ColorLike="red"):
        for face_hash in faces:
            self.debug_faces[face_hash] = color

    @classmethod
    def _cast_edges(cls, edges: EdgeListLike) -> Iterable[_.Edge]:
        if isinstance(edges, EdgeDict):
            return edges()
        if isinstance(edges, _.Edge):
            return [edges]
        return edges

    @classmethod
    def _cast_part(cls, part: Builder|_.Part) -> _.Part:
        return part if isinstance(part, _.Part) else part.object

    @classmethod
    def cast_color(cls, color: ColorLike) -> _.Color:
        return color if isinstance(color, _.Color) else _.Color(color)

    @classmethod
    def _part_color(cls, part: Builder|_.Part) -> ColorLike|None:
        if isinstance(part, Builder) and len(part.operations) == 1:
            return part.operations[-1].color
        return None

    def mutate(
            self,
            name: str,
            obj: _.Part,
            color: ColorLike|None,
            debug: bool,
            faces_alias: dict[Hash, Hash]|None=None
        ) -> Operation:
        self.object = obj

        opr = Operation(
            obj,
            self.operations[-1] if self.operations else None,
            name,
            len(self.operations),
            color,
            faces_alias
        )

        if debug:
            for face_hash in opr.faces_added:
                self.debug_faces[face_hash] = color

        self.operations.append(opr)
        return opr

    def move(self, location: _.Location, color: ColorLike|None=None, debug=False) -> Operation:
        obj = location * self.object
        faces_alias: dict[Hash, Hash] = {}

        for face in self.object.faces():
            old_hash = Operation.hash_shape(face)
            new_hash = Operation.hash_shape(location * face)
            faces_alias[new_hash] = old_hash

        return self.mutate('move', obj, color, debug, faces_alias)

    def add(
            self,
            part: Builder|_.Part,
            color: ColorLike|None=None,
            debug=False
        ) -> Operation:
        obj = self.object + self._cast_part(part)
        return self.mutate('add', obj, color or self._part_color(part), debug)

    def sub(
            self,
            part: Builder|_.Part,
            color: ColorLike|None=None,
            debug=False
        ) -> Operation:
        obj = self.object - self._cast_part(part)
        return self.mutate('sub', obj, color or self._part_color(part), debug)

    def fillet(
            self,
            edge_list: EdgeListLike,
            radius: float,
            color: ColorLike|None=None,
            debug=False
        ) -> Operation:
        obj = self.object.fillet(radius, self._cast_edges(edge_list))
        return self.mutate('fillet', obj, color, debug)

    def chamfer(
            self,
            edge_list: EdgeListLike,
            length: float,
            length2: float|None=None,
            face: _.Face|None=None,
            color: ColorLike|None=None,
            debug=False
        ) -> Operation:
        edges = self._cast_edges(edge_list)
        obj = self.object.chamfer(length, length2, edges, face) # type: ignore
        return self.mutate('chamfer', obj, color, debug)

    def export(
            self,
            exporter: _.Export2D,
            file_path: PathLike|bytes|str,
            include_part=True
        ):
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
        _.export_stl(self.object, file_path, tolerance, angular_tolerance, ascii_format)
