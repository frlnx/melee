from engine.models.base_model import BaseModel
from engine.physics.force import MutableOffsets, MutableDegrees


class ShipPartModel(BaseModel):

    def __init__(self, name, position: MutableOffsets, rotation: MutableDegrees,
                 movement: MutableOffsets, spin: MutableDegrees, bounding_box, **part_spec):
        super().__init__(position, rotation, movement, spin, bounding_box)
        self._name = name
        self._states = {t['name']: t for t in part_spec.get('states', [{"name": "idle"}])}
        self.button = part_spec.get('button')
        self.keyboard = part_spec.get('keyboard')
        self.axis = part_spec.get('axis')
        self._state = "idle"
        self._mesh_name = part_spec.get('mesh_name')
        self.nickname = part_spec.get('nickname')
        self.material_affected = part_spec.get('material_affected')
        self.material_mode = part_spec.get('material_mode')
        self.material_channel = part_spec.get('material_channels')
        self.material_value = 0
        self.input_value = 0
        self._spawn = None
        self._time_in_state = 0
        self._material_observers = set()
        self._connected_parts = set()

    def connect(self, other_part: "ShipPartModel"):
        self._connected_parts.add(other_part)
        other_part._connected_parts.add(self)

    def disconnect(self, other_part: "ShipPartModel"):
        try:
            self._connected_parts.remove(other_part)
            other_part._connected_parts.remove(self)
        except AttributeError:
            pass

    @property
    def connected_parts(self):
        return self._connected_parts

    def __getstate__(self):
        d = super(ShipPartModel, self).__getstate__()
        d['_material_observers'] = set()
        return d

    def set_controls(self, button=None, keyboard=None, axis=None):
        self.button = button
        self.keyboard = keyboard
        self.axis = axis

    def set_input_value(self, value):
        self.set_material_value(value)
        self.input_value = value

    def timers(self, dt):
        super().timers(dt)
        if 'timeout' in self.state_spec:
            self._time_in_state += dt
            self.set_material_value(self._time_in_state / self.state_spec['timeout'])
        if 'material_value' in self.state_spec:
            self.set_material_value(self.state_spec['material_value'])

    def set_material_value(self, value):
        self.material_value = value
        self._material_callback()

    def _material_callback(self):
        for callback in self._material_observers:
            callback()

    def observe_material(self, callback):
        self._material_observers.add(callback)

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
