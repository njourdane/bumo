from enum import Enum

import build123d as _

from . import config


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


AUTO = Mode(ModeType.AUTO, config.DEFAULT_COLOR)
