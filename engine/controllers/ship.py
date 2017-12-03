from typing import Set

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView
from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.input_handlers import GamePad


class ShipController(BaseController):

    def __init__(self, model: ShipModel, view: BaseView, gamepad: GamePad):
        super().__init__(model, view, gamepad)

    @property
    def sub_controllers(self) -> Set[ShipPartController]:
        return self._sub_controllers

    def update(self, dt):
        super().update(dt)
        #dyaw = (self._gamepad.axis['y'] - self._gamepad.axis['rz']) * dt * 10
        dyaw = 0
        for sub_controller in self.sub_controllers:
            vector = sub_controller.force_vector
            self._model.add_spin(*vector.rotational_forces)
            self._model.add_movement(*vector.directional_forces)
