from engine.models.base_model import BaseModel
from engine.input_handlers import InputHandler
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
        self._model.translate(*(self._model.movement * dt))
        self._model.rotate(*(self._model.spin * dt))
        for sub_controller in self._sub_controllers:
            sub_controller.update(dt)
        self._model.timers(dt)

    def solve_collision(self, other_model: BaseModel):
        pass
