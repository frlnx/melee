from engine.controllers.base_controller import BaseController
from engine.views.ship_part import ShipPartView
from engine.models.ship_part import ShipPartModel
from engine.physics.vector import Vector
from engine.input_handlers import GamePad


class ShipPartController(BaseController):

    def __init__(self, model: ShipPartModel, view: ShipPartView, gamepad: GamePad):
        super().__init__(model, view, gamepad)
        self._model = model
        self._view = view

    def spawns(self) -> bool:
        return False

    @property
    def force_vector(self) -> Vector:
        force = self._model.state_spec.get('thrust generated')
        return Vector(force, self._model.position, self._model.rotation)

    def update(self, dt):
        super(ShipPartController, self).update(dt)
        if self._model.button in self._gamepad.buttons:
            try:
                self._model.set_state('button')
            except AssertionError:
                pass
        elif self._gamepad.axis.get(self._model.axis, 0) > 0:
            try:
                self._model.set_state('axis')
            except AssertionError:
                pass
        else:
            self._model.set_state('idle')

    def axis_multiplier(self):
        return max(0, self._gamepad.axis.get(self._model.axis, 0))