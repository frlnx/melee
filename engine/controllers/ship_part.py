from typing import Callable

from engine.controllers.base_controller import BaseController
from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableForce, Degrees
from engine.input_handlers import InputHandler

from math import sin, cos, radians


class ShipPartController(BaseController):

    def __init__(self, model: ShipPartModel, gamepad: InputHandler, spawn_func: Callable):
        super().__init__(model, gamepad)
        self._model = model
        self._spawn_func = spawn_func
        yaw = self._model.rotation[1]
        self._force_vector = MutableForce(self._model.position,
                                          MutableOffsets(-sin(radians(yaw)), 0, -cos(radians(yaw))))
        self._model.observe(self.model_changed)

    def model_changed(self):
        yaw = self._model.rotation[1]
        self._force_vector.set_forces(-sin(radians(yaw)), 0, -cos(radians(yaw)))

    @property
    def moment_force(self):
        return self._force_vector

    def update(self, dt):
        super().update(dt)
        axis_value = self._gamepad.axis.get(self._model.axis, 0)
        if self._model.state_timeout > 0:
            return
        if 'next state' in self._model.state_spec and \
                self._model.state_transition_possible_to(self._model.state_spec['next state']):
            self._model.set_state(self._model.state_spec['next state'])

        if (self._model.button in self._gamepad.buttons or self._model.keyboard in self._gamepad.buttons) and \
                self._model.state_transition_possible_to('active'):
            try:
                self._model.set_state('active')
            except AssertionError:
                pass
            if self._model.state_spec.get('spawn', False):
                self.spawn()
            self._force_vector.set_force(1.0 * self._model.state_spec.get('thrust generated', 0))
        elif axis_value > 0:
            axis_value = min(1.0, max(0.0, axis_value))
            self._force_vector.set_force(axis_value * self._model.state_spec.get('thrust generated', 0))
            try:
                self._model.set_state('active')
            except AssertionError:
                raise
        elif self._model.state_transition_possible_to('idle'):
            self._force_vector.set_force(0.0)
            self._model.set_state('idle')

    def spawn(self):
        if not self._model.spawn:
            self._model.set_spawn(self._spawn_func())

    @property
    def spin(self):
        return Degrees(0, self._force_vector.delta_yaw, 0)

    @property
    def yaw(self):
        return self._model.rotation[1]

    @property
    def position(self):
        return self._model.position

    def __repr__(self):
        return "{} at {} directed {}".format(self._model.name, self._model.position, self._model.rotation[1])
