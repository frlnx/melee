from typing import Set, Tuple

from engine.models.ship_part import ShipPartModel
from engine.models.base_model import BaseModel


class ShipModel(BaseModel):
    def __init__(self, parts: Set[ShipPartModel], position: Tuple[float, float, float],
                 rotation: Tuple[float, float, float], movement: Tuple[float, float, float],
                 spin: Tuple[float, float, float]):
        super().__init__(position, rotation, movement, spin)
        self.parts = parts
        self._target_position = self.position
        self._target_rotation = self.rotation
        for part in self.parts:
            self._bounding_box = self._bounding_box + part.bounding_box

    @property
    def name(self):
        return "ship"

    def set_target_position_rotation(self, position, rotation):
        self._target_position = position
        self._target_rotation = rotation

    def set_target_position(self, position):
        self._target_position = position

    @property
    def target_pos(self):
        return self._target_position

    @property
    def has_target(self):
        return self._target_position is not None
