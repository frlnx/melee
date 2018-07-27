from typing import Callable

from engine.controllers.base_controller import BaseController
from engine.models.ship_part import ShipPartModel


class ShipPartController(BaseController):

    def __init__(self, model: ShipPartModel, gamepad: "InputHandler", spawn_func: Callable):
        super().__init__(model, gamepad)
        self._model = model
        self._spawn_func = spawn_func

    def update(self, dt):
        self._model.timers(dt)
        if self._gamepad:
            self.get_input()

    def get_input(self):
        if not self._model.working:
            self._model.set_input_value(0.)
            self._model.set_state("idle")
        else:
            input_value = (self._model.button in self._gamepad.buttons) + \
                          (self._model.keyboard in self._gamepad.buttons) + \
                          self._gamepad.axis.get(self._model.axis, 0.0)
            for axis in self._model.mouse:
                input_value += self._gamepad.axis.get(axis, 0.0)
            input_value = min(1.0, max(0., input_value))
            if 'next_state' in self._model.state_spec:
                new_state = self._model.state_spec.get('next state', self._model.state)
            elif input_value > 0:
                new_state = 'active'
            elif self._model.state_transition_possible_to('idle'):
                new_state = 'idle'
            else:
                new_state = self._model.state
            if self._model.state_timeout > 0:
                pass
            elif self._model.state_transition_possible_to(new_state):
                self._model.set_state(new_state)
                self._model.set_input_value(input_value)
                if self._model.state_spec.get('spawn', False):
                    self.spawn()

    def spawn(self):
        if not self._model.spawn:
            self._model.set_spawn(self._spawn_func())

    def __repr__(self):
        return "{} at {} directed {}".format(self._model.name, self._model.position, self._model.rotation[1])
