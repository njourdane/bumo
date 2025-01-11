from typing import TypeAlias, Iterable
from enum import Enum

import build123d as _

Hash: TypeAlias = str

ColorLike: TypeAlias = (
    _.Color | # build123d color
    _.Quantity_ColorRGBA | # OCP color
    str | # name, ex: "red"
    tuple[str, int] | # name + alpha, ex: ("red", 0.5)
    tuple[float, float, float] | # rvb, ex: (1, 0, 0)
    tuple[float, float, float, int] | # rvb + alpha, ex: (1, 0, 0, 0.5)
    int | # hexa, ex: 0xff0000
    tuple[int, int] # hexa + alpha, ex: (0xff0000, 0x80)
)


class ShapeState(Enum):
    added = 1
    altered = 2
    untouched = 3
    removed = 4


def to_color(color: ColorLike) -> _.Color:
    return color if isinstance(color, _.Color) else _.Color(color)


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


FaceListLike = FaceDict | Iterable[_.Face] | _.Face
EdgeListLike = EdgeDict | Iterable[_.Edge] | _.Edge
