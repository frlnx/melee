from typing import Set

from engine.models.ship_part import ShipPartModel
from engine.models.base_model import BaseModel
from engine.physics.force import MutableOffsets, MutableDegrees


class ShipModel(BaseModel):
    def __init__(self, parts: Set[ShipPartModel], position: MutableOffsets,
                 rotation: MutableDegrees, movement: MutableOffsets, spin: MutableDegrees):
        super().__init__(position, rotation, movement, spin)
        self.parts = parts
        self._target_position = self.position
        self._target_rotation = self.rotation
        for part in self.parts:
            if part.position[1] == 0:
                self._bounding_box = self._bounding_box + part.bounding_box
        self._mass = sum([part.mass for part in self.parts])
        bb_width = (self._bounding_box.right - self._bounding_box.left)
        bb_height = (self._bounding_box.top - self._bounding_box.bottom)
        self._inertia = self._mass / 12 * (bb_width ** 2 + bb_height ** 2)

    def set_target_position_rotation(self, position: MutableOffsets, rotation: MutableDegrees):
        self._target_position = position
        self._target_rotation = rotation

    def set_target_position(self, position: MutableOffsets):
        self._target_position = position

    @property
    def target_pos(self):
        return self._target_position

    @property
    def has_target(self):
        return self._target_position is not None
