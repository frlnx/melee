from typing import Set

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView
from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.input_handlers import GamePad
from engine.physics.force import Force

from functools import reduce


class ShipController(BaseController):

    def __init__(self, model: ShipModel, view: BaseView, gamepad: GamePad):
        super().__init__(model, view, gamepad)

    @property
    def sub_controllers(self) -> Set[ShipPartController]:
        return self._sub_controllers

    def update(self, dt):
        super().update(dt)
        forces = []
        for sub_controller in self.sub_controllers:
            self._model.add_spin(*sub_controller.spin)
            sized_force_vector = sub_controller.sized_force_vector
            if sized_force_vector.forces.distance > 0.01:
                forces.append(sub_controller.sized_force_vector)

        if len(forces) > 0:
            forces = self.sum_forces(forces)
            forces = forces.rotate(-self._model.rotation[1])
            movement = forces.translation_forces()
            self._model.add_movement(*movement)
        if 7 in self._gamepad.buttons:
            self._model.set_rotation(0, 0, 0)
            self._model.set_position(0, 0, 0)
            self._model.set_movement(0, 0, 0)
            self._model.set_spin(0, 0, 0)
        if 6 in self._gamepad.buttons:
            print(forces)

    @staticmethod
    def sum_forces(forces) -> Force:
        assert len(forces) > 0
        if len(forces) == 1:
            return forces[0]
        else:
            return reduce(lambda a, b: a + b, forces[1:], forces[0])


