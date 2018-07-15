from math import radians, cos, atan2, degrees

from engine.models.base_model import BaseModel
from engine.physics.force import MutableOffsets, MutableDegrees


class ShipPartModel(BaseModel):

    def __init__(self, name, position: MutableOffsets, rotation: MutableDegrees,
                 movement: MutableOffsets, spin: MutableDegrees,
                 acceleration: MutableOffsets, torque: MutableDegrees, bounding_box, **part_spec):
        super().__init__(position, rotation, movement, spin, acceleration, torque, bounding_box)
        self._name = name
        self._states = {t['name']: t for t in part_spec.get('states', [{"name": "idle"}])}
        self.button = part_spec.get('button')
        self.keyboard = part_spec.get('keyboard')
        self.mouse = part_spec.get('mouse', [])
        self.axis = part_spec.get('axis')
        self._state = "idle"
        self._mesh_name = part_spec.get('mesh_name')
        self.material_affected = part_spec.get('material_affected')
        self.material_mode = part_spec.get('material_mode')
        self.material_channel = part_spec.get('material_channels')
        self.needs_connection_to = set(part_spec.get('needs_connection_to', []))
        self.material_value = 0
        self.input_value = 0
        self._spawn = None
        self._time_in_state = 0
        self._connected_parts = set()
        self._working = False
        self.update_working_status()
        self.full_torque = self._full_torque()
        self._integrity = 100

    @property
    def integrity(self):
        return self._integrity

    @property
    def working(self):
        return self._working

    def update_working_status(self):
        working = self.needs_fullfilled and self.is_alive and not self.is_exploding
        updated = self._working != working
        self._working = working
        if updated:
            self._callback("working")

    @property
    def needs_fullfilled(self):
        names_of_connected_parts = set([part.name for part in self.connected_parts if part.working])
        return len(self.needs_connection_to & names_of_connected_parts) == len(self.needs_connection_to)

    def connect(self, other_part: "ShipPartModel"):
        self._connect(other_part)
        other_part._connect(self)

    def _connect(self, other_part: "ShipPartModel"):
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
            if other_part.name in self.needs_connection_to:
                other_part.unobserve(self.update_working_status, "working")
                other_part.unobserve(self.update_working_status, "explode")
                other_part.unobserve(self.update_working_status, "alive")
            self.update_working_status()
        except KeyError:
            pass

    def disconnect_all(self):
        for connected_part in self.connected_parts:
            connected_part.unobserve(self.update_working_status, "working")
            connected_part.unobserve(self.update_working_status, "explode")
            connected_part.unobserve(self.update_working_status, "alive")
        self.connected_parts.clear()
        self.update_working_status()

    @property
    def connected_parts(self):
        return self._connected_parts

    def set_controls(self, button=None, keyboard=None, axis=None):
        self.button = button
        self.keyboard = keyboard
        self.axis = axis

    def set_input_value(self, value):
        self.input_value = value
        thrust = self.input_value * self.state_spec.get('thrust generated', 0)
        torque_yaw = self.full_torque * thrust
        self.set_local_acceleration(0, 0, -thrust)
        self.set_torque(0, torque_yaw, 0)
        self.set_material_value(value)

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
