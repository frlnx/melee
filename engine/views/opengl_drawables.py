import ctypes
from math import *

from pyglet.gl import *

from engine.views.opengl_mesh import OpenGLMaterial
from .opengl_mesh import Drawable
from .opengl_shapes import shape_factory


# noinspection PyTypeChecker
class ExplosionDrawable(Drawable):

    def __init__(self):
        self._blast = shape_factory.polyhedron
        self.explosion_time = 0
        self._blast_material_centre = OpenGLMaterial(diffuse=(.9, .65, .12), ambient=(.9, .65, .12),
                                                     emissive=(.9, .65, .12), alpha=1.0)
        self._blast_material_edge = OpenGLMaterial(diffuse=(.9, .65, .12), ambient=(.9, .65, .12),
                                                   emissive=(.9, .65, .12), alpha=0.0)

    @property
    def blast_interleaved_arrays(self):
        n3f_v3f = []
        animation_time = max(0, self.explosion_time)
        animation_time = sqrt(animation_time * 10)
        for i in range(0, len(self._blast), 6):
            n3f_v3f += [-self._blast[i], -self._blast[i + 1], -self._blast[i + 2],
                        (self._blast[i + 3] + self._blast[i]) * animation_time,
                        (self._blast[i + 4] + self._blast[i + 1]) * animation_time,
                        (self._blast[i + 5] + self._blast[i + 2]) * animation_time]
        return n3f_v3f

    def explode(self):
        self.explosion_time = 0

    def timer(self, dt):
        self.explosion_time += dt
        animation_time = max(0, self.explosion_time)
        self._blast_material_centre.update(alpha=max(0., 1. - sqrt(animation_time * 2)))

    def draw(self):
        draw_data = self.blast_interleaved_arrays
        n_points = len(draw_data)
        c_arr = ctypes.c_float * n_points
        c_draw_data = c_arr(*draw_data)
        self._configure_cull_face()
        self._blast_material_centre.set_material()
        glInterleavedArrays(GL_N3F_V3F, 0, c_draw_data)
        glDrawArrays(GL_TRIANGLES, 0, (20 * 3))
