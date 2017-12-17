from engine.controllers.base_controller import BaseController
from engine.views.base_view import BaseView
from engine.models.ship_part import ShipPartModel
from engine.physics.force import Offsets, Force
from engine.input_handlers import InputHandler

from math import sin, cos, radians


class ShipPartController(BaseController):

    def __init__(self, model: ShipPartModel, view: BaseView, gamepad: InputHandler):
        super().__init__(model, view, gamepad)
        self._model = model
        self._view = view
        self._force = 0
        yaw = self._model.rotation[1]
        self._force_vector = Force(Offsets(*self._model.position),
                                   Offsets(-sin(radians(yaw)), 0, -cos(radians(yaw))))

    @property
    def force_vector(self) -> Force:
        return self._force_vector

    @property
    def sized_force_vector(self):
        return self._force_vector * self._force

    def update(self, dt):
        super(ShipPartController, self).update(dt)
        axis_value = self._gamepad.axis.get(self._model.axis, 0)
        if self._model.button in self._gamepad.buttons:
            self._force = 1.0
            try:
                self._model.set_state('button')
            except AssertionError:
                pass
        elif axis_value > 0:
            self._force = self._model.state_spec.get('thrust generated', 0) * axis_value
            try:
                self._model.set_state('axis')
                fire_material = self._view._mesh.materials['Fire_front']
                fire_material.set_diffuse([axis_value] * 4)
            except AssertionError:
                raise
        else:
            self._force = 0
            self._model.set_state('idle')

    @property
    def spin(self):
        return 0, self.force_vector.yaw_force(self._force), 0

    @property
    def yaw(self):
        return self._model.rotation[1]

    @property
    def position(self):
        return self._model.position

    def __repr__(self):
        return "{} at {} directed {}".format(self._model.name, self._model.position, self._model.rotation[1])