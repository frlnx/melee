from math import copysign
from pyglet.input import get_joysticks


class GamePad(object):

    def __init__(self):
        self.axis = {'x': 0, 'y': 0, 'z': 0, 'rz': 0, '-x': 0, '-y': 0, '-z': 0, '-rz': 0}
        self.buttons = set()
        joystick = get_joysticks()[1]
        joystick.open()
        joystick.push_handlers(self)

    def on_joyaxis_motion(self, joystick, axis, value):
        negative_axis = "-{}".format(axis)
        if value == 0:
            self.axis[axis] = 0
            self.axis[negative_axis] = 0
        if value < 0:
            axis = negative_axis
            value = -value
        self.axis[axis] = value ** 2

    def on_joybutton_press(self, joystick, button):
        self.buttons.add(button)

    def on_joybutton_release(self, joystick, button):
        try:
            self.buttons.remove(button)
        except ValueError:
            pass