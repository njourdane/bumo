"""Module containing the Mutation class."""
from __future__ import annotations

import build123d as _

from .colors import cast_color
from .shapes import Hash, ShapeState, FaceDict, EdgeDict, hash_shape, ShapeList


class Mutation:
    """Class managing the mutation applied when mutating the object."""

    def __init__(
        self,
        obj: _.Part,
        previous: Mutation | None,
        name: str,
        index: int,
        color: _.Color | None,
        faces_alias: dict[Hash, Hash] | None
    ) -> None:
        self.previous = previous
        self.name = name
        self.index = index
        self.color = cast_color(color) if color else None
        self.faces_alias = faces_alias or {}

        self.id = f"{ name }-{ index }"

        self.faces = FaceDict({f.label: f for f in ShapeList(obj.faces())})
        self.faces_state = self.get_faces_state()
        self.faces_added = self.filter_faces(ShapeState.ADDED)
        self.faces_altered = self.filter_faces(ShapeState.ALTERED)
        self.faces_untouched = self.filter_faces(ShapeState.UNTOUCHED)
        self.faces_removed = self.filter_faces(ShapeState.REMOVED)

        self.edges = EdgeDict({e.label: e for e in ShapeList(obj.edges())})
        self.edges_state = self.get_edges_state()
        self.edges_added = self.filter_edges(ShapeState.ADDED)
        self.edges_altered = self.filter_edges(ShapeState.ALTERED)
        self.edges_untouched = self.filter_edges(ShapeState.UNTOUCHED)
        self.edges_removed = self.filter_edges(ShapeState.REMOVED)

        self.vertices = {v.label: v for v in ShapeList(obj.vertices())}

    def __repr__(self):
        return self.id

    def filter_faces(self, state: ShapeState) -> FaceDict:
        """Return the faces of the current object that match the given state."""

        faces = (
            self.previous.faces
            if self.previous and state == ShapeState.REMOVED
            else self.faces
        )
        faces = {h: faces[h] for h, s in self.faces_state.items() if s == state}
        return FaceDict(faces)

    def filter_edges(self, state: ShapeState) -> EdgeDict:
        """Return the edges of the current object that match the given state."""

        edges = (
            self.previous.edges
            if self.previous and state == ShapeState.REMOVED
            else self.edges
        )
        edges = {h: edges[h] for h, e in self.edges_state.items() if e == state}
        return EdgeDict(edges)

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
            if hash_shape(edge) in self.previous.edges:
                return True

        for that_face in self.previous.faces():
            if (face.geom_type == that_face.geom_type
                and face.location == that_face.location
                and face.center_location == that_face.center_location
            ):
                return True

        return False

    def get_faces_state(self) -> dict[Hash, ShapeState]:
        """Return a dictionnary holding the state of each face of the object."""

        def get_state(face_hash: Hash, face: _.Face) -> ShapeState:
            if not self.previous:
                return ShapeState.ADDED

            if face_hash in self.previous.faces:
                return ShapeState.UNTOUCHED

            if self.is_altered_face(face):
                return ShapeState.ALTERED

            return ShapeState.ADDED

        faces = {fh: get_state(fh, face) for fh, face in self.faces.items()}

        if self.previous:
            for face_hash in self.previous.faces:
                if face_hash not in self.faces:
                    faces[face_hash] = ShapeState.REMOVED

        return faces

    def is_altered_edge(self, edge: _.Edge):
        """Check if the given edge were altered, by comparing the vertices of
        the face: if a similar vertex is found in the object, it is altered."""

        if not self.previous:
            return True

        for vertex in edge.vertices():
            if hash_shape(vertex) in self.previous.vertices:
                return True

        return False

    def get_edges_state(self) -> dict[Hash, ShapeState]:
        """Return a dictionnary holding the state of each edge of the object."""

        def get_state(edge_hash: Hash, edge: _.Edge) -> ShapeState:
            if not self.previous:
                return ShapeState.ADDED

            if edge_hash in self.previous.edges:
                return ShapeState.UNTOUCHED

            if self.is_altered_edge(edge):
                return ShapeState.ALTERED

            return ShapeState.ADDED

        edges = {eh: get_state(eh, edge) for eh, edge in self.edges.items()}

        if self.previous:
            for edge_hash in self.previous.edges:
                if edge_hash not in self.edges:
                    edges[edge_hash] = ShapeState.REMOVED

        return edges
