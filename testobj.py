import ctypes
from math import *
from os import path

import pyglet
from pyglet.gl import *
from pyglet.window import Window, key

from engine.physics.polygon import Polygon
from engine.views.opengl_animations import Explosion
from engine.views.opengl_drawables import ExplosionDrawable
from engine.views.opengl_mesh import OpenGLWaveFrontParser, OpenGLMesh, OpenGLMaterial, OpenGLFace


class TestWindow(Window):

    def __init__(self, obj):
        super().__init__(width=1280, height=720)
        op = OpenGLWaveFrontParser(object_class=OpenGLMesh)
        with open(path.join("objects", "backdrop.obj"), 'r') as f:
            self.backdrop = op.parse(f.readlines())
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
        self.backdrop.draw()
        self.obj.draw()
        self.backdrop.draw_transparent()
        self.obj.draw_transparent()
        return

    def on_key_press(self, symbol, modifiers):
        super(TestWindow, self).on_key_press(symbol, modifiers)
        if symbol == key.SPACE:
            explosion = ExplosionDrawable()
            pyglet.clock.schedule(explosion.timer)
            self.obj.add_drawable(explosion)
            explode_animation = Explosion(self.obj.all_faces)
            self.obj.add_animation(explode_animation.animate)
            self.obj.set_double_sided(True)


if __name__ == "__main__":
    def _hexagon_fence(polygon):
        faces = []
        material = OpenGLMaterial(diffuse=(.54, .81, .94), ambient=(.54, .81, .94), alpha=.5, name="Shield")
        for line in polygon.lines:
            c_x, c_z = line.centroid
            c_y = 0
            half_length = line.length / 2
            r = line.radii + radians(90)
            normals = [(cos(r), 0, sin(r))] * 3
            hex_points = [(c_x, 1, c_z), (line.x1, half_length, line.y1), (line.x1, -half_length, line.y1),
                          (c_x, -1, c_z), (line.x2, -half_length, line.y2), (line.x2, half_length, line.y2)]
            coords1 = hex_points[-1]
            for coords2 in hex_points:
                vertices = [(c_x, c_y, c_z), coords1, coords2]
                coords1 = coords2
                face = OpenGLFace(vertices, normals, material)
                faces.append(face)
            normals = [(-cos(r), 0, -sin(r))] * 3
            coords1 = hex_points[0]
            for coords2 in reversed(hex_points):
                vertices = [(c_x, c_y, c_z), coords1, coords2]
                coords1 = coords2
                face = OpenGLFace(vertices, normals, material)
                faces.append(face)
        mesh = OpenGLMesh(faces, [], name="Shield", group="Shields")
        mesh.set_double_sided(True)
        return mesh

    print(GL_MAX_LIGHTS, GL_LIGHT0)
    #op = OpenGLWaveFrontParser(object_class=OpenGLMesh)
    #with open(path.join("objects", "cockpit.obj"), 'r') as f:
    #    obj = op.parse(f.readlines())
    polygon = Polygon.manufacture_open([(0, 0), (1, 1), (1, 2.5), (2.5, 3), (3, 4.5)])
    obj = _hexagon_fence(polygon)
    win = TestWindow(obj)
    pyglet.app.run()
