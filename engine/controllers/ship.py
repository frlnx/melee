from typing import Set

from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.input_handlers import InputHandler
from engine.models.base_model import BaseModel
from engine.models.projectiles import PlasmaModel
from engine.models.ship import ShipModel


class ShipController(BaseController):

    def __init__(self, model: ShipModel, gamepad: InputHandler):
        super().__init__(model, gamepad)
        self._model = model
        self._target_model = model
        self._possible_targets = [model]
        self._button_config = {
            3: self.select_next_target,
            2: self.reset,
            "TAB": self.select_next_target,
            "SPACE": self.self_destruct
        }

    def self_destruct(self):
        for part in self._model.parts:
            part.set_movement(*self._model.momentum_at(part.position).forces)
            self._model.mutate_offsets_to_global(part.position)
            part.set_rotation(*self._model.rotation)
            self._model.add_own_spawn(part)
            self._model.remove_part(part)

    def destroy_part(self, part):
        self._model.remove_part(part)
        part.set_alive(False)

    @property
    def spawns(self):
        return self._model.spawns

    def reset(self):
        self._model.set_rotation(0, 0, 0)
        self._model.set_position(0, 0, 0)
        self._model.set_movement(0, 0, 0)
        self._model.set_spin(0, 0, 0)

    def register_target(self, target_model: ShipModel):
        if target_model.mass > 1.0 and target_model not in self._possible_targets:
            self._possible_targets.append(target_model)

    def deregister_target(self, target_model: ShipModel):
        try:
            self._possible_targets.remove(target_model)
        except ValueError:
            pass

    def select_next_target(self):
        next_target = self.next_target()
        self.select_target(next_target)
        self.update_target_position()

    def next_target(self) -> BaseModel:
        index = self._possible_targets.index(self._target_model)
        target_model = self._possible_targets[(index + 1) % len(self._possible_targets)]
        return target_model

    def select_target(self, target: BaseModel):
        try:
            self._target_model.unobserve(self.update_target_position)
        except AttributeError:
            pass
        self._target_model = target
        self._target_model.observe(self.update_target_position)

    def update_target_position(self):
        self._model.set_target_position_rotation(self._target_model.position, self._target_model.rotation)

    @property
    def sub_controllers(self) -> Set[ShipPartController]:
        return self._sub_controllers

    def update(self, dt):
        super().update(dt)
        for sub_controller in self.sub_controllers:
            self._model.add_spin(*sub_controller.spin / self._model.inertia)
            forces = sub_controller.moment_force.rotated(-self._model.rotation.yaw)
            forces = forces.translation_forces() / self._model.mass
            self._model.add_movement(*forces)

        buttons_done = set()
        for button in self._gamepad.buttons:
            if button in self._button_config:
                self._button_config[button]()
                buttons_done.add(button)
        self._gamepad.buttons -= buttons_done

    def move_to(self, location):
        self._model.set_position(*location)

    def solve_collision(self, other_model: BaseModel):
        if self._model.movement.distance == 0 and other_model.movement.distance == 0:
            return
        if isinstance(other_model, PlasmaModel):
            parts = self._model.parts_intersected_by(other_model)
            for part in parts:
                self.destroy_part(part)
        super(ShipController, self).solve_collision(other_model)

    def collide_with(self, other_model: BaseModel):
        if isinstance(other_model, PlasmaModel):
            parts = self._model.parts_intersected_by(other_model)
            for part in parts:
                self.destroy_part(part)
