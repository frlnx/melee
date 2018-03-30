from engine.controllers.base_controller import BaseController
from engine.models.projectiles import PlasmaModel
from engine.models.base_model import BaseModel
from engine.input_handlers import InputHandler
from engine.physics.force import MutableOffsets


class ProjectileController(BaseController):

    def __init__(self, model: PlasmaModel, gamepad: InputHandler):
        super(ProjectileController, self).__init__(model, gamepad)
        self._model = model

    def solve_collision(self, other_model: BaseModel):
        collides, x, z = self._model.intersection_point(other_model)
        if collides:
            print("Bang at {} {}".format(x, z))
            self._model.set_alive(False)
