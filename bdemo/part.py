from __future__ import annotations
from typing import Iterable

import build123d as _

from .operation import Operation


class Part:
    def __init__(self, obj: _.Part, name: str=''):
        self.object = obj
        self.operations = [Operation(obj, name, None)]

    def __call__(self) -> _.Part:
        return self.object

    def __and__(self, part: Part) -> Part:
        return Part(self.object + part.object)

    def mutate(self, name: str, obj: _.Part) -> Operation:
        self.object = obj
        operation = Operation(obj, name, self.operations[-1])
        self.operations.append(operation)
        return operation

    def add(self, part: Part) -> Operation:
        return self.mutate('add', self.object + part.object)

    def sub(self, part: Part) -> Operation:
        return self.mutate('sub', self.object - part.object)

    def fillet(self, radius: float, edge_list: Iterable[_.Edge]) -> Operation:
        return self.mutate('fillet', self.object.fillet(radius, edge_list))

    def chamfer(self, length: float, length2: float|None, edge_list: Iterable[_.Edge], face: _.Face|None=None) -> Operation:
        return self.mutate('chamfer', self.object.chamfer(length, length2, edge_list, face))
