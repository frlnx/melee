from typing import List, Callable
from engine.views.menus.base import BaseMenu, BaseButton
from engine.models.factories import ShipPartModelFactory
from .drydock import Drydock


class ShipBuildMenu(BaseMenu):

    ship_part_model_factory = ShipPartModelFactory()

    def __init__(self, heading: str, buttons: List[BaseButton], x, y, drydock: Drydock):
        super().__init__(heading, buttons, x, y)
        self.drydock = drydock

    @classmethod
    def manufacture_for_ship_model(cls, ship_model, close_menu_function: Callable, x, y, mesh_factory, font_size=36):
        drydock = Drydock(ship_model, mesh_factory)
        heading = "Shipyard"
        callables = [("<- Back", close_menu_function), ("Save", drydock.save_all),
                     ("Debug", drydock.debug), ("Reset", drydock.reset)]
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

        return cls(heading, buttons, x, y, drydock)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.drydock.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.drydock.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        super(ShipBuildMenu, self).on_mouse_motion(x, y, dx, dy)
        self.drydock.on_mouse_motion(x, y, dx, dy)

    def draw(self):
        super(ShipBuildMenu, self).draw()
        self.drydock.draw()
