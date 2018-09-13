from math import radians, cos, atan2, degrees

from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableDegrees
from .fuel_tank import FuelTankModel


class ThrusterModel(ShipPartModel):

    def __init__(self, name, position: MutableOffsets, rotation: MutableDegrees, movement: MutableOffsets,
                 spin: MutableDegrees, acceleration: MutableOffsets, torque: MutableDegrees, bounding_box, **part_spec):

        super().__init__(name, position, rotation, movement, spin, acceleration, torque, bounding_box, **part_spec)
        self.full_torque = self._full_torque()

    @property
    def _connected_fuel_tanks(self) -> list:
        return [part for part in self.connected_parts if isinstance(part, FuelTankModel) and part.working]

    def _consume_fuel(self, amount):
        fuel_tanks = self._connected_fuel_tanks
        n_fuel_tanks = len(fuel_tanks)
        amount_per_tank = amount / n_fuel_tanks
        for fuel_tank in fuel_tanks:
            fuel_tank.drain_fuel(amount_per_tank)

    def set_input_value(self, value):
        super(ThrusterModel, self).set_input_value(value)
        thrust = self.input_value * self.state_spec.get('thrust generated', 0)
        torque_yaw = self.full_torque * thrust
        self.set_local_acceleration(0, 0, -thrust)
        self.set_torque(0, torque_yaw, 0)

    def run(self, dt):
        super(ThrusterModel, self).run(dt)
        fuel_consumption = self.state_spec.get('fuel consumption')
        if fuel_consumption and self.input_value > 0 and self.working:
            fuel_consumed = fuel_consumption * self.input_value
            self._consume_fuel(fuel_consumed)

    def update(self):
        super(ShipPartModel, self).update()
        self.full_torque = self._full_torque()

    @property
    def diff_yaw_of_force_to_pos(self):
        return (((self.rotation.yaw % 360) - (self.position.direction.yaw % 360) + 180) % 360) - 180

    @property
    def radians_force_is_lateral_to_position(self):
        return radians(self.diff_yaw_of_force_to_pos - 90)

    def _full_torque(self):
        amount_of_force_that_rotates = cos(self.radians_force_is_lateral_to_position)
        full_torque_radians = atan2(amount_of_force_that_rotates, self.position.distance)
        return degrees(full_torque_radians)
