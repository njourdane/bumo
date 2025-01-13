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


def cast_color(color: ColorLike) -> _.Color:
    """Cast a ColorLike to a Build123d Color"""
    return color if isinstance(color, _.Color) else _.Color(color)


def color_to_str(color: _.Color) -> str:
    """Return a string representation of the given color."""
    def float_to_hex(n: float):
        return hex(int(n * 255))[2:].rjust(2, '0')

    r, g, b, a = [float_to_hex(c) for c in color.to_tuple()]
    word = str(color).split("~")[1].strip().lower()
    return f"#{ r }{ g }{ b }{ a } (~{ word })"



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

    def build_palette(self, amount: int) -> list[_.Color]:
        """Build a list of colors based on the given palette and the amount of
        colors."""

        def get_color(index: int) -> _.Color:
            color_int = self.get_palette()[index]
            color_hex = hex(color_int)[2:].rjust(6, '0')
            color_tuple = struct.unpack('BBB', bytes.fromhex(color_hex))
            return _.Color(tuple(c/256 for c in color_tuple))

        if amount == 1:
            return [get_color(127)]

        indexes = [int(idx / (amount - 1) * 255) for idx in range(amount)]
        return [get_color(index) for index in indexes]
