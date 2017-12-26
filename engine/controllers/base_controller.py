from engine.models.base_model import BaseModel
from engine.views.base_view import BaseView
from engine.input_handlers import InputHandler


class BaseController(object):

    def __init__(self, model: BaseModel, view: BaseView, gamepad: InputHandler):
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
        self._model.translate(*(self._model.movement * dt))
        self._model.rotate(*(self._model.spin * dt))
        for sub_controller in self._sub_controllers:
            sub_controller.update(dt)

    @staticmethod
    def _collides(model1: BaseModel, model2: BaseModel):
        if not model1.outer_bounding_box.intersects(model2.outer_bounding_box):
            return False
        m1_m1 = model1.outer_bounding_box_after_rotation(-model1.yaw)
        m2_m1 = model2.outer_bounding_box_after_rotation(-model1.yaw)
        if not m1_m1.intersects(m2_m1):
            return False
        m1_m2 = model1.outer_bounding_box_after_rotation(-model2.yaw)
        m2_m2 = model2.outer_bounding_box_after_rotation(-model2.yaw)
        if not m1_m2.intersects(m2_m2):
            return False
        return True

    def collides(self, other_model: BaseModel):
        return self._collides(self._model, other_model)
