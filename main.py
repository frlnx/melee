#!/usr/bin/env python
"""This script shows an example of using the PyWavefront module."""
import sys
import ctypes

import pyglet
from pyglet.gl import *

from shipfactory import ShipFactory

class Window(pyglet.window.Window):

    def __init__(self, ship):
        super().__init__(width=1280, height=720)
        self.rotation = 0
        self.lightfv = ctypes.c_float * 4
        self.ship = ship
        self.controller_values = {'x': 0, 'y': 0, 'z': 0}
        pyglet.clock.schedule(self.update)

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

        glTranslated(0, 0, -13)
        glEnable(GL_LIGHTING)

        self.ship.draw()

    def update(self, dt):
        self.ship.pitch += self.controller_values['y']
        self.ship.yaw += self.controller_values['x']
        self.ship.roll += self.controller_values['z']

    def on_joyaxis_motion(self, joystick, axis, value):
        self.controller_values[axis] = value

    def on_joybutton_press(self, joystick, button):
        print(button)

if __name__ == '__main__':
    sf = ShipFactory()
    ship = sf.manufacture("default")
    window = Window(ship)
    joystick = pyglet.input.get_joysticks()[1]
    joystick.open()
    joystick.push_handlers(window)
    pyglet.app.run()

