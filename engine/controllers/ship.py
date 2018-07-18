from typing import Set

from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.input_handlers import InputHandler
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
        if self._model.target == target_model:
            self.select_next_target()

    def select_next_target(self):
        next_target = self.next_target()
        self._model.set_target(next_target)

    def next_target(self) -> ShipModel:
        index = self._possible_targets.index(self._target_model)
        target_model = self._possible_targets[(index + 1) % len(self._possible_targets)]
        return target_model

    @property
    def sub_controllers(self) -> Set[ShipPartController]:
        return self._sub_controllers

    def update(self, dt):
        super().update(dt)
        buttons_done = set()
        for button in self._gamepad.buttons:
            if button in self._button_config:
                self._button_config[button]()
                buttons_done.add(button)
        self._gamepad.buttons -= buttons_done

    def move_to(self, location):
        self._model.set_position(*location)
