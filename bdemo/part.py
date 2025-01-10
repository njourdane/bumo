from __future__ import annotations
from os import PathLike
from typing import Iterable

import build123d as _

from .operation import Operation
from .utils import ColorLike, to_color


class Part:
    def __init__(self, part: _.Part, color: ColorLike|None=None):
        self.object = part
        self.operations: list[Operation] = []
        self.mutate(self.__class__.__name__, part, color)
        self.debug_faces: dict[str, ColorLike] = {}

    def __call__(self) -> list[_.Face]:
        faces = self.operations[-1].faces
        faces_color = self.get_faces_color()

        for face_id, face in faces.items():
            face.color = faces_color[face_id]
            face.label = face_id

        return list(faces.values())

    def __and__(self, part: Part) -> Part:
        return Part(self.object & part.object)

    def get_faces_color(self) -> dict[str, ColorLike|None]:
        faces_color: dict[str, ColorLike|None] = {}

        for opr in self.operations:

            for face_id in opr.faces_added:
                faces_color[face_id] = opr.color

            rem_colors = {faces_color[rm_id] for rm_id in opr.faces_removed}
            if len(rem_colors) > 1:
                for rm_id, rm_face in opr.faces_removed.items():
                    assert opr.last_operation
                    if not opr.last_operation.is_altered_face(rm_face):
                        rem_colors.remove(faces_color[rm_id])

            color = rem_colors.pop() if len(rem_colors) == 1 else None
            for face_id in opr.faces_altered:
                faces_color[face_id] = color

        if self.debug_faces:
            for face_id, color in faces_color.items():
                if face_id in self.debug_faces:
                    faces_color[face_id] = self.debug_faces[face_id]
                else:
                    r, v, b = to_color(color).to_tuple()[:3]
                    faces_color[face_id] = _.Color(r, v, b, 0.1)

        return faces_color

    def get_operation(self, op_id: str) -> Operation|None:
        for operation in self.operations:
            if operation.id == op_id:
                return operation
        return None

    def debug(self, faces: list[str], color: ColorLike="red"):
        for face_id in faces:
            self.debug_faces[face_id] = color

    def mutate(self, name: str, obj: _.Part, color: ColorLike|None=None) -> Operation:
        self.object = obj
        last_operation = self.operations[-1] if self.operations else None
        opr = Operation(obj, last_operation, name, len(self.operations), color)

        self.operations.append(opr)
        return opr

    @classmethod
    def cast_part(cls, part: Part|_.Part) -> _.Part:
        return part if isinstance(part, _.Part) else part.object

    @classmethod
    def part_color(cls, part: Part|_.Part) -> ColorLike|None:
        if isinstance(part, Part) and len(part.operations) == 1:
            return part.operations[-1].color
        return None

    def add(self, part: Part|_.Part, color: str|None=None) -> Operation:
        obj = self.object + self.cast_part(part)
        return self.mutate('add', obj, color or self.part_color(part))

    def sub(self, part: Part|_.Part, color: str|None=None) -> Operation:
        obj = self.object - self.cast_part(part)
        return self.mutate('sub', obj, color or self.part_color(part))

    def fillet(self, edge_list: Iterable[_.Edge], radius: float, color: str|None=None) -> Operation:
        obj = self.object.fillet(radius, edge_list)
        return self.mutate('fillet', obj, color)

    def chamfer(self, edge_list: Iterable[_.Edge], length: float, length2: float|None=None, face: _.Face|None=None, color: str|None=None) -> Operation:
        obj = self.object.chamfer(length, length2, edge_list, face)
        return self.mutate('chamfer', obj, color)

    def export(self, exporter: _.Export2D, file_path: PathLike|bytes|str, include_part=True):
        if include_part:
            exporter.add_shape(self.object)
        exporter.write(file_path)

    def export_stl(self, file_path: PathLike|bytes|str, tolerance: float = 0.001, angular_tolerance: float = 0.1, ascii_format: bool = False):
        _.export_stl(self.object, file_path, tolerance, angular_tolerance, ascii_format)
