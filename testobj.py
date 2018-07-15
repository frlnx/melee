import ctypes
from os import path

import pyglet
from pyglet.gl import *
from pyglet.window import Window, key

from engine.views.opengl_animations import Explosion
from engine.views.opengl_drawables import ExplosionDrawable
from engine.views.opengl_mesh import OpenGLWaveFrontParser, OpenGLMesh


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
            explosion = ExplosionDrawable()
            pyglet.clock.schedule(explosion.timer)
            self.obj.add_drawable(explosion)
            explode_animation = Explosion(self.obj.all_faces)
            self.obj.add_animation(explode_animation.animate)
            self.obj.set_double_sided(True)
            #for material in self.obj.materials.values():
            #    material.ambient = (10., 10., 10.)
            #self.obj.add_transmutation(extinguish)


if __name__ == "__main__":
    print(GL_MAX_LIGHTS, GL_LIGHT0)
    op = OpenGLWaveFrontParser(object_class=OpenGLMesh)
    with open(path.join("objects", "cockpit.obj"), 'r') as f:
        obj = op.parse(f.readlines())
    win = TestWindow(obj)
    pyglet.app.run()
