from typing import Tuple

from engine.models.base_model import BaseModel

class ShipPartModel(BaseModel):

    def __init__(self, name, position: Tuple[float, float, float], rotation: Tuple[float, float, float],
                 movement: Tuple[float, float, float], spin: Tuple[float, float, float], **part_spec):
        super().__init__(position, rotation, movement, spin)
        self._name = name
        self._states = {t['name']: t for t in part_spec.get('triggers', [{"name": "idle"}])}
        self.button = part_spec.get('button')
        self.axis = part_spec.get('axis')
        self._state = "idle"

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
