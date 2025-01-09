import build123d as _

from .part import Part


class Box(Part):
    def __init__(self, length: float, width: float, height: float) -> None:
        super().__init__(_.Box(length, width, height))


class Cone(Part):
    def __init__(self, bottom_radius: float, top_radius: float, height: float, arc_size: float) -> None:
        super().__init__(_.Cone(bottom_radius, top_radius, height, arc_size))


class CounterBoreHole(Part):
    def __init__(self, radius: float, counter_bore_radius: float, counter_bore_depth: float, depth: float|None = None):
        super().__init__(_.CounterBoreHole(radius, counter_bore_radius, counter_bore_depth, depth))


class CounterSinkHole(Part):
    def __init__(self, radius: float, counter_sink_radius: float, depth: float|None = None, counter_sink_angle: float = 82):
        super().__init__(_.CounterSinkHole(radius, counter_sink_radius, depth, counter_sink_angle))


class Cylinder(Part):
    def __init__(self, radius: float, height: float, arc_size: float=360) -> None:
        super().__init__(_.Cylinder(radius, height, arc_size))


class Hole(Part):
    def __init__(self, radius: float, depth: float|None = None):
        super().__init__(_.Hole(radius, depth))


class Sphere(Part):
    def __init__(self, radius: float, arc_size1: float = -90, arc_size2: float = 90, arc_size3: float = 360):
        super().__init__(_.Sphere(radius, arc_size1, arc_size2, arc_size3))


class Torus(Part):
    def __init__(self, major_radius: float, minor_radius: float, minor_start_angle: float = 0, minor_end_angle: float = 360, major_angle: float = 360):
        super().__init__(_.Torus(major_radius, minor_radius, minor_start_angle, minor_end_angle, major_angle))


class Wedge(Part):
    def __init__(self, xsize: float, ysize: float, zsize: float, xmin: float, zmin: float, xmax: float, zmax: float):
        super().__init__(_.Wedge(xsize, ysize, zsize, xmin, zmin, xmax, zmax))
