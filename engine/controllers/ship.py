from typing import Set

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView
from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.input_handlers import GamePad

from math import cos, sin, radians, atan2, pi
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

        movement = m.dot(array(self.sum_directional_forces())).tolist()[0]
        self._model.add_movement(*movement)

    def sum_directional_forces(self):
        x_pos_sum = 0
        z_pos_sum = 0
        x_force_sum = 0
        z_force_sum = 0
        for sub_controller in self.sub_controllers:
            force = sub_controller._force
            if force > 0:
                x_force, z_force = sub_controller.x_z_force
                x_force_sum += x_force
                z_force_sum += z_force
                x_pos_sum += sub_controller.position[0] * force
                z_pos_sum += sub_controller.position[2] * force
        yaw = atan2(z_force_sum, x_force_sum)
        pos_yaw = atan2(z_pos_sum, x_pos_sum)
        translation_force = sin((pi/2) - (yaw % (pi*2)) - (pos_yaw % (pi*2)))
        return x_force_sum * translation_force, 0, z_force_sum * translation_force