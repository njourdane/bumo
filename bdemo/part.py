from __future__ import annotations
from typing import Iterable

import build123d as _

from .operation import Operation


class Part:
    def __init__(self, obj: _.Part, color: str|None=None):
        self.object = obj
        self.operations = [Operation(obj, obj.__class__.__name__, None, color)]

    def __call__(self) -> _.Part:
        return self.object

    def __and__(self, part: Part) -> Part:
        return Part(self.object + part.object)

    def mutate(self, name: str, obj: _.Part, color: str|None=None) -> Operation:
        self.object = obj
        operation = Operation(obj, name, self.operations[-1], color)
        self.operations.append(operation)
        return operation

    @classmethod
    def cast_part(cls, part: Part|_.Part) -> _.Part:
        return part if isinstance(part, _.Part) else part.object

    def add(self, part: Part|_.Part, color: str|None=None) -> Operation:
        obj = self.object + self.cast_part(part)
        return self.mutate('add', obj, color)

    def sub(self, part: Part|_.Part, color: str|None=None) -> Operation:
        obj = self.object - self.cast_part(part)
        return self.mutate('sub', obj, color)

    def fillet(self, radius: float, edge_list: Iterable[_.Edge], color: str|None=None) -> Operation:
        obj = self.object.fillet(radius, edge_list)
        return self.mutate('fillet', obj, color)

    def chamfer(self, length: float, length2: float|None, edge_list: Iterable[_.Edge], face: _.Face|None=None, color: str|None=None) -> Operation:
        obj = self.object.chamfer(length, length2, edge_list, face)
        return self.mutate('chamfer', obj, color)
