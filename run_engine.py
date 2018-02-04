#!/usr/bin/env python
import ctypes
from itertools import combinations

from engine.controllers.factories import ShipControllerFactory, BaseFactory
from engine.views.base_view import BaseView
from engine.input_handlers import InputHandler, GamePad

from pyglet.gl import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHT0, GL_LIGHT1, GL_POSITION, GL_LIGHTING
from pyglet.gl import GL_DIFFUSE, GL_QUADRATIC_ATTENUATION, GLfloat, GL_AMBIENT
from pyglet.gl import glMatrixMode, glLoadIdentity, glEnable, glDisable, gluPerspective, glLightfv, glTranslated, glRotatef
from pywavefront import Wavefront
import pyglet


class Window(pyglet.window.Window):

    def __init__(self):
        super().__init__(width=1280, height=720)
        self.lightfv = ctypes.c_float * 4
        self.views = set()
        self.new_views = set()
        self.center = None
        self.backdrop = Wavefront("objects/backdrop.obj")

    def add_view(self, view: BaseView):
        self.new_views.add(view)
        if self.center is None:
            self.center = view

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

    def integrate_new_views(self):
        self.views.update(self.new_views)
        self.new_views.clear()


class Engine(pyglet.app.EventLoop):

    def __init__(self):
        super().__init__()
        self.controllers = set()
        self.ships = set()
        self.bf = BaseFactory()
        self.sf = ShipControllerFactory()
        self.window = Window()
        self.has_exit = True
        pyglet.clock.schedule(self.update)
        pyglet.clock.set_fps_limit(60)

    def on_enter(self):
        self.spawn_ship("wolf", [0, 0, 0], GamePad(1))
        self.spawn_ship("dolph", [10, 0, 2], GamePad(0))
        self.spawn_ship("dolph", [0, 0, 20], GamePad(0))
        self.spawn_ship("dolph", [-10, 0, -2], GamePad(0))

    def spawn_ship(self, name, location, input_device=None):
        ship = self.sf.manufacture(name, input_device)
        self.propagate_target(ship)
        ship.move_to(location)
        self.spawn(ship)
        self.ships.add(ship)

    def spawn(self, controller):
        self.window.add_view(controller.view)
        self.controllers.add(controller)

    def propagate_target(self, ship):
        for c in self.controllers:
            c.register_target(ship._model)
            ship.register_target(c._model)

    def update(self, dt):
        spawns = []
        for controller in self.controllers:
            controller.update(dt)
            spawns += [self.bf.manufacture(model, controller._gamepad) for model in controller.spawns]
        for ship in self.ships:
            for controller in self.controllers:
                if ship != controller:
                    ship.solve_collision(controller._model)
        #for c1, c2 in combinations(self.controllers, 2):
        #    c1.solve_collision(c2._model)
        for spawned_controller in spawns:
            self.spawn(spawned_controller)


if __name__ == '__main__':
    engine = Engine()
    engine.run()
