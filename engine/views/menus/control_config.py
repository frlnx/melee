from functools import partial
from typing import Callable, List

from pyglet.window import mouse

from engine.models.ship import ShipModel
from .base import BaseMenu, BaseButton
from .drydock import ControlConfiguration


class ControlConfigMenu(BaseMenu):

    def __init__(self, heading: str, buttons, x, y, control_config: ControlConfiguration):
        super().__init__(heading, buttons, x, y)
        self.control_config = control_config
        self.components: List[ControlConfiguration] = [control_config]

    @classmethod
    def manufacture_for_ship_model(cls, ship_model: ShipModel, close_menu_function: Callable, x, y,
                                   view_factory, font_size=36, screen_width=1280, screen_height=720):
        left = 0
        right = screen_width
        bottom = 0
        top = screen_height
        control_config = ControlConfiguration(left, right, bottom, top, ship=ship_model, view_factory=view_factory)

        heading = "Configure controls"
        callables = [("<- Back", close_menu_function),
                     ("Keyboard", partial(control_config.set_mode, "keyboard")),
                     ("Gamepad", partial(control_config.set_mode, "gamepad")),
                     ("Reset", control_config.reset),
                     ("Save", control_config.save_all)]
        height = int(font_size * 1.6)
        width = int(height * 6)
        height_spacing = int(height * 1.1)
        buttons = []
        for i, (name, func) in enumerate(callables):
            i += 1
            button = BaseButton.labeled_button(name, font_size=font_size, left=x, right=x + width,
                                               bottom=y - height_spacing * i, top=y - height_spacing * i + height,
                                               func=func)
            buttons.append(button)

        return cls(heading, buttons, x, y, control_config)

    def _component_at(self, x, y):
        for component in self.components:
            if component.in_area(x, y):
                return component

    def draw(self):
        super(ControlConfigMenu, self).draw()
        self.control_config.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        super(ControlConfigMenu, self).on_mouse_motion(x, y, dx, dy)
        self.control_config.highlight_at(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        super(ControlConfigMenu, self).on_mouse_press(x, y, button, modifiers)
        self.control_config.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.control_config.on_mouse_release(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        component = self._component_at(x, y)
        if component:
            if buttons & mouse.RIGHT:
                component.translate(dx, dy)
            if buttons & mouse.LEFT:
                self.control_config.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_key_press(self, symbol, modifiers):
        self.control_config.on_key_press(symbol, modifiers)

    def on_joybutton_press(self, joystick, button):
        self.control_config.on_joybutton_press(joystick, button)

    def on_joyaxis_motion(self, joystick, axis, value):
        if abs(value) > 0.9:
            self.control_config.on_joyaxis_motion(joystick, axis, value)
