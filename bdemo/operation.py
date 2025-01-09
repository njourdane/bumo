from __future__ import annotations

import build123d as _

operations = {}


class Operation:
    def __init__(self, obj: _.Part, name: str, last: Operation|None, color: str|None=None) -> None:
        self.name = name
        self.last = last
        self.color = color

        operations[name] = operations[name] + 1 if name in operations else 1
        self.id = f"{ name }-{ operations[name] }"

        self.faces = {self.get_id(f): f for f in obj.faces()}
        self.new_faces = {id: f for id, f in self.faces.items() if self.is_new_face(f)}
        self.very_new_faces = {id: f for id, f in self.faces.items() if self.is_very_new_face(f)}

        self.edges = {self.get_id(e): e for e in obj.edges()}
        self.new_edges = {id: e for id, e in self.edges.items() if self.is_new_edge(e)}
        self.very_new_edges = {id: e for id, e in self.edges.items() if self.is_very_new_edge(e)}

        self.vertices = {self.get_id(v): v for v in obj.vertices()}

        self.shapes = {**self.faces, **self.edges}

    def __repr__(self):
        return self.id

    def get_id(self, shape: _.Shape) -> str:
        return hex(hash(shape))[2:]

    def get_shapes_obj(self) -> list[_.Shape]:
        return list(self.shapes.values())

    def get_shapes_name(self) -> list[str]:
        return list(self.shapes.keys())

    def is_new_face(self, face: _.Face) -> bool:
        return self.last is None or self.get_id(face) not in self.last.faces

    def is_very_new_face(self, face: _.Face) -> bool:
        for edge in face.edges():
            if self.last and self.get_id(edge) in self.last.edges:
                return False
        return True

    def is_new_edge(self, edge: _.Edge) -> bool:
        return self.last is None or self.get_id(edge) not in self.last.edges

    def is_very_new_edge(self, edge: _.Edge) -> bool:
        for vertex in edge.vertices():
            if self.last and self.get_id(vertex) in self.last.vertices:
                return False
        return True
