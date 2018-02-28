import ctypes

from engine.views.base_view import BaseView
from engine.views.factories import DynamicViewFactory

from pyglet.gl import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHT0, GL_POSITION, GL_LIGHTING
from pyglet.gl import GL_DIFFUSE, GLfloat, GL_AMBIENT
from pyglet.gl import glMatrixMode, glLoadIdentity, glEnable, gluPerspective, glLightfv, glRotatef
from pywavefront import Wavefront
import pyglet


class Window(pyglet.window.Window):

    def __init__(self):
        super().__init__(width=1280, height=720)
        self.lightfv = ctypes.c_float * 4
        self.view_factory = DynamicViewFactory()
        self.views = set()
        self.new_views = set()
        self.del_views = set()
        self.center = None
        self.backdrop = Wavefront("objects/backdrop.obj")
        #self.spawn_sound = pyglet.media.load('plasma.mp3', streaming=False)

    def spawn(self, model):
        view = self.view_factory.manufacture(model)
        #self.spawn_sound.play()
        self.new_views.add(view)
        if self.center is None:
            self.center = view

    def del_view(self, view: BaseView):
        self.del_views.add(view)

    def center_camera_on(self, view: BaseView):
        self.center = view

    def on_resize(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        gluPerspective(60., float(width) / height, 1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        return True

    def on_draw(self):
        self.clear()
        glLoadIdentity()
        glEnable(GL_LIGHTING)

        glRotatef(90, 1, 0, 0)
        self.center.align_camera()

        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat * 4)(1, 1, 1, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, self.lightfv(0, 1, 1, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0, 1.0))
        #glLightfv(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, (GLfloat * 1)(.005))
        #glEnable(GL_LIGHT0)
        self.backdrop.draw()

        self.center.center_camera()

        for view in self.views:
            view.draw()
        self.integrate_new_views()
        self.remove_views()

    def integrate_new_views(self):
        self.views.update(self.new_views)
        self.new_views.clear()

    def remove_views(self):
        self.views = self.views - self.del_views
        self.del_views.clear()

