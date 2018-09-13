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
        self._connectability = part_spec.get('connectability', set())
        self.connection_configs = {config['name']: config for config in self._connectability}
        self.needs_connection_to: set = {c['name'] for c in self._connectability if c.get('required')}
        self.material_value = 0
        self.input_value = 0
        self._spawn = None
        self._time_in_state = 0
        self._connected_parts = set()
        self._working = False
        self.update_working_status()

    def set_input_value(self, value):
        self.input_value = self.working and value or 0
        self.set_material_value(self.input_value)

    @property
    def working(self):
        return self._working

    def update_working_status(self):
        actual_working = self._check_working()
        updated = self._working != actual_working
        self._working = actual_working
        if updated:
            self._callback("working")

    def _check_working(self):
        return self.needs_fulfilled and self.is_alive and not self.is_exploding and self.has_route_to_cockpit

    @property
    def has_route_to_cockpit(self):
        checked = set()
        queue = set(self.connected_parts)
        queue.add(self)
        while queue:
            new_parts = set()
            for part in queue:
                if part.name == 'cockpit':
                    return True
                new_parts |= set(part.connected_parts)
            checked |= queue
            queue.clear()
            new_parts -= checked
            queue = new_parts
        return False

    @property
    def needs_fulfilled(self):
        return self.missing_connections == set()

    @property
    def missing_connections(self):
        names_of_connected_parts = set(part.name for part in self.connected_parts if part.working)
        return (self.needs_connection_to & names_of_connected_parts) - self.needs_connection_to

    def can_connect_to(self, other_part: "ShipPartModel"):
        return self._can_connect_to(other_part) and other_part._can_connect_to(self)

    def _can_connect_to(self, other_part: "ShipPartModel"):
        distance = self._local_distance_to(other_part)
        config = self.connection_configs.get(other_part.name, {})
        if distance <= config.get('distance', 1.7):
            return config.get('can_connect', True)
        return False

    def _local_distance_to(self, other_part: "ShipPartModel"):
        distance = (self.position - other_part.position).distance
        return distance

    def connect(self, other_part: "ShipPartModel"):
        self._connect(other_part)
        other_part._connect(self)

    def _connect(self, other_part: "ShipPartModel"):
        if other_part in self.connected_parts:
            return
        self._connected_parts.add(other_part)
        self._callback("connection")
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
            self._callback("disconnect")
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

    def run(self, dt):
        #super().run(dt)
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

    def damage(self):
        super(ShipPartModel, self).damage()
        self.explode()

    def explode(self):
        super(ShipPartModel, self).explode()
        self.disconnect_all()

    def copy(self) -> "ShipPartModel":
        return self.__class__(name=self.name, position=self.position.__copy__(), rotation=self.rotation.__copy__(),
                              movement=self.movement.__copy__(), spin=self.spin.__copy__(),
                              acceleration=self.acceleration.__copy__(), torque=self.torque.__copy__(),
                              bounding_box=self.bounding_box.__copy__(), states=self._states.copy(),
                              keyboard=self.keyboard, mouse=self.mouse.copy(), axis=self.axis, button=self.button,
                              connectability=self._connectability.copy(), mesh_name=self.mesh_name,
                              material_affected=self.material_affected, material_channels=self.material_channels,
                              material_mode=self.material_mode)
