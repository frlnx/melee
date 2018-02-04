from engine.models.base_model import BaseModel
from engine.views.base_view import BaseView
from engine.input_handlers import InputHandler
from engine.physics.force import MutableOffsets


class BaseController(object):

    def __init__(self, model: BaseModel, view: BaseView, gamepad: InputHandler):
        self._model = model
        self._view = view
        self._gamepad = gamepad
        self._sub_controllers = set()

    @property
    def spawns(self):
        return []

    @property
    def view(self):
        return self._view

    def add_sub_controller(self, sub_controller):
        self._sub_controllers.add(sub_controller)

    def update(self, dt):
        self._model.translate(*(self._model.movement * dt))
        self._model.rotate(*(self._model.spin * dt))
        for sub_controller in self._sub_controllers:
            sub_controller.update(dt)

    def solve_collision(self, other_model: BaseModel):
        collides, x, z = self._model.intersection_point(other_model)
        if collides:
            position = MutableOffsets(x, 0, z)
            my_force = self._model.global_momentum_at(position)
            other_force = other_model.global_momentum_at(position)
            other_model.apply_global_force(-other_force)
            self._model.apply_global_force(-my_force)
            other_model.apply_global_force(my_force)
            self._model.apply_global_force(other_force)
