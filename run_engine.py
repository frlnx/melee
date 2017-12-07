#!/usr/bin/env python
import ctypes

from engine.controllers.factories import ShipControllerFactory
from engine.views.ship import ShipView
from engine.input_handlers import GamePad

from pyglet.gl import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHT0, GL_POSITION, GL_LIGHTING
from pyglet.gl import glMatrixMode, glLoadIdentity, glEnable, gluPerspective, glLightfv, glTranslated, glRotatef
import pyglet


class Window(pyglet.window.Window):

    def __init__(self, ship_view: ShipView):
        super().__init__(width=1280, height=720)
        self.lightfv = ctypes.c_float * 4
        self.ship_view = ship_view

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
        glTranslated(0, -13, 0)
        glEnable(GL_LIGHTING)

        self.ship_view.draw()


if __name__ == '__main__':
    gamepad = GamePad()
    sf = ShipControllerFactory()
    ship_controller = sf.manufacture("wolf", gamepad)
    window = Window(ship_controller._view)
    pyglet.clock.schedule(ship_controller.update)
    pyglet.app.run()
