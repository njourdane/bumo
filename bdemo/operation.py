from __future__ import annotations
from enum import Enum

import build123d as _


class ShapeState(Enum):
    added = 1
    altered = 2
    untouched = 3
    removed = 4


class Operation:
    def __init__(self, obj: _.Part, last_operation: Operation|None, name: str, index: int, color: str|None=None) -> None:
        self.last_operation = last_operation
        self.name = name
        self.index = index
        self.color = color

        self.id = f"{ name }-{ index }"
        self.faces = {self.get_id(f): f for f in obj.faces()}
        self.faces_state = self.get_faces_state()
        self.faces_added = self.filter_faces(ShapeState.added)
        self.faces_altered = self.filter_faces(ShapeState.altered)
        self.faces_untouched = self.filter_faces(ShapeState.untouched)
        self.faces_removed = self.filter_faces(ShapeState.removed)

        self.edges = {self.get_id(e): e for e in obj.edges()}
        self.edges_state = self.get_edges_state()
        self.edges_added = self.filter_edges(ShapeState.added)
        self.edges_altered = self.filter_edges(ShapeState.altered)
        self.edges_untouched = self.filter_edges(ShapeState.untouched)
        self.edges_removed = self.filter_edges(ShapeState.removed)

        self.vertices = {self.get_id(v): v for v in obj.vertices()}

        self.shapes = {**self.faces, **self.edges}

    def __repr__(self):
        return self.id

    def filter_faces(self, state: ShapeState) -> dict[str, _.Face]:
        faces = self.last_operation.faces if self.last_operation and state == ShapeState.removed else self.faces
        return {id: faces[id] for id, fs in self.faces_state.items() if fs == state}

    def filter_edges(self, state: ShapeState) -> dict[str, _.Edge]:
        edges = self.last_operation.edges if self.last_operation and state == ShapeState.removed else self.edges
        return {id: edges[id] for id, es in self.edges_state.items() if es == state}

    @classmethod
    def get_id(cls, shape: _.Shape) -> str:
        return hex(hash(shape))[2:]

    def get_shapes_obj(self) -> list[_.Shape]:
        return list(self.shapes.values())

    def get_shapes_name(self) -> list[str]:
        return list(self.shapes.keys())

    def is_altered_face(self, face: _.Face):
        if not self.last_operation:
            return True

        for edge in face.edges():
            if self.get_id(edge) in self.last_operation.edges:
                return True

        return False

    def get_faces_state(self) -> dict[str, ShapeState]:
        def get_state(face_id: str, face: _.Face) -> ShapeState:
            if not self.last_operation:
                return ShapeState.added

            if face_id in self.last_operation.faces:
                return ShapeState.untouched

            if self.is_altered_face(face):
                return ShapeState.altered

            return ShapeState.added

        faces = {id: get_state(id, face) for id, face in self.faces.items()}

        if self.last_operation:
            for face_id in self.last_operation.faces:
                if face_id not in self.faces:
                    faces[face_id] = ShapeState.removed

        return faces

    def is_altered_edge(self, edge: _.Edge):
        if not self.last_operation:
            return True

        for vertex in edge.vertices():
            if self.get_id(vertex) in self.last_operation.vertices:
                return True

        return False

    def get_edges_state(self) -> dict[str, ShapeState]:
        def get_state(edge_id: str, edge: _.Edge) -> ShapeState:
            if not self.last_operation:
                return ShapeState.added

            if edge_id in self.last_operation.edges:
                return ShapeState.untouched

            if self.is_altered_edge(edge):
                return ShapeState.altered

            return ShapeState.added

        edges = {id: get_state(id, edge) for id, edge in self.edges.items()}

        if self.last_operation:
            for edge_id in self.last_operation.edges:
                if edge_id not in self.edges:
                    edges[edge_id] = ShapeState.removed

        return edges
