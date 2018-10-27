from pyglet.window import key, mouse


class InputInterface:
    __abstract__ = True

    key = key
    mouse = mouse

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        pass

    def on_key_release(self, symbol, modifiers):
        pass

    def on_joyaxis_motion(self, joystick, axis, value):
        pass

    def on_joybutton_press(self, joystick, button):
        pass

    def on_joybutton_release(self, joystick, button):
        pass

    def on_joyhat_motion(self, hat_x, hat_y, joystick):
        pass
