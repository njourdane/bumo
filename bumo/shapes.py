"""A module used to store shapes-related stuff."""
from enum import Enum
from typing import TypeAlias, Iterable, TextIO, TypeVar
from hashlib import md5
from sys import stdout

from tabulate import tabulate
import build123d as _

from . import config
from .colors import color_to_str


Hash: TypeAlias = str


class ShapeState(Enum):
    """The possible states of a shape for a mutation."""

    ADDED = 1
    ALTERED = 2
    UNTOUCHED = 3
    REMOVED = 4

def hash_shape(shape: _.Shape) -> Hash:
    """Return a reproducible hash.
    OCP 7.2 might produce better hashes that could make this unnecessary."""

    def to_int(number: float) -> int:
        return int(number * 1000)

    def serialize_vertex(vertex: _.Vertex) -> tuple:
        return tuple(to_int(v) for v in vertex.to_tuple())

    def serialize_edge(edge: _.Edge) -> tuple:
        vertices = tuple(serialize_vertex(v) for v in edge.vertices())
        is_circle = edge.geom_type == _.GeomType.CIRCLE
        radius = to_int(edge.radius) if is_circle else 0
        return (edge.geom_type, vertices, radius)

    def serialize_face(face: _.Face) -> tuple:
        return tuple(serialize_edge(edge) for edge in face.edges())

    def serialize_part(part: _.Part) -> tuple:
        return tuple(serialize_face(face) for face in part.faces())

    if isinstance(shape, _.Vertex):
        serialized = serialize_vertex(shape)
    elif isinstance(shape, _.Edge):
        serialized = serialize_edge(shape)
    elif isinstance(shape, _.Face):
        serialized = serialize_face(shape)
    elif isinstance(shape, _.Part):
        serialized = serialize_part(shape)
    else:
        raise TypeError

    return md5(str(serialized).encode()).hexdigest()


ShapeLike: TypeAlias = _.Face | _.Edge | _.Vertex
ShapeT = TypeVar("ShapeT", bound=_.Face | _.Edge | _.Vertex)


def add_shape_hash(shape: ShapeT) -> ShapeT:
    """Add the hash of the given shape to the shape label."""
    if not shape.label:
        shape.label = hash_shape(shape)
    return shape


class ShapeList(_.ShapeList[ShapeT]):
    """A custom ShapeList that automatically adds a hash to the shape label,
    and with some extra utility methods."""

    def __init__(self, shapes: Iterable[ShapeT]):
        super().__init__(add_shape_hash(shape) for shape in shapes)

    def __setitem__(self, index: int, shape: ShapeT):
        super().__setitem__(index, add_shape_hash(shape))

    def insert(self, index: int, shape: ShapeT):
        super().insert(index, add_shape_hash(shape))

    def append(self, shape: ShapeT):
        super().append(add_shape_hash(shape))

    def extend(self, other: Iterable[ShapeT]):
        super().extend(
            other if isinstance(other, ShapeList)
            else [add_shape_hash(shape) for shape in other]
        )

    def get(self, shape_hash: Hash) -> ShapeT:
        """Return the shape that belongs to the given hash."""
        for shape in self:
            if shape.label == shape_hash:
                return shape
        raise KeyError(shape_hash)

    def contain(self, edge_hash: Hash) -> bool:
        """Return True if the given hash is found in the shape list."""
        for edge in self:
            if edge.label == edge_hash:
                return True
        return False

    def hashes(self) -> list[Hash]:
        """Return a list of hashes corresponding to the all shapes hash."""
        return [shape.label for shape in self]

    def info(self, file: TextIO|None=None):
        """Prints an info table of all the faces to the given file or stream
        (default to stdout)"""

        def str_vector(vector: _.Vector) -> str:
            return f"[{', '.join([f'{ n :.1g}' for n in vector.to_tuple()])}]"

        def row(shape: _.Shape) -> tuple:
            color = shape.color or config.DEFAULT_COLOR
            r, g, b = [int(c * 255) for c in color.to_tuple()[:3]]

            start = f"\033[38;2;{ r };{ g };{ b }m"
            end = "\033[0m"

            columns = {
                "hash": shape.label[:6],
                "type": shape.geom_type,
                "area": f"{ shape.area :.2g}",
                "position": str_vector(shape.position),
                "orientation": str_vector(shape.orientation),
                "color_hex": color_to_str(color, True),
                "color_name": color_to_str(color, False),
            }

            return tuple(
                (f"{ start }{ color }{ end }" if config.INFO_COLOR else color)
                for header, color in columns.items()
                if header in config.COLUMNS_SHAPES
            )

        str_table = tabulate(
            [row(shape) for shape in self],
            [header.title() for header in config.COLUMNS_SHAPES],
            config.INFO_TABLE_FORMAT
        )
        print(str_table, file=file or stdout)
