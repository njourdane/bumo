from __future__ import annotations
from typing import Iterable

import build123d as _

from .operation import Operation


class Part:
    def __init__(self, part: _.Part, color: str|None=None):
        self.object = part
        self.operations: list[Operation] = []
        self.mutate(self.__class__.__name__, part, color)

    def __call__(self) -> list[_.Face]:
        faces = self.operations[-1].faces
        faces_color = self.get_faces_color()

        for face_id, face in faces.items():
            face.color = faces_color[face_id]

        return list(faces.values())

    def __and__(self, part: Part) -> Part:
        return Part(self.object & part.object)

    def get_faces_color(self) -> dict[str, str|None]:
        faces_color: dict[str, str|None] = {}

        for opr in self.operations:

            for face_id in opr.faces_added:
                faces_color[face_id] = opr.color

            removed = list({faces_color[rm_id] for rm_id in opr.faces_removed})
            for face_id in opr.faces_altered:
                if len(removed) == 1:
                    faces_color[face_id] = removed[0]
                else:
                    faces_color[face_id] = "grey"

        return faces_color

    def get_operation(self, op_id: str) -> Operation|None:
        for operation in self.operations:
            if operation.id == op_id:
                return operation
        return None

    def mutate(self, name: str, obj: _.Part, color: str|None=None) -> Operation:
        self.object = obj
        last_operation = self.operations[-1] if self.operations else None
        opr = Operation(obj, last_operation, name, len(self.operations), color)

        self.operations.append(opr)
        return opr

    @classmethod
    def cast_part(cls, part: Part|_.Part) -> _.Part:
        return part if isinstance(part, _.Part) else part.object

    @classmethod
    def part_color(cls, part: Part|_.Part) -> str|None:
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
