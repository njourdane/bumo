from typing import TypeAlias
from enum import Enum

import build123d as _


class ShapeState(Enum):
    added = 1
    altered = 2
    untouched = 3
    removed = 4


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

def to_color(color: ColorLike) -> _.Color:
    return color if isinstance(color, _.Color) else _.Color(color)
