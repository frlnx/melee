#!/usr/bin/env python
import ctypes
from itertools import combinations

from engine.controllers.factories import ShipControllerFactory
from engine.views.base_view import BaseView
from engine.input_handlers import InputHandler, GamePad

from pyglet.gl import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHT0, GL_POSITION, GL_LIGHTING
from pyglet.gl import glMatrixMode, glLoadIdentity, glEnable, gluPerspective, glLightfv, glTranslated, glRotatef
import pyglet


class Window(pyglet.window.Window):

    def __init__(self):
        super().__init__(width=1280, height=720)
        self.lightfv = ctypes.c_float * 4
        self.views = set()
        self.center = None

    def add_view(self, view: BaseView):
        self.views.add(view)
        if self.center is None:
            self.center = view

    def center_camera_on(self, view: BaseView):
        self.center = view

    def on_resize(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        gluPerspective(60., float(width)/height, 1., 100.)
        glMatrixMode(GL_MODELVIEW)
        return True

    def on_draw(self):
        self.clear()
        glLoadIdentity()

        glLightfv(GL_LIGHT0, GL_POSITION, self.lightfv(-1.0, 1.0, 1.0, 0.0))
        glEnable(GL_LIGHT0)

        glRotatef(90, 1, 0, 0)
        glEnable(GL_LIGHTING)

        self.center.center_camera()
        for view in self.views:
            view.draw()


class Engine(pyglet.app.EventLoop):

    def __init__(self):
        super().__init__()
        self.controllers = set()
        self.sf = ShipControllerFactory()
        self.window = Window()
        self.has_exit = True
        pyglet.clock.schedule(self.update)

    def on_enter(self):
        self.spawn_ship("wolf", [0, 0, 0], GamePad(1))
        self.spawn_ship("dolph", [10, 0, 2], GamePad(0))

    def spawn_ship(self, name, location, input_device=None):
        ship = self.sf.manufacture(name, input_device)
        self.propagate_target(ship)
        ship.move_to(location)
        self.window.add_view(ship.view)
        self.controllers.add(ship)

    def propagate_target(self, ship):
        for c in self.controllers:
            c.register_target(ship._model)
            ship.register_target(c._model)

    def update(self, dt):
        for controller in self.controllers:
            controller.update(dt)
        for c1, c2 in combinations(self.controllers, 2):
            if c1.collides(c2._model):
                print("Bang")

if __name__ == '__main__':
    engine = Engine()
    engine.run()
