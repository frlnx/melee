from pyglet.window import Window
import pyglet
from pyglet.gl import *
from engine.views.opengl_mesh import OpenGLWaveFrontParser, OpenGLMesh
from pywavefront import Wavefront
import ctypes
from os import path


class TestWindow(Window):

    point_flag_map = {3: GL_TRIANGLES, 4: GL_QUADS}

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
        self.rotation += dt * 90

    def on_draw(self):
        self.clear()
        glLoadIdentity()
        glEnable(GL_LIGHTING)

        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.to_cfloat_array(1, 1, 1, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, self.to_cfloat_array(0, 1, 1, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.to_cfloat_array(1.0, 1.0, 1.0, 1.0))

        glTranslated(0, 0, -4)
        glRotatef(self.rotation, 0, 1, 0)
        glRotatef(self.rotation / 10, 1, 0, 0)

        self.obj.draw()
        return



if __name__ == "__main__":
    print(GL_MAX_LIGHTS, GL_LIGHT0)
    op = OpenGLWaveFrontParser()
    with open(path.join("objects", "backdrop.obj"), 'r') as f:
        obj = op.parse(f.readlines())
    #obj = Wavefront("objects\\cockpit.obj")
    win = TestWindow(obj)
    pyglet.app.run()
