from dataclasses import dataclass

from build123d import Color
from .colors import ColorPalette, ColorLike, cast_color


@dataclass
class Config:
    """A data class used to store configuration values."""

    color_palette = ColorPalette.VIRIDIS
    "The color palette to use when auto_color is enabled."

    debug_alpha = 0.2
    "The alpha value used for translucent shapes in debug mode."

    _default_color = Color("orange")

    @property
    def default_color(self) -> Color:
        "The default color to be used when a color is passed to a mutation."
        return self._default_debug_color

    @default_color.setter
    def default_color(self, value: ColorLike):
        self._default_color = cast_color(value)

    _default_debug_color = Color("red")

    @property
    def default_debug_color(self) -> Color:
        "The default color to be used when using the debug mode."
        return self._default_debug_color

    @default_debug_color.setter
    def default_debug_color(self, value: ColorLike):
        self._default_debug_color = cast_color(value)

    info_colors = True
    "Set to False to disable terminal colors in the info table."

    info_table_format = "fancy_outline"
    """The table format used in the info table. See
    https://github.com/astanin/python-tabulate?tab=readme-ov-file#table-format
    """

    info_columns = ["idx", "label", "type", "f+", "f~", "f-", "e+", "e~", "e-"]
    """"The columns to display in info tables."""
