from .base_view import BaseView
from engine.models.base_model import BaseModel
from .opengl_mesh import OpenGLTexturedFace, OpenGLMesh, OpenGLTexturedMaterial
from itertools import chain
from pyglet.gl import GL_LINES
from pyglet.graphics import draw

from math import sin, radians


class DynamicMeshView(BaseView):

    def __init__(self, model: BaseModel, **_):
        super().__init__(model)
        faces = []
        point_seven = (0.7, 0.7, 0.7)
        zeroes = (0, 0, 0)
        material = OpenGLTexturedMaterial(diffuse=point_seven, emissive=zeroes, ambient=point_seven, shininess=0.0,
                                          specular=zeroes, alpha=1.0, name="Rock Surface",
                                          texture_file_name="ROCKS001.TGA")
        bb = model.bounding_box
        for line in bb.lines:
            middle_factor = sin(radians(45))
            middle_x1 = line.original_x1 * middle_factor
            middle_y1 = line.original_y1 * middle_factor
            middle_x2 = line.original_x2 * middle_factor
            middle_y2 = line.original_y2 * middle_factor
            vertices = [(line.original_x1, 0, line.original_y1),
                        (line.original_x2, 0, line.original_y2),
                        (middle_x2, 10, middle_y2),
                        (middle_x1, 10, middle_y1)]
            texture_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
            normals = [(1, 0, 0), (0, 0, 1), (0, 1, 0), (1, 1, 0)]
            face = OpenGLTexturedFace(vertices, texture_coords, normals, material)
            faces.append(face)
            vertices = [(middle_x1, 10, middle_y1),
                        (middle_x2, 10, middle_y2),
                        (bb.x, 15, bb.y)]
            texture_coords = [(0, 0), (1, 0), (1, 1)]
            normals = [(1, 0, 0), (0, 0, 1), (0, 1, 0)]
            face = OpenGLTexturedFace(vertices, texture_coords, normals, material)
            faces.append(face)
        mesh = OpenGLMesh([], faces, name="Asteroid {}".format(model.uuid), group="Asteroids")
        self.set_mesh(mesh)

    def draw(self):
        super(DynamicMeshView, self).draw()
        lines  = self._model.bounding_box.lines
        v3f = [(line.x1, -10.0, line.y1, line.x2, -10.0, line.y2) for line in lines]
        v3f = list(chain(*v3f))
        n_points = int(len(v3f) / 3)
        v3f = ('v3f', v3f)
        c4B = ('c4B', (255, 255, 255, 255) * n_points)
        draw(n_points, GL_LINES, v3f, c4B)
