from engine.models.base_model import BaseModel


class BaseController(object):

    def __init__(self, model: BaseModel, gamepad: "InputHandler"=None):
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
