from itertools import chain
from math import *
from typing import Dict, Tuple

from engine.physics.polygon import Line, Polygon
from engine.views.opengl_mesh import OpenGLMesh, OpenGLFace, OpenGLMaterial


class FlexibleMesh(OpenGLMesh):

    def __init__(self, polygon: Polygon, material: OpenGLMaterial):
        self.material = material
        self.polygon = polygon
        self.line_triples: Dict[Line, Tuple[Line, Line]] = {t: (p, n) for p, t, n in polygon.lines_outer_triplets()}
        self.line_faces: Dict[Line, Tuple[OpenGLFace, OpenGLFace]] = {l: self.make_faces(l) for l in polygon.lines}
        faces = list(chain(*self.line_faces.values()))
        for line in polygon.lines:
            line.observe(self.line_callback, "move")
            self.line_callback(line)
        super().__init__(faces, [])

    def make_faces(self, line: Line):
        (ox1, oy1), (ox2, oy2), (nx1, ny1), (nx2, ny2) = self.make_face_coordinates(line)
        face1 = OpenGLFace([(ox1, 0, oy1), (ox2, 0, oy2), (nx2, 0, ny2)], [(0, 1, 0)] * 3, self.material)
        face2 = OpenGLFace([(ox1, 0, oy1), (nx2, 0, ny2), (nx1, 0, ny1)], [(0, 1, 0)] * 3, self.material)
        return face1, face2

    def line_callback(self, line: Line):
        for l in self.line_triples[line]:
            self.update_line(l)
        self.update_line(line)

    def update_line(self, line: Line):
        (ox1, oy1), (ox2, oy2), (nx1, ny1), (nx2, ny2) = self.make_face_coordinates(line)
        face1, face2 = self.line_faces[line]
        face1.set_vertices([(ox1, 0, oy1), (ox2, 0, oy2), (nx2, 0, ny2)])
        face2.set_vertices([(ox1, 0, oy1), (nx2, 0, ny2), (nx1, 0, ny1)])

    def make_face_coordinates(self, line):
        prev_line, next_line = self.line_triples[line]
        radii1 = prev_line.radii + (line.radii - prev_line.radii) / 2
        radii2 = line.radii + (next_line.radii - line.radii) / 2
        ox1, oy1 = line.x1 + cos(radii1) * 0.2, line.y1 + sin(radii1) * 0.2
        ox2, oy2 = line.x1 - cos(radii1) * 0.2, line.y1 - sin(radii1) * 0.2
        nx1, ny1 = line.x2 + cos(radii2) * 0.2, line.y2 + sin(radii2) * 0.2
        nx2, ny2 = line.x2 - cos(radii2) * 0.2, line.y2 - sin(radii2) * 0.2
        return (ox1, oy1), (ox2, oy2), (nx1, ny1), (nx2, ny2)
