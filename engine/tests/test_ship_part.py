from engine.controllers.factories import ShipPartControllerFactory
from engine.models.factories import ShipPartModelFactory
from engine.input_handlers import InputHandler


controller_factory = ShipPartControllerFactory()
model_factory = ShipPartModelFactory()


class TestHorizontalEngineAt45DegreesOff(object):

    def setup(self):
        model = model_factory.manufacture("engine", position=[1, 0, -1], rotation=[0, 90, 0])
        self.gamepad = InputHandler()
        self.target = controller_factory.manufacture(model, self.gamepad)
        self.target._force = 1

    def test_engine_force_direction_is_left(self):
        assert round(self.target.sized_force_vector.forces.direction.yaw, 3) == 90

    def test_force_is_pushing_left(self):
        assert -1 == self.target.sized_force_vector.forces.x