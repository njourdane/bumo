"""A module used for color-related stuff."""

from enum import Enum
from typing import TypeAlias

import build123d as _


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
