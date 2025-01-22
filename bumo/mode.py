from enum import Enum

import build123d as _

from . import config
from .colors import ColorLike, cast_color


class ModeType(Enum):
    FIXED = 1
    AUTO = 2
    DEBUG = 3
    DEFAULT = 4


class Mode:
    def __init__(self, mode_type: ModeType, color: _.Color) -> None:
        self.mode_type = mode_type
        self.color = color

    def get_color(self, auto_color: _.Color):
        if self.mode_type == ModeType.AUTO:
            return auto_color

        if self.mode_type == ModeType.DEFAULT:
            return config.DEFAULT_COLOR

        return self.color


def cast_mode(mode: Mode | ColorLike) -> Mode:
    if isinstance(mode, Mode):
        return mode
    return Mode(ModeType.FIXED, cast_color(mode))


AUTO = Mode(ModeType.AUTO, config.DEFAULT_COLOR)
DEBUG = Mode(ModeType.DEBUG, config.DEFAULT_DEBUG_COLOR)
