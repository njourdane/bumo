"""Module containing the Mutation class."""
from __future__ import annotations

import build123d as _

from .shapes import Hash, ShapeState, hash_shape, ShapeList, ShapeLike


class Mutation:
    """Class managing the mutation applied when mutating the object."""

    def __init__(
        self,
        obj: _.Part,
        previous: Mutation | None,
        name: str,
        index: int,
        faces_alias: dict[Hash, Hash] | None
    ) -> None:
        self.previous = previous
        self.name = name
        self.index = index
        self.faces_alias = faces_alias or {}

        self.id = f"{ name }-{ index }"

        self.faces = ShapeList(obj.faces())
        self.faces_state = self.get_shapes_state(_.Face)

        self.faces_added = self.filter_shapes(ShapeState.ADDED, _.Face)
        self.faces_altered = self.filter_shapes(ShapeState.ALTERED, _.Face)
        self.faces_untouched = self.filter_shapes(ShapeState.UNTOUCHED, _.Face)
        self.faces_removed = self.filter_shapes(ShapeState.REMOVED, _.Face)

        self.edges = ShapeList(obj.edges())
        self.edges_state = self.get_shapes_state(_.Edge)
        self.edges_added = self.filter_shapes(ShapeState.ADDED, _.Edge)
        self.edges_altered = self.filter_shapes(ShapeState.ALTERED, _.Edge)
        self.edges_untouched = self.filter_shapes(ShapeState.UNTOUCHED, _.Edge)
        self.edges_removed = self.filter_shapes(ShapeState.REMOVED, _.Edge)

        self.vertices = ShapeList(obj.vertices())

    def get_shapes(self, shape_type: type[ShapeLike]) -> ShapeList:
        """Return the mutation shapes belonging the given shape type."""
        if shape_type == _.Face:
            return self.faces
        if shape_type == _.Edge:
            return self.edges
        if shape_type == _.Vertex:
            return self.vertices
        raise TypeError

    def __repr__(self):
        return self.id

    def filter_shapes(self, state: ShapeState, shape_type: type[ShapeLike]) -> ShapeList:
        """Return the shapes of the current object that match the given state."""

        assert shape_type in [_.Face, _.Edge]

        mutation = (
            self.previous if self.previous and state == ShapeState.REMOVED
            else self
        )
        shapes = mutation.get_shapes(shape_type)
        shapes_state = self.faces_state if shape_type == _.Face else self.edges_state

        faces = [shapes.get(h) for h, s in shapes_state.items() if s == state]
        return ShapeList(faces)

    def get_shapes_state(self, shape_type: type[ShapeLike]) -> dict[Hash, ShapeState]:
        """Return a dictionnary holding the state of each face of the object."""

        def get_state(shape: ShapeLike) -> ShapeState:
            if not self.previous:
                return ShapeState.ADDED

            if self.previous.get_shapes(shape_type).contain(shape.label):
                return ShapeState.UNTOUCHED

            if isinstance(shape, _.Face) and self.is_altered_face(shape):
                return ShapeState.ALTERED

            if isinstance(shape, _.Edge) and self.is_altered_edge(shape):
                return ShapeState.ALTERED

            return ShapeState.ADDED

        shapes = self.get_shapes(shape_type)
        shapes_state = {shape.label: get_state(shape) for shape in shapes}

        if self.previous:
            for previous_shape in self.previous.get_shapes(shape_type):
                if not shapes.contain(previous_shape.label):
                    shapes_state[previous_shape.label] = ShapeState.REMOVED

        return shapes_state

    @classmethod
    def is_altered_faces(cls, this_face: _.Face, that_face: _.Face):
        """Check if the two given faces were altered or not, by comparing the
        edges of each face: if a similar edge is found, they are altered."""

        for this_edge in this_face.edges():
            this_hash = hash_shape(this_edge)
            for that_edge in that_face.edges():
                if this_hash == hash_shape(that_edge):
                    return True

        if (
            this_face.geom_type == that_face.geom_type
            and this_face.location == that_face.location
            and this_face.center_location == that_face.center_location
        ):
            return True

        return False

    def is_altered_face(self, face: _.Face):
        """Check if the given face were altered, by comparing the edges of the
        face: if a similar edge is found in the object, it is altered."""

        if not self.previous:
            return True

        for edge in face.edges():
            if self.previous.edges.contain(hash_shape(edge)):
                return True

        for that_face in self.previous.faces:
            if (face.geom_type == that_face.geom_type
                and face.location == that_face.location
                and face.center_location == that_face.center_location
            ):
                return True

        return False

    def is_altered_edge(self, edge: _.Edge):
        """Check if the given edge were altered, by comparing the vertices of
        the face: if a similar vertex is found in the object, it is altered."""

        if not self.previous:
            return True

        for vertex in edge.vertices():
            if self.previous.vertices.contain(hash_shape(vertex)):
                return True

        return False
