from typing import List, Callable

from pyglet.window import mouse
from pyglet.window.key import MOD_CTRL

from engine.models import ShipModel
from engine.models.factories import ShipPartModelFactory
from engine.views.menus.base import BaseMenu, BaseButton
from engine.views.ship_parts.factories import PartStoreViewFactory, DrydockViewFactory
from .button_container import ButtonContainer
from .drydock import Drydock, PartStore, DockableItem, ShipBuildMenuComponent
from .model_inspection import ModelInspectionMenuComponent


class ShipBuildMenu(BaseMenu):

    ship_part_model_factory = ShipPartModelFactory()

    def __init__(self, heading: str, buttons: List[BaseButton], x, y, drydock: Drydock, part_store: PartStore,
                 part_inspection: ModelInspectionMenuComponent):
        super().__init__(heading, buttons, x, y)
        self.components: List[ShipBuildMenuComponent] = [drydock, part_store, part_inspection]
        self._held_item: DockableItem = None

    @classmethod
    def manufacture_for_ship_model(cls, ship_model: ShipModel, close_menu_function: Callable,
                                   x, y, font_size=36, screen_width=1280, screen_height=720):
        vertical_ruler = screen_width - 100
        drydock = Drydock(400, vertical_ruler, 0, screen_height, ship_model, DrydockViewFactory())
        part_store = PartStore(vertical_ruler, screen_width, 0, screen_height, PartStoreViewFactory())
        part_inspection = ModelInspectionMenuComponent(0, 400, 0, 400, ship_model)

        drydock.observe(part_inspection.set_model, "highlight")
        part_store.observe(part_inspection.set_model, "highlight")

        heading = "Shipyard"
        callables = [("<- Back", close_menu_function), ("Save", drydock.save_all), ("Reset", drydock.reset),
                     ("Debug", drydock.debug)]
        callables = [close_menu_function, drydock.save_all, drydock.reset, drydock.debug]
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
        buttons = ButtonContainer.labeled_menu_from_function_names(heading, callables, x, y, font_size)

        return cls(heading, buttons, x, y, drydock, part_store, part_inspection)

    def _component_at(self, x, y):
        for component in self.components:
            if component.in_area(x, y):
                return component

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        component = self._component_at(x, y)
        if component:
            if buttons & mouse.RIGHT:
                component.translate(dx, dy)
            if buttons & mouse.LEFT:
                if not self._held_item:
                    self._held_item = component.grab(x, y)
                else:
                    snap = modifiers & MOD_CTRL
                    component.drag(self._held_item, x, y, snap=snap)

    def on_mouse_release(self, x, y, button, modifiers):
        component = self._component_at(x, y)
        if component:
            component.drop(self._held_item)
            self._held_item = None

    def on_mouse_motion(self, x, y, dx, dy):
        super(ShipBuildMenu, self).on_mouse_motion(x, y, dx, dy)
        component = self._component_at(x, y)
        if component:
            if not self._held_item:
                component.highlight_at(x, y)

    def draw(self):
        super(ShipBuildMenu, self).draw()
        for component in self.components:
            component.draw()
