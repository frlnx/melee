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
        self._target: ShipModel = None
        self._valid_targets: Set[ShipModel] = set()
        self._fuel_parts = set()
        self._max_fuel = sum([part.max_fuel_stored for part in self._fuel_parts])

    def _add_part(self, part):
        super(ShipModel, self)._add_part(part)
        if hasattr(part, "fuel_stored"):
            self._fuel_parts.add(part)

    def set_ship_id(self, identification):
        self.ship_id = identification

    def apply_global_force(self, force: 'MutableForce'):
        super(ShipModel, self).apply_global_force(force)

    def set_target(self, target: "ShipModel"):
        self._target = target
        self._callback("target")

    def __getstate__(self):
        state = super(ShipModel, self).__getstate__()
        state['_valid_targets'] = set()
        state['_target'] = self.target and self.target.uuid or None
        return state

    @property
    def target(self) -> "ShipModel":
        return self._target or self

    @property
    def fuel_percentage(self):
        return sum(part.fuel_stored for part in self._fuel_parts if part.fuel_stored) / self._max_fuel

    def copy(self):
        parts = [part.copy() for part in self.parts]
        return self.__class__(self.ship_id, parts,
                              position=self.position.__copy__(), rotation=self.rotation.__copy__(),
                              movement=self.movement.__copy__(), spin=self.spin.__copy__(),
                              acceleration=self.acceleration.__copy__(), torque=self.torque.__copy__())
