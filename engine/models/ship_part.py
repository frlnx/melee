from math import radians, cos, atan2, degrees
from typing import Set

from engine.models.base_model import BaseModel
from engine.physics.force import MutableOffsets, MutableDegrees


class ShipPartModel(BaseModel):

    def __init__(self, name, position: MutableOffsets, rotation: MutableDegrees,
                 movement: MutableOffsets, spin: MutableDegrees,
                 acceleration: MutableOffsets, torque: MutableDegrees, bounding_box, **part_spec):
        super().__init__(position, rotation, movement, spin, acceleration, torque, bounding_box)
        self._name = name
        self._states: dict = part_spec['states']
        self.button = part_spec.get('button')
        self.keyboard = part_spec.get('keyboard')
        self.mouse = part_spec.get('mouse', [])
        self.axis = part_spec.get('axis')
        self._state = "idle"
        self._mesh_name = part_spec.get('mesh_name')
        self.material_affected = part_spec.get('material_affected')
        self.material_mode = part_spec.get('material_mode')
        self.material_channels = part_spec.get('material_channels')
        self.max_fuel_stored = part_spec.get('fuel storage')
        self._fuel_stored = part_spec.get('fuel storage')
        self.needs_connection_to: set = part_spec['needs_connection_to']
        self.material_value = 0
        self.input_value = 0
        self._spawn = None
        self._time_in_state = 0
        self._connected_parts = set()
        self._working = False
        self.update_working_status()
        self.full_torque = self._full_torque()

    @property
    def fuel_stored(self):
        return self._fuel_stored

    @property
    def working(self):
        return self._working

    def update_working_status(self):
        working = self.needs_fulfilled and self.is_alive and not self.is_exploding and self.fuel_stored != 0
        updated = self._working != working
        self._working = working
        if updated:
            self._callback("working")

    @property
    def _connected_fuel_tanks(self):
        return [part for part in self.connected_parts if part.fuel_stored]

    def _consume_fuel(self, amount):
        fuel_tanks = self._connected_fuel_tanks
        n_fuel_tanks = len(fuel_tanks)
        amount_per_tank = amount / n_fuel_tanks
        for fuel_tank in fuel_tanks:
            fuel_tank.drain_fuel(amount_per_tank)

    def drain_fuel(self, amount):
        if self._fuel_stored is None:
            raise AttributeError(f"No fuel stored in a {self.name}")
        self._fuel_stored -= amount
        self._fuel_stored = max(0, self._fuel_stored)
        if self._fuel_stored == 0:
            self.update_working_status()

    @property
    def needs_fulfilled(self):
        names_of_connected_parts = set([part.name for part in self.connected_parts if part.working])
        return len(self.needs_connection_to & names_of_connected_parts) == len(self.needs_connection_to)

    def connect(self, other_part: "ShipPartModel"):
        self._connect(other_part)
        other_part._connect(self)

    def _connect(self, other_part: "ShipPartModel"):
        if other_part in self.connected_parts:
            return
        self._connected_parts.add(other_part)
        if other_part.name in self.needs_connection_to:
            other_part.observe(self.update_working_status, "working")
            other_part.observe(self.update_working_status, "explode")
            other_part.observe(self.update_working_status, "alive")
        self.update_working_status()

    def disconnect(self, other_part: "ShipPartModel"):
        self._disconnect(other_part)
        other_part._disconnect(self)

    def _disconnect(self, other_part: "ShipPartModel"):
        try:
            self._connected_parts.remove(other_part)
        except KeyError:
            pass
        else:
            if other_part.name in self.needs_connection_to:
                other_part.unobserve(self.update_working_status, "working")
                other_part.unobserve(self.update_working_status, "explode")
                other_part.unobserve(self.update_working_status, "alive")
            self.update_working_status()

    def disconnect_all(self):
        for connected_part in self.connected_parts:
            connected_part._disconnect(self)
            for signal in ["working", "explode", "alive"]:
                self.unobserve(connected_part.update_working_status, signal)
        self.connected_parts.clear()
        self.update_working_status()

    @property
    def connected_parts(self) -> Set["ShipPartModel"]:
        return self._connected_parts

    def set_controls(self, button=None, keyboard=None, axis=None):
        self.button = button
        self.keyboard = keyboard
        self.axis = axis

    def set_input_value(self, value):
        self.input_value = self.working and value or 0
        thrust = self.input_value * self.state_spec.get('thrust generated', 0)
        torque_yaw = self.full_torque * thrust
        self.set_local_acceleration(0, 0, -thrust)
        self.set_torque(0, torque_yaw, 0)
        self.set_material_value(value)

    def run(self, dt):
        fuel_consumption = self.state_spec.get('fuel consumption')
        if fuel_consumption and self.input_value > 0 and self.working:
            fuel_consumed = fuel_consumption * self.input_value
            self._consume_fuel(fuel_consumed)

    def timers(self, dt):
        super().timers(dt)
        if 'timeout' in self.state_spec:
            self._time_in_state += dt
            self.set_material_value(self._time_in_state / self.state_spec['timeout'])
        if 'material_value' in self.state_spec:
            self.set_material_value(self.state_spec['material_value'])

    def set_spawn(self, projectile):
        self._spawn = projectile

    def pop_spawn(self):
        spawn = self.spawn
        self._spawn = None
        return spawn

    @property
    def spawn(self):
        return self._spawn

    def set_state(self, state):
        self._state = state
        self._time_in_state = 0

    def state_transition_possible_to(self, state):
        if self.state_timeout > 0:
            return False
        spec = self._states.get(state, {})
        return self.state == spec.get('required state', self.state)

    @property
    def state_timeout(self):
        return max(0, self.state_spec.get('timeout', 0) - self._time_in_state)

    @property
    def state_spec(self):
        return self._states.get(self._state)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def __repr__(self):
        return "{} @{}".format(self.name, self.position.xyz)

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

    def damage(self):
        super(ShipPartModel, self).damage()
        self.explode()

    def explode(self):
        super(ShipPartModel, self).explode()
        self.disconnect_all()

    def copy(self):
        return self.__class__(name=self.name, position=self.position.__copy__(), rotation=self.rotation.__copy__(),
                              movement=self.movement.__copy__(), spin=self.spin.__copy__(),
                              acceleration=self.acceleration.__copy__(), torque=self.torque.__copy__(),
                              bounding_box=self.bounding_box.__copy__(), states=self._states.copy(),
                              keyboard=self.keyboard, mouse=self.mouse.copy(), axis=self.axis, button=self.button,
                              needs_connection_to=self.needs_connection_to.copy(), mesh_name=self.mesh_name,
                              material_affected=self.material_affected, material_channels=self.material_channels,
                              material_mode=self.material_mode)
