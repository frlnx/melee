from engine.models.ship import ShipModel
from engine.views.ship import ShipView
from engine.controllers.base_controller import BaseController
from engine.input_handlers import GamePad


class ShipController(BaseController):

    def __init__(self, model: ShipModel, view: ShipView, gamepad: GamePad):
        super().__init__(model, view, gamepad)

    def update(self, dt):
        super(ShipController, self).update(dt)
        dyaw = (self._gamepad.axis['y'] - self._gamepad.axis['rz']) * dt * 10
        self._model.add_spin(0, dyaw, 0)
