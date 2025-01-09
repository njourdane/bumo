import build123d as _

from .part import Part


class Box(Part):
    def __init__(self, length: float, width: float, height: float, color: str|None=None) -> None:
        part = _.Box(length, width, height)
        super().__init__(part, color)


class Cone(Part):
    def __init__(self, bottom_radius: float, top_radius: float, height: float, arc_size: float, color: str|None=None) -> None:
        part = _.Cone(bottom_radius, top_radius, height, arc_size)
        super().__init__(part, color)


class CounterBoreHole(Part):
    def __init__(self, radius: float, counter_bore_radius: float, counter_bore_depth: float, depth: float|None = None, color: str|None=None):
        part = _.CounterBoreHole(radius, counter_bore_radius, counter_bore_depth, depth)
        super().__init__(part, color)


class CounterSinkHole(Part):
    def __init__(self, radius: float, counter_sink_radius: float, depth: float|None = None, counter_sink_angle: float = 82, color: str|None=None):
        part = _.CounterSinkHole(radius, counter_sink_radius, depth, counter_sink_angle)
        super().__init__(part, color)


class Cylinder(Part):
    def __init__(self, radius: float, height: float, arc_size: float=360, color: str|None=None) -> None:
        part = _.Cylinder(radius, height, arc_size)
        super().__init__(part, color)


class Hole(Part):
    def __init__(self, radius: float, depth: float|None = None, color: str|None=None):
        part = _.Hole(radius, depth)
        super().__init__(part, color)


class Sphere(Part):
    def __init__(self, radius: float, arc_size1: float = -90, arc_size2: float = 90, arc_size3: float = 360, color: str|None=None):
        part = _.Sphere(radius, arc_size1, arc_size2, arc_size3)
        super().__init__(part, color)


class Torus(Part):
    def __init__(self, major_radius: float, minor_radius: float, minor_start_angle: float = 0, minor_end_angle: float = 360, major_angle: float = 360, color: str|None=None):
        part = _.Torus(major_radius, minor_radius, minor_start_angle, minor_end_angle, major_angle)
        super().__init__(part, color)


class Wedge(Part):
    def __init__(self, xsize: float, ysize: float, zsize: float, xmin: float, zmin: float, xmax: float, zmax: float, color: str|None=None):
        part = _.Wedge(xsize, ysize, zsize, xmin, zmin, xmax, zmax)
        super().__init__(part, color)
