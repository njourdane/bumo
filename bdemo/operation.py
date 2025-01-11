from __future__ import annotations
from hashlib import md5

import build123d as _

from .utils import ColorLike, Hash
from .shapes import ShapeState, FaceDict, EdgeDict


class Operation:
    def __init__(
        self,
        obj: _.Part,
        previous: Operation|None,
        name: str,
        index: int,
        color: ColorLike|None,
        faces_alias: dict[Hash, Hash]|None
    ) -> None:
        self.previous = previous
        self.name = name
        self.index = index
        self.color = color
        self.faces_alias = faces_alias or {}

        self.id = f"{ name }-{ index }"

        self.faces = FaceDict({self.hash_shape(f): f for f in obj.faces()})
        self.faces_state = self.get_faces_state()
        self.faces_added = self.filter_faces(ShapeState.added)
        self.faces_altered = self.filter_faces(ShapeState.altered)
        self.faces_untouched = self.filter_faces(ShapeState.untouched)
        self.faces_removed = self.filter_faces(ShapeState.removed)

        self.edges = EdgeDict({self.hash_shape(e): e for e in obj.edges()})
        self.edges_state = self.get_edges_state()
        self.edges_added = self.filter_edges(ShapeState.added)
        self.edges_altered = self.filter_edges(ShapeState.altered)
        self.edges_untouched = self.filter_edges(ShapeState.untouched)
        self.edges_removed = self.filter_edges(ShapeState.removed)

        self.vertices = {self.hash_shape(v): v for v in obj.vertices()}

    def __repr__(self):
        return self.id

    @classmethod
    def hash_shape(cls, shape: _.Shape) -> Hash:
        """
        Return a reproducible hash.
        OCP 7.2 might produce better hashes that could make this unnecessary.
        """

        def to_int(number: float) -> int:
            return int(number * 1000)

        def serialize_vertex(vertex: _.Vertex) -> tuple:
            return tuple(to_int(v) for v in vertex.to_tuple())

        def serialize_edge(edge: _.Edge) -> tuple:
            return (
                edge.geom_type,
                tuple(serialize_vertex(vertex) for vertex in edge.vertices()),
                to_int(edge.radius) if edge.geom_type == _.GeomType.CIRCLE else 0
            )

        def serialize_face(face: _.Face) -> tuple:
            return tuple(serialize_edge(edge) for edge in face.edges())

        def serialize_part(part: _.Part) -> tuple:
            return tuple(serialize_face(face) for face in part.faces())

        if isinstance(shape, _.Vertex):
            serialized = serialize_vertex(shape)
        elif isinstance(shape, _.Edge):
            serialized = serialize_edge(shape)
        elif isinstance(shape, _.Face):
            serialized = serialize_face(shape)
        elif isinstance(shape, _.Part):
            serialized = serialize_part(shape)
        else:
            raise TypeError

        return md5(str(serialized).encode()).hexdigest()

    def filter_faces(self, state: ShapeState) -> FaceDict:
        faces = (
            self.previous.faces
            if self.previous and state == ShapeState.removed
            else self.faces
        )
        faces = {h: faces[h] for h, s in self.faces_state.items() if s == state}
        return FaceDict(faces)

    def filter_edges(self, state: ShapeState) -> EdgeDict:
        edges = (
            self.previous.edges
            if self.previous and state == ShapeState.removed
            else self.edges
        )
        edges = {h: edges[h] for h, e in self.edges_state.items() if e == state}
        return EdgeDict(edges)

    @classmethod
    def is_altered_faces(cls, this_face: _.Face, that_face: _.Face):
        for this_edge in this_face.edges():
            this_hash = cls.hash_shape(this_edge)
            for that_edge in that_face.edges():
                if this_hash == cls.hash_shape(that_edge):
                    return True

        return False

    def is_altered_face(self, face: _.Face):
        if not self.previous:
            return True

        for edge in face.edges():
            if self.hash_shape(edge) in self.previous.edges:
                return True

        return False

    def get_faces_state(self) -> dict[Hash, ShapeState]:
        def get_state(face_hash: Hash, face: _.Face) -> ShapeState:
            if not self.previous:
                return ShapeState.added

            if face_hash in self.previous.faces:
                return ShapeState.untouched

            if self.is_altered_face(face):
                return ShapeState.altered

            return ShapeState.added

        faces = {fh: get_state(fh, face) for fh, face in self.faces.items()}

        if self.previous:
            for face_hash in self.previous.faces:
                if face_hash not in self.faces:
                    faces[face_hash] = ShapeState.removed

        return faces

    def is_altered_edge(self, edge: _.Edge):
        if not self.previous:
            return True

        for vertex in edge.vertices():
            if self.hash_shape(vertex) in self.previous.vertices:
                return True

        return False

    def get_edges_state(self) -> dict[Hash, ShapeState]:
        def get_state(edge_hash: Hash, edge: _.Edge) -> ShapeState:
            if not self.previous:
                return ShapeState.added

            if edge_hash in self.previous.edges:
                return ShapeState.untouched

            if self.is_altered_edge(edge):
                return ShapeState.altered

            return ShapeState.added

        edges = {eh: get_state(eh, edge) for eh, edge in self.edges.items()}

        if self.previous:
            for edge_hash in self.previous.edges:
                if edge_hash not in self.edges:
                    edges[edge_hash] = ShapeState.removed

        return edges
