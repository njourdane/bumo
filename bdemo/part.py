from __future__ import annotations
from os import PathLike
from typing import Iterable

import build123d as _

from .operation import Operation
from .utils import ColorLike, to_color, FaceList


class Part:
    debug_alpha = 0.2

    def __init__(self, part: _.Part, color: ColorLike|None=None, debug=False):
        self.object = part
        self.operations: list[Operation] = []
        self.debug_faces: dict[int, ColorLike] = {}
        self.mutate(self.__class__.__name__, part, color, debug)

    def __call__(self) -> list[_.Face]:
        faces = self.operations[-1].faces
        faces_color = self.get_faces_color()

        for face_hash, face in faces.items():
            face.color = faces_color[face_hash]
            face.label = hex(face_hash)[2:]

        return list(faces.values())

    def __mul__(self, location: _.Location) -> Part:
        return Part(location * self.object)

    def get_faces_color(self) -> dict[int, ColorLike|None]:
        faces_color: dict[int, ColorLike|None] = {}

        for opr in self.operations:

            for face_hash in opr.faces_added:
                faces_color[face_hash] = opr.color

            rem_colors = {faces_color[rm_hash] for rm_hash in opr.faces_removed}
            if len(rem_colors) > 1:
                for rm_hash, rm_face in opr.faces_removed.items():
                    assert opr.last_operation
                    if not opr.last_operation.is_altered_face(rm_face):
                        rem_colors.remove(faces_color[rm_hash])

            previous_color = rem_colors.pop() if len(rem_colors) == 1 else None
            for face_hash in opr.faces_altered:
                faces_color[face_hash] = previous_color

        if self.debug_faces:
            for face_hash, color in faces_color.items():
                if face_hash in self.debug_faces:
                    faces_color[face_hash] = self.debug_faces[face_hash]
                else:
                    r, v, b = to_color(color).to_tuple()[:3]
                    faces_color[face_hash] = _.Color(r, v, b, self.debug_alpha)

        return faces_color

    def get_operation(self, op_id: str) -> Operation|None:
        for operation in self.operations:
            if operation.id == op_id:
                return operation
        return None

    def debug(self, face_hashes: dict[int, _.Face], color: ColorLike="red"):
        for face_hash in face_hashes:
            self.debug_faces[face_hash] = color

    def mutate(self, name: str, obj: _.Part, color: ColorLike|None, debug: bool) -> Operation:
        self.object = obj
        last_operation = self.operations[-1] if self.operations else None
        opr = Operation(obj, last_operation, name, len(self.operations), color)

        if debug:
            for face_hash in opr.faces_added:
                self.debug_faces[face_hash] = color

        self.operations.append(opr)
        return opr

    @classmethod
    def cast_edges(cls, edges: FaceList) -> Iterable[_.Edge]:
        return edges.values() if isinstance(edges, dict) else edges

    @classmethod
    def cast_part(cls, part: Part|_.Part) -> _.Part:
        return part if isinstance(part, _.Part) else part.object

    @classmethod
    def part_color(cls, part: Part|_.Part) -> ColorLike|None:
        if isinstance(part, Part) and len(part.operations) == 1:
            return part.operations[-1].color
        return None

    def move(self, location: _.Location, color: ColorLike|None=None, debug=False) -> Operation:
        obj = location * self.object
        return self.mutate('add', obj, color, debug)

    def add(self, part: Part|_.Part, color: ColorLike|None=None, debug=False) -> Operation:
        obj = self.object + self.cast_part(part)
        return self.mutate('add', obj, color or self.part_color(part), debug)

    def sub(self, part: Part|_.Part, color: ColorLike|None=None, debug=False) -> Operation:
        obj = self.object - self.cast_part(part)
        return self.mutate('sub', obj, color or self.part_color(part), debug)

    def fillet(self, edge_list: FaceList, radius: float, color: ColorLike|None=None, debug=False) -> Operation:
        obj = self.object.fillet(radius, self.cast_edges(edge_list))
        return self.mutate('fillet', obj, color, debug)

    def chamfer(self, edge_list: FaceList, length: float, length2: float|None=None, face: _.Face|None=None, color: ColorLike|None=None, debug=False) -> Operation:
        obj = self.object.chamfer(length, length2, self.cast_edges(edge_list), face)
        return self.mutate('chamfer', obj, color, debug)

    def export(self, exporter: _.Export2D, file_path: PathLike|bytes|str, include_part=True):
        if include_part:
            exporter.add_shape(self.object)
        exporter.write(file_path)

    def export_stl(self, file_path: PathLike|bytes|str, tolerance: float = 0.001, angular_tolerance: float = 0.1, ascii_format: bool = False):
        _.export_stl(self.object, file_path, tolerance, angular_tolerance, ascii_format)
