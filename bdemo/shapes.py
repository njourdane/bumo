from enum import Enum
from typing import TypeAlias, Iterable

import build123d as _

from .utils import Hash


class ShapeState(Enum):
    ADDED = 1
    ALTERED = 2
    UNTOUCHED = 3
    REMOVED = 4


class EdgeDict(dict):
    def __init__(self, edges_dict: dict[Hash, _.Edge]):
        super().__init__(edges_dict)

    def __setitem__(self, edge_hash: Hash, edge: _.Edge) -> None:
        super().__setitem__(edge_hash, edge)

    def __getitem__(self, edge_hash: Hash) -> _.Edge:
        return super().__getitem__(edge_hash)

    def __call__(self) -> list[_.Edge]:
        return list(self.values())


class FaceDict(dict):
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
