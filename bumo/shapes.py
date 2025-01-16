"""A module used to store shapes-related stuff"""
from enum import Enum
from typing import TypeAlias, Iterable
from hashlib import md5

import build123d as _


Hash: TypeAlias = str


class ShapeState(Enum):
    """The possible states of a shape for a mutation."""

    ADDED = 1
    ALTERED = 2
    UNTOUCHED = 3
    REMOVED = 4

def hash_shape(shape: _.Shape) -> Hash:
    """Return a reproducible hash.
    OCP 7.2 might produce better hashes that could make this unnecessary."""

    def to_int(number: float) -> int:
        return int(number * 1000)

    def serialize_vertex(vertex: _.Vertex) -> tuple:
        return tuple(to_int(v) for v in vertex.to_tuple())

    def serialize_edge(edge: _.Edge) -> tuple:
        vertices = tuple(serialize_vertex(v) for v in edge.vertices())
        is_circle = edge.geom_type == _.GeomType.CIRCLE
        radius = to_int(edge.radius) if is_circle else 0
        return (edge.geom_type, vertices, radius)

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

class EdgeDict(dict):
    """A custom dictionnary used to store edges by their hash.
    If the dict is called ie. `my_edges()`, a list is returned."""

    def __init__(self, edges_dict: dict[Hash, _.Edge]):
        super().__init__(edges_dict)

    def __setitem__(self, edge_hash: Hash, edge: _.Edge) -> None:
        super().__setitem__(edge_hash, edge)

    def __getitem__(self, edge_hash: Hash) -> _.Edge:
        return super().__getitem__(edge_hash)

    def __call__(self) -> list[_.Edge]:
        return list(self.values())


class FaceDict(dict):
    """A custom dictionnary used to store faces by their hash.
    If the dict is called ie. `my_edges()`, a list is returned."""

    def __init__(self, faces_dict: dict[Hash, _.Face]):
        super().__init__(faces_dict)

    def __setitem__(self, face_hash: Hash, face: _.Face) -> None:
        super().__setitem__(face_hash, face)

    def __getitem__(self, face_hash: Hash) -> _.Face:
        return super().__getitem__(face_hash)

    def __call__(self) -> list[_.Face]:
        return list(self.values())


FaceListLike: TypeAlias = FaceDict | Iterable[_.Face] | _.Face
EdgeListLike: TypeAlias = EdgeDict | Iterable[_.Edge] | _.Edge
