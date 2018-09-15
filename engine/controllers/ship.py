from typing import Set

from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.models.ship import ShipModel


class ShipController(BaseController):

    def __init__(self, model: ShipModel, gamepad: "InputHandler"):
        super().__init__(model, gamepad)
        self._model = model
        self._button_config = {
            3: self.select_next_target,
            2: self.reset,
            "TAB": self.select_next_target,
            "SPACE": self.self_destruct
        }

    def self_destruct(self):
        for part in self._model.parts:
            if part.name != "cockpit":
                self._model.eject_part(part)
                part.explode()

    @property
    def spawns(self):
        return self._model.spawns

    def reset(self):
        self._model.set_rotation(0, 0, 0)
        self._model.set_position(0, 0, 0)
        self._model.set_movement(0, 0, 0)
        self._model.set_spin(0, 0, 0)

    def select_next_target(self):
        self._model.cycle_next_target()

    @property
    def sub_controllers(self) -> Set[ShipPartController]:
        return self._sub_controllers

    def update(self, dt):
        for sub_controller in self._sub_controllers:
            sub_controller.update(dt)
        if self._gamepad:
            buttons_done = set()
            for button in self._gamepad.buttons:
                if button in self._button_config:
                    self._button_config[button]()
                    buttons_done.add(button)
            self._gamepad.buttons -= buttons_done
