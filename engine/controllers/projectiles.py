from engine.controllers.base_controller import BaseController
from engine.models.projectiles import PlasmaModel


class ProjectileController(BaseController):

    def __init__(self, model: PlasmaModel, gamepad: "InputHandler"):
        super(ProjectileController, self).__init__(model, gamepad)
        self._model = model
