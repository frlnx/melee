from typing import Set

from engine.models.ship import ShipModel, BaseModel
from engine.views.base_view import BaseView
from engine.controllers.base_controller import BaseController
from engine.controllers.ship_part import ShipPartController
from engine.input_handlers import InputHandler
from engine.physics.force import Force, Offsets

from functools import reduce


class ShipController(BaseController):

    def __init__(self, model: ShipModel, view: BaseView, gamepad: InputHandler):
        super().__init__(model, view, gamepad)
        self._model = model
        self._target_model = model
        self._possible_targets = [model]
        self._button_config = {3: self.select_next_target, 2: self.reset}
        try:
            self._target_indicator = [model for model in self._model.parts if model.target_indicator][0]
        except IndexError:
            self._target_indicator = None

    def collides(self, other_model: BaseModel):
        if not self._collides(self._model, other_model):
            return False
        try:
            other_parts = other_model.parts
        except AttributeError:
            other_parts = [other_model]
        part_zip = zip(self._model.parts, other_parts)
        # TODO: Check each part against other outer bounding box to determine which needs individual checks
        for part1, part2 in part_zip:
            if self._collides(part1, part2):
                return True
        return False

    def colliding_forces(self, other_model: ShipModel):
        part_zip = zip(self._model.parts, other_model.parts)
        for part1, part2 in part_zip:
            if self._collides(part1, part2):
                direction = Offsets(*(other_model.movement)) # Movement is already in the universal coord system
                # TODO: Transfer the rotational force from the coordinate system of other model to the coordinate system
                #       Of the own model with rotational forces.
                force1 = Force(part2.position, self.movement_at(part2.position))
                force1.rotated(other_model.yaw - self._model.yaw)
                force1.translate(other_model.position - self._model.position)
                force2 = Force(part1.position, self.movement_at(part1.position))
                force2.rotated(self._model.yaw - other_model.yaw)
                force2.translate(self._model.position - other_model.position)
                if force1.forces.y != 0 or force2.forces.y != 0:
                    print(force1, force2)
                return force1, force2
        raise ValueError("Models don't collide")

    def movement_at(self, ship_grid_position: Offsets) -> Offsets:
        movement = self._model.movement
        yaw_delta = self._model.spin[1]
        spin_speed = ship_grid_position.distance * yaw_delta
        tangent_movement = ship_grid_position.rotated(90) * spin_speed
        return movement + tangent_movement

    def apply_force(self, force: Force):
        force = force.rotated(-self._model.rotation[1])
        self._model.add_movement(*force.translation_forces())
        self._model.add_spin(0, force.delta_yaw, 0)

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
        if self._target_indicator:
            self._target_indicator.texture_rotation = [x for x in self._model.rotation]
            positions_iterator = zip(self._target_model.position, self._model.position)
            self._target_indicator.texture_offset = [-(y - x) / 10.2 for x, y in positions_iterator]

    @property
    def sub_controllers(self) -> Set[ShipPartController]:
        return self._sub_controllers

    def update(self, dt):
        super().update(dt)
        for sub_controller in self.sub_controllers:
            self._model.add_spin(*sub_controller.spin / self._model._inertia)
            forces = sub_controller.moment_force.rotated(-self._model.rotation[1])
            forces = forces.translation_forces() / self._model.mass
            self._model.add_movement(*forces)

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
