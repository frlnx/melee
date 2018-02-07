from pyglet.window import Window
import pyglet
from pyglet.gl import *
from engine.views.opengl_mesh import OpenGLWaveFrontParser, OpenGLMesh
from pywavefront import Wavefront
import ctypes


class TestWindow(Window):

    point_flag_map = {3: GL_TRIANGLES, 4: GL_QUADS}

    def __init__(self, obj):
        super().__init__(width=1280, height=720)
        self.obj = obj
        self.lightfv = ctypes.c_float * 4
        self.rotation = 0
        pyglet.clock.schedule(self.update)

    def on_resize(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        gluPerspective(60., float(width)/height, 1., 100.)
        glMatrixMode(GL_MODELVIEW)
        return True

    def update(self, dt):
        self.rotation += dt * 90

    def on_draw(self):
        self.clear()
        glLoadIdentity()
        glEnable(GL_LIGHTING)

        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat * 4)(1, 1, 1, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, self.lightfv(2, 2, -3, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * 4)(1.5, 1.0, 1.5, 1.0))
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, self.lightfv(-2, 2, -3, 1))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (GLfloat * 4)(1.0, 0.5, 0.5, 1.0))
        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, self.lightfv(-2, -2, -3, 1))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (GLfloat * 4)(0.5, 0.5, 1.0, 1.0))
        glEnable(GL_LIGHT3)
        glLightfv(GL_LIGHT3, GL_POSITION, self.lightfv(2, -2, -3, 1))
        glLightfv(GL_LIGHT3, GL_DIFFUSE, (GLfloat * 4)(0.5, 0.5, 0.5, 1.0))

        glTranslated(0, 0, -4)
        glRotatef(self.rotation, 0, 1, 0)
        glRotatef(self.rotation / 10, 1, 0, 0)

        self.obj.draw()


if __name__ == "__main__":
    print(GL_MAX_LIGHTS, GL_LIGHT0)
    op = OpenGLWaveFrontParser()
    with open("objects\\cockpit.obj", 'r') as f:
        obj = op.parse(f.readlines())
    #obj = Wavefront("objects\\cockpit.obj")
    win = TestWindow(obj)
    pyglet.app.run()