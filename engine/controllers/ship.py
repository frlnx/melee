from typing import Set

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView
from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.input_handlers import GamePad

from math import cos, sin, radians, pi
from numpy import matrix, array


class ShipController(BaseController):

    def __init__(self, model: ShipModel, view: BaseView, gamepad: GamePad):
        super().__init__(model, view, gamepad)

    @property
    def sub_controllers(self) -> Set[ShipPartController]:
        return self._sub_controllers

    def update(self, dt):
        super().update(dt)
        theta = radians(self._model.rotation[1])
        m = matrix([[cos(theta), 0, sin(theta)], [0, 1, 0], [-sin(theta), 0, -cos(theta)]])
        for sub_controller in self.sub_controllers:
            self._model.add_spin(*sub_controller.spin)

        movement = m.dot(self.sum_directional_forces()).tolist()[0]
        self._model.add_movement(*movement)

    def sum_directional_forces(self) -> array:
        forces = None
        for sub_controller in self.sub_controllers:
            if forces is None:
                forces = sub_controller.sized_force_vector
            else:
                forces = forces + sub_controller.sized_force_vector
        return forces.translation_forces()