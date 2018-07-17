from typing import Set

from engine.models.composite_model import CompositeModel
from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableDegrees, MutableForce


class ShipModel(CompositeModel):
    def __init__(self, ship_id, parts: Set[ShipPartModel], position: MutableOffsets,
                 rotation: MutableDegrees, movement: MutableOffsets, spin: MutableDegrees,
                 acceleration: MutableOffsets, torque: MutableDegrees):
        super().__init__(parts, position, rotation, movement, spin, acceleration, torque)
        self.ship_id = ship_id
        self._target_position = self.position
        self._target_rotation = self.rotation
        self.shields = []
        self._fuel_parts = [part for part in parts if part.state_spec.get('fuel storage')]
        self._max_fuel = sum([part.state_spec.get('fuel storage', 0) for part in self._fuel_parts])

    def set_ship_id(self, identification):
        self.ship_id = identification

    def apply_global_force(self, force: 'MutableForce'):
        super(ShipModel, self).apply_global_force(force)

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

    @property
    def fuel_percentage(self):
        return 1.00

    def copy(self):
        parts = [part.copy() for part in self.parts]
        return self.__class__(self.ship_id, parts,
                              position=self.position.__copy__(), rotation=self.rotation.__copy__(),
                              movement=self.movement.__copy__(), spin=self.spin.__copy__(),
                              acceleration=self.acceleration.__copy__(), torque=self.torque.__copy__())
