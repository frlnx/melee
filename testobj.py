from pyglet.window import Window, key
import pyglet
from pyglet.gl import *
from engine.views.opengl_mesh import OpenGLWaveFrontParser, OpenGLMesh, OpenGLFace, OpenGLTexturedFace, OpenGLMaterial
import ctypes
from os import path

from itertools import chain, cycle, combinations
from math import *
from typing import List


class TestWindow(Window):

    def __init__(self, obj):
        super().__init__(width=1280, height=720)
        self.obj = obj
        self._to_cfloat_array = ctypes.c_float * 4
        self.rotation = 0
        pyglet.clock.schedule(self.update)

    def to_cfloat_array(self, *floats):
        return self._to_cfloat_array(*floats)

    def on_resize(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        gluPerspective(60., float(width)/height, 1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        return True

    def update(self, dt):
        self.rotation += dt * 25
        self.obj.timer(dt)

    def on_draw(self):
        self.clear()
        glLoadIdentity()
        glEnable(GL_LIGHTING)

        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.to_cfloat_array(1, 1, 1, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, self.to_cfloat_array(0, 1, 1, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.to_cfloat_array(1.0, 1.0, 1.0, 1.0))

        glTranslated(0, 0, -14)
        glRotatef(self.rotation, 0, 1, 0)
        glRotatef(self.rotation / 10, 1, 0, 0)

        self.obj.draw()
        return

    def on_key_press(self, symbol, modifiers):
        super(TestWindow, self).on_key_press(symbol, modifiers)
        if symbol == key.SPACE:
            self.obj.explode()


class ExplodingMesh(OpenGLMesh):

    cull_face = GL_FRONT_AND_BACK

    def __init__(self, faces: List['OpenGLFace'], textured_faces: List['OpenGLTexturedFace'], name=None, group=None):
        super().__init__(faces, textured_faces, name=name, group=group)
        self.explosion_time = 0
        self._blast = self._render_polyhedron()
        self._blast_material_centre = OpenGLMaterial(diffuse=(.9, .65, .12), ambient=(.9, .65, .12), emissive=(.9, .65, .12), alpha=1.0)
        self._blast_material_edge = OpenGLMaterial(diffuse=(.9, .65, .12), ambient=(.9, .65, .12), emissive=(.9, .65, .12), alpha=0.0)

    @staticmethod
    def _render_polyhedron():
        shape = []
        top = [0, -1, 0, 0, -1, 0]
        upper_circle = list(chain(*[(sin(radians(d)), -0.6, cos(radians(d)),
                                     sin(radians(d)), -0.6, cos(radians(d))) for d in range(0, 360, int(360 / 5))]))
        lower_circle = list(chain(*[(sin(radians(d)), 0.6, cos(radians(d)),
                                     sin(radians(d)), 0.6, cos(radians(d))) for d in range(36, 396, int(360 / 5))]))
        bottom = [0, 1, 0, 0, 1, 0]
        for i in range(5):
            i1 = i * 6
            i2 = i1 + 6
            i3 = ((i + 1) % 5) * 6
            i4 = i3 + 6
            up1 = upper_circle[i1:i2]
            up2 = upper_circle[i3:i4]
            lp1 = lower_circle[i1:i2]
            lp2 = lower_circle[i3:i4]

            shape += top
            shape += up1
            shape += up2

            shape += up1
            shape += lp1
            shape += up2

            shape += lp1
            shape += lp2
            shape += up2

            shape += lp1
            shape += bottom
            shape += lp2
        return shape

    @property
    def blast_interleaved_arrays(self):
        n3f_v3f = []
        for i in range(0, len(self._blast), 6):
            n3f_v3f += [-self._blast[i], -self._blast[i + 1], -self._blast[i + 2],
                        self._blast[i + 3] + self._blast[i] * sqrt(self.explosion_time),
                        self._blast[i + 4] + self._blast[i + 1] * sqrt(self.explosion_time),
                        self._blast[i + 5] + self._blast[i + 2] * sqrt(self.explosion_time)]
        return n3f_v3f

    def explode(self):
        self.explosion_time = 0

    def timer(self, dt):
        self.explosion_time += dt
        self._blast_material_centre.update(alpha=max(0, 1. - sqrt(self.explosion_time / 10)))

    def draw(self):
        super(ExplodingMesh, self).draw()
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT | GL_LIGHTING_BIT)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        glDisable(GL_TEXTURE_2D)
        draw_data = self.blast_interleaved_arrays
        n_points = len(draw_data)
        c_arr = ctypes.c_float * n_points
        c_draw_data = c_arr(*draw_data)
        self._blast_material_centre.set_material()
        glInterleavedArrays(GL_N3F_V3F, 0, c_draw_data)
        glDrawArrays(GL_TRIANGLES, 0, (20 * 3))
        glPopAttrib()
        glPopClientAttrib()


if __name__ == "__main__":
    print(GL_MAX_LIGHTS, GL_LIGHT0)
    op = OpenGLWaveFrontParser(object_class=ExplodingMesh)
    with open(path.join("objects", "cockpit.obj"), 'r') as f:
        obj = op.parse(f.readlines())
    win = TestWindow(obj)
    pyglet.app.run()
