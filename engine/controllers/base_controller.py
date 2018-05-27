from engine.input_handlers import InputHandler
from engine.models.base_model import BaseModel
from engine.physics.force import MutableOffsets


class BaseController(object):

    def __init__(self, model: BaseModel, gamepad: InputHandler):
        self._model = model
        self._gamepad = gamepad
        self._sub_controllers = set()

    @property
    def spawns(self):
        return []

    @property
    def is_alive(self):
        return self._model.is_alive

    def add_sub_controller(self, sub_controller):
        self._sub_controllers.add(sub_controller)

    def update(self, dt):
        half_of_acceleration = self._model.acceleration * dt / 2
        half_of_torque = self._model.torque * dt / 2
        self._model.movement.translate(half_of_acceleration)
        self._model.spin.translate(half_of_torque)
        self._model.translate(*(self._model.movement * dt))
        self._model.rotate(*(self._model.spin * dt))
        self._model.movement.translate(half_of_acceleration)
        self._model.spin.translate(half_of_torque)
        for sub_controller in self._sub_controllers:
            sub_controller.update(dt)
        self._model.timers(dt)

    def solve_collision(self, other_model: BaseModel):
        collides, x, z = self._model.intersection_point(other_model)
        if collides:
            position = MutableOffsets(x, 0, z)
            my_force = self._model.global_momentum_at(position) * self._model.mass
            other_force = other_model.global_momentum_at(position) * other_model.mass
            other_model.apply_global_force(my_force)
            self._model.apply_global_force(other_force)
