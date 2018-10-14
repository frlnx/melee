from typing import Set

from engine.models.observable import Observable
from engine.physics.polygon import ClosedPolygon
from .component import MenuComponentModel


class DragAndDropItem(Observable):

    def __init__(self, x, y, degrees, polygon: ClosedPolygon):
        Observable.__init__(self)
        self._polygon = polygon
        self._x, self._y = x, y
        self._degrees = degrees

    def contains(self, x, y):
        return self._polygon.point_inside(x, y)

    def set_position(self, x, y):
        self._x, self._y = x, y
        self._update_position()

    def move_by(self, dx, dy):
        self._x += dx
        self._y += dy
        self._update_position()

    def _update_position(self):
        self._polygon.set_position_rotation(self._x, self._y, self._polygon.rotation)
        self._callback('move')

    def set_angle(self, degrees):
        self._degrees = degrees
        self._polygon.set_position_rotation(self._polygon.x, self._polygon.y, degrees)
        self._callback('move')


class DragAndDropContainer(MenuComponentModel):

    def __init__(self, left, right, bottom, top, items: Set[DragAndDropItem]):
        super().__init__(left, right, bottom, top)
        self._items = items
        self._held_item = None

    def item_at(self, x, y):
        for item in self._items:
            if item.contains(x, y):
                return item

    def grab_at(self, x, y):
        if not self._held_item:
            grabbed_item = self.item_at(x, y)
            if grabbed_item:
                self._held_item = grabbed_item

    def drag(self, x, y, dx, dy):
        self.grab_at(x, y)
        self.move(x, y, dx, dy)

    def drop(self, x, y):
        if self._held_item:
            self._held_item = None

    def move(self, x, y, dx, dy):
        if self._held_item:
            self._held_item.move_by(dx, dy)

    def add_item(self, item: DragAndDropItem):
        self._items.add(item)

    def remove_item(self, item: DragAndDropItem):
        self._items.remove(item)
