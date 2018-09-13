from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableDegrees
from .fuel_tank import FuelTankModel


class GeneratorModel(ShipPartModel):

    def __init__(self, name, position: MutableOffsets, rotation: MutableDegrees, movement: MutableOffsets,
                 spin: MutableDegrees, acceleration: MutableOffsets, torque: MutableDegrees, bounding_box, **part_spec):
        super().__init__(name, position, rotation, movement, spin, acceleration, torque, bounding_box, **part_spec)
        self._generation_level = 0

    @property
    def _connected_fuel_tanks(self) -> list:
        return [part for part in self.connected_parts if isinstance(part, FuelTankModel) and part.working]

    def _consume_fuel(self, amount):
        fuel_tanks = self._connected_fuel_tanks
        n_fuel_tanks = len(fuel_tanks)
        amount_per_tank = amount / n_fuel_tanks
        for fuel_tank in fuel_tanks:
            fuel_tank.drain_fuel(amount_per_tank)

    @property
    def max_power_output(self):
        return self.working and self.state_spec['power generation'] or 0

    def set_generation_level(self, percent):
        self._generation_level = percent

    def run(self, dt):
        super(GeneratorModel, self).run(dt)
        if self.working:
            fuel_required = self.state_spec['fuel consumption'] * self.generation_level
            self._consume_fuel(fuel_required)

    @property
    def generation_level(self):
        return self.working and self._generation_level or 0
