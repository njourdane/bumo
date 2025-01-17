"""Bumo configuration variables."""

from build123d import Color
from .colors import ColorPalette


COLOR_PALETTE = ColorPalette.VIRIDIS
"The color palette to use when auto_color is enabled."

DEBUG_ALPHA = 0.2
"The alpha value used for translucent shapes in debug mode."

DEFAULT_COLOR = Color("orange")
"The default color to be used when a color is passed to a mutation."

DEFAULT_DEBUG_COLOR = Color("red")
"The default color to be used when using the debug mode."

INFO_COLOR = True
"Set to False to disable terminal colors in the info table."

INFO_TABLE_FORMAT = "fancy_outline"
"""The table format used in the info table. See
https://github.com/astanin/python-tabulate?tab=readme-ov-file#table-format
"""

INFO_COLUMNS = ["idx", "label", "type", "f+", "f~", "f-", "e+", "e~", "e-"]
""""The columns to display in info tables."""
