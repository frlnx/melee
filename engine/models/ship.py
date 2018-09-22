from typing import Set, List

from engine.models import BaseModel
from engine.models.composite_model import CompositeModel
from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableDegrees, MutableForce


class ShipModel(CompositeModel):
    def __init__(self, ship_id, parts: Set[ShipPartModel], position: MutableOffsets,
                 rotation: MutableDegrees, movement: MutableOffsets, spin: MutableDegrees,
                 acceleration: MutableOffsets, torque: MutableDegrees, center_of_mass: MutableOffsets):
        super().__init__(parts, position, rotation, movement, spin, acceleration, torque, center_of_mass)
        self.ship_id = ship_id
        self._targets: List[BaseModel] = []
        self._current_target_index = 0
        self._fuel_parts = set()
        self._max_fuel = sum([part.max_fuel_stored for part in self._fuel_parts])

    def add_target(self, target: BaseModel):
        if target not in self._targets:
            self._targets.append(target)

    def remove_target(self, target: BaseModel):
        try:
            self._targets.remove(target)
        except ValueError:
            pass

    def cycle_next_target(self):
        self._current_target_index += 1
        self._current_target_index %= len(self._targets)

    def cycle_previous_target(self):
        self._current_target_index -= 1
        self._current_target_index %= len(self._targets)

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
        state['_valid_targets'] = []
        state['_target'] = self.target and self.target.uuid or None
        return state

    @property
    def target(self) -> "BaseModel":
        try:
            return self._targets[self._current_target_index]
        except IndexError:
            return self

    @property
    def fuel_percentage(self):
        return sum(part.fuel_stored for part in self._fuel_parts if part.fuel_stored) / self._max_fuel

    def copy(self):
        center_of_mass = self._center_of_mass.__copy__()
        parts = [part.copy(center_of_mass=center_of_mass) for part in self.parts]
        return self.__class__(self.ship_id, parts,
                              position=self.position.__copy__(), rotation=self.rotation.__copy__(),
                              movement=self.movement.__copy__(), spin=self.spin.__copy__(),
                              acceleration=self.acceleration.__copy__(), torque=self.torque.__copy__(),
                              center_of_mass=center_of_mass)
