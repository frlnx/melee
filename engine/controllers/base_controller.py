from engine.models.base_model import BaseModel
from engine.views.base_view import BaseView
from engine.input_handlers import GamePad


class BaseController(object):

    def __init__(self, model: BaseModel, view: BaseView, gamepad: GamePad):
        self._model = model
        self._view = view
        self._gamepad = gamepad
        self._sub_controllers = set()

    @property
    def view(self):
        return self._view

    def add_sub_controller(self, sub_controller):
        self._sub_controllers.add(sub_controller)

    def update(self, dt):
        self._model.set_position(*[p + m * dt for p, m in zip(self._model.position, self._model.movement)])
        self._model.set_rotation(*[r + s * dt for r, s in zip(self._model.rotation, self._model.spin)])
        for sub_controller in self._sub_controllers:
            sub_controller.update(dt)
