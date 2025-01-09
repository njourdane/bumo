from __future__ import annotations

import build123d as _


class Operation:
    def __init__(self, obj: _.Part, name: str, last: Operation|None) -> None:
        self.name = name
        self.last = last

        self.faces = {self.get_id(f): f for f in obj.faces()}
        self.edges = {self.get_id(e): e for e in obj.edges()}
        self.vertices = {self.get_id(v): v for v in obj.vertices()}
        self.shapes = {**self.faces, **self.edges}

    def __repr__(self):
        return self.name

    def get_id(self, shape: _.Shape) -> str:
        return hex(hash(shape))[2:]
