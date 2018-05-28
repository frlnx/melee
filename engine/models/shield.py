from typing import Callable

from engine.models.ship_part import ShipPartModel
from engine.physics.polygon import TemporalPolygon


class ShieldModel(object):

    def __init__(self, generated_from: ShipPartModel, bounding_box: TemporalPolygon):
        self._bounding_box = bounding_box
        self.generated_from = generated_from
        generated_from.observe(self.update_position)
        self._charge = 0
        self._max_charge = 1000
        self._observers = set()

    def observe(self, func: Callable):
        self._observers.add(func)

    def _callback(self):
        for observer in self._observers:
            observer()

    def unobserve(self, func: Callable):
        try:
            self._observers.remove(func)
        except KeyError:
            pass

    def update_position(self):
        self._bounding_box.set_position_rotation(self.generated_from.x, self.generated_from.z,
                                                 -self.generated_from.yaw)

    def update(self):
        self._bounding_box.enable_percent_lines(self._max_charge / self._charge)
        self._callback()

    def power_up(self, amount):
        self._charge += amount
        self._charge = min(self._charge, self._max_charge)
        if amount > 0:
            self.update()

    def discharge(self, amount):
        self._charge -= amount
        self._charge = max(self._charge, 0)
        if amount > 0:
            self.update()

    @property
    def bounding_box(self):
        return self._bounding_box
