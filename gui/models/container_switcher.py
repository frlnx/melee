from typing import List

from .container import ComponentContainerModel
from .drag_and_drop import DragAndDropContainer


class ContainerSwitcherModel(ComponentContainerModel, DragAndDropContainer):

    components: List[DragAndDropContainer]

    def __init__(self, components: List[DragAndDropContainer]):
        super().__init__(components)

    def move(self, x, y, dx, dy):
        ox, oy = self._held_item.x, self._held_item.y
        before_move_component = self.component_at(ox, oy)
        super(ContainerSwitcherModel, self).move(x, y, dx, dy)
        after_move_component = self.component_at(x, y)
        if before_move_component != after_move_component:
            before_move_component.remove_item(self._held_item)
            after_move_component.add_item(self._held_item)
