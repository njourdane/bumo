"""A module used for color-related stuff."""
from enum import Enum
from typing import TypeAlias
import struct

import build123d as _
from .color_palettes import viridis, inferno, magma, plasma


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


ColorTuple: TypeAlias = tuple[float, float, float]


class ColorPalette(Enum):
    "The name of predefined color palettes."
    VIRIDIS = 0
    INFERNO = 1
    MAGMA = 2
    PLASMA = 3

    def get_palette(self):
        """Return the color palette related to the enum value."""
        palettes = [viridis, inferno, magma, plasma]
        return palettes[self.value]


def build_palette(
        palette: ColorPalette,
        amount: int,
        as_str=False
    ) -> list[ColorTuple|str]:
    """Build a list of colors based on the given palette and the amount of
    colors."""

    def to_hex(color: int) -> str:
        return hex(color)[2:].rjust(6, '0')

    def to_tuple(color: int) -> ColorTuple:
        tuple_int = struct.unpack('BBB', bytes.fromhex(to_hex(color)))
        return tuple(c/256 for c in tuple_int)

    def get_color(index):
        func_convert = to_hex if as_str else to_tuple
        return func_convert(palette.get_palette()[index])

    indexes = (
        [127] if amount == 1
        else [int(idx / (amount - 1) * 255) for idx in range(amount)]
    )

    return [get_color(index) for index in indexes]
