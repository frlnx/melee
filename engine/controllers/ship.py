from typing import Set

from engine.models.ship import ShipModel, BaseModel
from engine.views.base_view import BaseView
from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.input_handlers import InputHandler
from engine.physics.force import Force

from functools import reduce


class ShipController(BaseController):

    def __init__(self, model: ShipModel, view: BaseView, gamepad: InputHandler):
        super().__init__(model, view, gamepad)
        self._target_model = model
        self._possible_targets = [model]
        self._button_config = {3: self.select_next_target, 2: self.reset}

    def reset(self):
        self._model.set_rotation(0, 0, 0)
        self._model.set_position(0, 0, 0)
        self._model.set_movement(0, 0, 0)
        self._model.set_spin(0, 0, 0)

    def register_target(self, target_model: BaseModel):
        self._possible_targets.append(target_model)

    def select_next_target(self):
        self.select_target(self.next_target())

    def next_target(self) -> BaseModel:
        index = self._possible_targets.index(self._target_model)
        target_model = self._possible_targets[(index + 1) % len(self._possible_targets)]
        return target_model

    def select_target(self, target: BaseModel):
        try:
            self.target_model.unobserve(self.update_target_position)
        except AttributeError:
            pass
        self.target_model = target

    def update_target_position(self):
        self._model.set_target_position(self.target_model.position)

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
        buttons_done = set()
        for button in self._gamepad.buttons:
            if button in self._button_config:
                self._button_config[button]()
                buttons_done.add(button)
        self._gamepad.buttons -= buttons_done
        if len(self._gamepad.buttons) > 0:
            print(self._gamepad.buttons)

    def move_to(self, location):
        self._model.set_position(*location)

    @staticmethod
    def sum_forces(forces) -> Force:
        assert len(forces) > 0
        if len(forces) == 1:
            return forces[0]
        else:
            return reduce(lambda a, b: a + b, forces[1:], forces[0])


