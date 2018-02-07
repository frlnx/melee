from engine.controllers.base_controller import BaseController
from engine.models.projectiles import PlasmaModel
from engine.views.base_view import BaseView
from engine.input_handlers import InputHandler


class ProjectileController(BaseController):

    def __init__(self, model: PlasmaModel, view: BaseView, gamepad: InputHandler):
        super(ProjectileController, self).__init__(model, view, gamepad)
        self._model = model

    @property
    def is_alive(self):
        return self._model.is_alive
