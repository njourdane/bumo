from __future__ import annotations
import build123d as _


class Part:
    def __init__(self, obj: _.Part):
        self.obj = obj
        self.name = 'Part'

    def __call__(self) -> _.Part:
        return self.obj

    def add(self, part: Part) -> Part:
        self.obj += part.obj
        self.name = f"{self.name} + {part.name}"
        return self

    def __add__(self, part: Part) -> Part:
        return Part(self.obj + part.obj)

    def sub(self, part: Part) -> Part:
        self.obj -= part.obj
        self.name = f"{self.name} - {part.name}"
        return self

    def __sub__(self, part: Part) -> Part:
        return Part(self.obj - part.obj)

    # def chamfer(self, part: Self) -> Self:
    #     self.obj -= part.obj
    #     return self

    def Box(self):
        pass

    def __str__(self) -> str:
        return self.name


class Box(Part):
    def __init__(self, length: float, width: float, height: float) -> None:
        super().__init__(_.Box(length, width, height))
        self.name = f"Part({length}, {width}, {height})"


class Cylinder(Part):
    def __init__(self, radius: float, height: float, arc_size: float=360) -> None:
        super().__init__(_.Cylinder(radius, height, arc_size))
        self.name = f"Cylinder({radius}, {height})"
