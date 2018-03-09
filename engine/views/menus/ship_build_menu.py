from typing import List, Callable
from engine.views.menus.base_menu import BaseMenu, BaseButton
from engine.views.menus.grid import GridItem, GridItemArranger


class ShipBuildMenu(BaseMenu):

    def __init__(self, heading: str, buttons: List[BaseButton], x, y, grid_item_arranger: GridItemArranger):
        super().__init__(heading, buttons, x, y)
        self.grid_item_arranger = grid_item_arranger

    @classmethod
    def manufacture_for_ship_model(cls, ship_model, close_menu_function:Callable, x, y, mesh_factory, font_size=36):
        items = {}
        for part in ship_model.parts:
            mesh = mesh_factory.manufacture(part.mesh)
            item = GridItem(part, mesh.draw)
            items[(part.x, part.z)] = item
        grid_item_arranger = GridItemArranger(x + 400, y - 400, items, 5, 5, 100)

        heading = "Configure ship"
        callables = [("<- Back", close_menu_function), ("Save", grid_item_arranger.save_all)]
        height = int(font_size * 1.6)
        width = int(height * 6)
        height_spacing = int(height * 1.1)
        buttons = []
        for i, (name, func) in enumerate(callables):
            i += 1
            button = BaseButton.labeled_button(name, font_size=font_size, left=x, right=x + width,
                                               bottom=y - height_spacing * i, top=y - height_spacing * i + height,
                                               function=func)
            buttons.append(button)

        return cls(heading, buttons, x, y, grid_item_arranger)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.grid_item_arranger.drag(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.grid_item_arranger.drop(x, y)

    def draw(self):
        super(ShipBuildMenu, self).draw()
        self.grid_item_arranger.draw()
