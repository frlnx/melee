from pyglet.input import get_joysticks
from pyglet.window import key


class InputHandler(object):

    def __init__(self):
        self.axis = {'x': 0, 'y': 0, 'z': 0, 'rz': 0, '-x': 0, '-y': 0, '-z': 0, '-rz': 0}
        self.buttons = set()


class Keyboard(InputHandler):

    def __init__(self, window):
        super(Keyboard, self).__init__()
        window.push_handlers(self)

    def on_key_press(self, symbol, modifiers):
        key_name = key._key_names[symbol]
        self.buttons.add(key_name)

    def on_key_release(self, symbol, modifiers):
        key_name = key._key_names[symbol]
        try:
            self.buttons.remove(key_name)
        except KeyError:
            pass

    def push_handlers(self, target):
        pass

    def remove_handlers(self, target):
        pass


class GamePad(InputHandler):

    def __init__(self, joystick_id):
        super().__init__()
        joystick = get_joysticks()[joystick_id]
        joystick.open()
        joystick.push_handlers(self)
        self.joystick = joystick

    def push_handlers(self, target):
        self.joystick.push_handlers(target)

    def remove_handlers(self, target):
        self.joystick.remove_handlers(target)

    def on_joyaxis_motion(self, joystick, axis, value):
        negative_axis = "-{}".format(axis)
        if value < 0:
            self.axis[negative_axis] = value ** 2
            self.axis[axis] = 0
        elif value > 0:
            self.axis[axis] = value ** 2
            self.axis[negative_axis] = 0
        elif value == 0:
            self.axis[axis] = 0
            self.axis[negative_axis] = 0

    def on_joybutton_press(self, joystick, button):
        self.buttons.add(button)

    def on_joybutton_release(self, joystick, button):
        try:
            self.buttons.remove(button)
        except KeyError:
            pass
