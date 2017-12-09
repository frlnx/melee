from typing import Set

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView
from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.input_handlers import GamePad
from engine.physics.force import Vector, MomentumForce, Direction, Position

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
        sum_p = array([0, 0, 0])
        sum_v = array([0, 0, 0])
        for sub_controller in self.sub_controllers:
            self._model.add_spin(*sub_controller.spin)
            force = sub_controller._force
            if force > 0:
                r = radians(sub_controller._model.rotation[1]) + pi
                v = array([sin(-r), 0, cos(r)]) * force
                sum_v = sum_v + v
                p = array(sub_controller._model.position) * (force / sum([abs(v) for v in sum_v]))
                sum_p = sum_p + p
        yaw = atan2(sum_v[2], sum_v[0])
        pos_yaw = atan2(sum_p[2], sum_p[0])
        translation_force = sin((pi/2) - (yaw % (pi*2)) - (pos_yaw % (pi*2)))
        directional_forces = sum_v * translation_force
        movement = m.dot(directional_forces).tolist()[0]
        self._model.add_movement(*movement)
