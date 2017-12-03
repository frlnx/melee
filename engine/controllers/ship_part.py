from engine.controllers.base_controller import BaseController
from engine.views.base_view import BaseView
from engine.models.ship_part import ShipPartModel
from engine.physics.vector import Vector, Position, Direction
from engine.input_handlers import GamePad


class ShipPartController(BaseController):

    def __init__(self, model: ShipPartModel, view: BaseView, gamepad: GamePad):
        super().__init__(model, view, gamepad)
        self._model = model
        self._view = view
        self._null_vector = Vector(0, Position(0, 0, 0), Direction(0, 0, 0))
        print(self._model.name, self._model.axis, self._model.button)

    def spawns(self) -> bool:
        return False

    @property
    def force_vector(self) -> Vector:
        force = self._model.state_spec.get('thrust generated', 0)
        if force == 0:
            return self._null_vector
        vector = Vector(force, Position(*self._model.position), Direction(*self._model.rotation))
        print("Thrust", vector.rotational_forces)
        return vector

    def update(self, dt):
        super(ShipPartController, self).update(dt)
        axis_value = self._gamepad.axis.get(self._model.axis, 0)
        if self._model.button in self._gamepad.buttons:
            try:
                self._model.set_state('button')
            except AssertionError:
                pass
        elif axis_value > 0:
            try:
                self._model.set_state('axis')
                fire_material = self._view._mesh.materials['Fire_front']
                fire_material.set_alpha(axis_value)
            except AssertionError:
                raise
        else:
            self._model.set_state('idle')

    def axis_multiplier(self):
        return max(0, self._gamepad.axis.get(self._model.axis, 0))