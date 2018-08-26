import ctypes
from math import *
from os import path

import pyglet
from pyglet.gl import *
from pyglet.window import Window, key

from engine.physics.polygon import Polygon
from engine.views.flexible_mesh import FlexibleMesh
from engine.views.opengl_animations import Explosion
from engine.views.opengl_drawables import ExplosionDrawable
from engine.views.opengl_mesh import OpenGLWaveFrontParser, OpenGLMesh, OpenGLMaterial


class TestWindow(Window):

    def __init__(self, obj):
        super().__init__(width=1280, height=720)
        op = OpenGLWaveFrontParser(object_class=OpenGLMesh)
        with open(path.join("objects", "backdrop.obj"), 'r') as f:
            self.backdrop = op.parse(f.readlines())
        self.obj: FlexibleMesh = obj
        self._to_cfloat_array = ctypes.c_float * 4
        self.rotation = 0
        pyglet.clock.schedule(self.update)

    def to_cfloat_array(self, *floats):
        return self._to_cfloat_array(*floats)

    def on_resize(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        gluPerspective(60., float(width) / height, 1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        return True

    def update(self, dt):
        self.rotation += dt * 25
        self.obj.timer(dt)
        for i, line in enumerate(self.obj.polygon.lines):
            r = radians(i * 23 + self.rotation)
            line.set_points(i, cos(r), i+1, cos(r + radians(23)))

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
        glRotatef(90, 1, 0, 0)
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

    print(GL_MAX_LIGHTS, GL_LIGHT0)

    #op = OpenGLWaveFrontParser(object_class=OpenGLMesh)
    #with open(path.join("objects", "cockpit.obj"), 'r') as f:
    #    obj = op.parse(f.readlines())
    material = OpenGLMaterial(diffuse=(.54, .81, .94), ambient=(.54, .81, .94), alpha=1, name="Shield")
    polygon = Polygon.manufacture_open([(i, 0) for i in range(10)])

    obj = FlexibleMesh(polygon, material)
    obj.set_double_sided(True)
    win = TestWindow(obj)
    pyglet.app.run()
