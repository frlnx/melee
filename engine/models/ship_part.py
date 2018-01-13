from engine.models.base_model import BaseModel
from engine.physics.force import MutableOffsets, MutableDegrees


class ShipPartModel(BaseModel):

    def __init__(self, name, position: MutableOffsets, rotation: MutableDegrees,
                 movement: MutableOffsets, spin: MutableDegrees, bounding_box, **part_spec):
        super().__init__(position, rotation, movement, spin, bounding_box)
        self._name = name
        self._states = {t['name']: t for t in part_spec.get('states', [{"name": "idle"}])}
        self.button = part_spec.get('button')
        self.axis = part_spec.get('axis')
        self._state = "idle"
        self._mesh = part_spec.get('mesh')
        self.nickname = part_spec.get('nickname')
        self.target_indicator = part_spec.get('target_indicator', False)
        self.texture_offset = [0, 0, 0]
        self.texture_rotation = [0, 0, 0]
        self._spawn = None

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
        assert state in self._states
        self._state = state

    @property
    def state_spec(self):
        return self._states.get(self._state)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self.state
