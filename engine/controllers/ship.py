from typing import Set

from engine.models.ship import ShipModel, BaseModel
from engine.models.projectiles import PlasmaModel
from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.input_handlers import InputHandler
from engine.physics.force import MutableOffsets
from pyglet.window import key


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
        self._model.parts = []
        #self._model.rebuild()

    @property
    def spawns(self):
        return self._model.spawns

    def reset(self):
        self._model.set_rotation(0, 0, 0)
        self._model.set_position(0, 0, 0)
        self._model.set_movement(0, 0, 0)
        self._model.set_spin(0, 0, 0)

    def register_target(self, target_model: BaseModel):
        self._possible_targets.append(target_model)

    def select_next_target(self):
        self.select_target(self.next_target())
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
            self._model.add_spin(*sub_controller.spin / self._model._inertia)
            forces = sub_controller.moment_force.rotated(-self._model.rotation.yaw)
            forces = forces.translation_forces() / self._model.mass
            self._model.add_movement(*forces)

        buttons_done = set()
        for button in self._gamepad.buttons:
            if button in self._button_config:
                self._button_config[button]()
                buttons_done.add(button)
        self._gamepad.buttons -= buttons_done
        #if len(self._gamepad.buttons) > 0:
        #    print(self._gamepad.buttons)

    def move_to(self, location):
        self._model.set_position(*location)

    def solve_collision(self, other_model: BaseModel):
        collides, x, z = self._model.intersection_point(other_model)
        if collides and isinstance(other_model, PlasmaModel):
            print("Bang at {} {}".format(x, z))

        if collides and False:
            position = MutableOffsets(x, 0, z)
            my_force = self._model.global_momentum_at(position)
            other_force = other_model.global_momentum_at(position)
            #other_model.apply_global_force(-other_force)
            #self._model.apply_global_force(-my_force)
            other_model.apply_global_force(my_force)
            self._model.apply_global_force(other_force)
