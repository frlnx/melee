from .base import BaseMenu, BaseButton
from typing import Callable
from engine.models.ship import ShipModel
from .grid import GridItemValueSetter, ValueKeepingGridItem


class ControlConfigMenu(BaseMenu):

    def __init__(self, heading: str, buttons, x, y, grid_item_presenter):
        super().__init__(heading, buttons, x, y)
        self.grid_item_presenter = grid_item_presenter

    @classmethod
    def manufacture_for_ship_model(cls, ship_model: ShipModel, close_menu_function: Callable, x, y,
                                   mesh_factory, font_size=36):
        grid_item_presenter = GridItemValueSetter.from_model(640, 300, ship_model, mesh_factory)

        heading = "Configure controls"
        callables = [("<- Back", close_menu_function), ("Save", grid_item_presenter.save_all)]
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

        return cls(heading, buttons, x, y, grid_item_presenter)

    def draw(self):
        super(ControlConfigMenu, self).draw()
        self.grid_item_presenter.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        super(ControlConfigMenu, self).on_mouse_press(x, y, button, modifiers)
        self.grid_item_presenter.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol, modifiers):
        self.grid_item_presenter.on_key_press(symbol, modifiers)

    def on_joybutton_press(self, joystick, button):
        self.grid_item_presenter.on_joybutton_press(joystick, button)

    def on_joyaxis_motion(self, joystick, axis, value):
        if abs(value) > 0.9:
            self.grid_item_presenter.on_joyaxis_motion(joystick, axis, value)
