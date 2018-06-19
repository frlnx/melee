from engine.controllers.factories import ShipPartControllerFactory
from engine.models.factories import ShipPartModelFactory
from engine.input_handlers import InputHandler

from math import degrees

controller_factory = ShipPartControllerFactory()
model_factory = ShipPartModelFactory()


class TestHorizontalEngineAt135DegreesOff(object):

    def setup(self):
        model = model_factory.manufacture("engine", position=[1, 0, -1], rotation=[0, 90, 0])
        self.gamepad = InputHandler()
        self.target = controller_factory.manufacture(model, self.gamepad)

    def etst_engine_force_offsets_is_left(self):
        x, y, z = self.target.moment_force.forces
        assert (-1, 0, 0) == (x, y, z)

    def test_engine_force_direction_is_left(self):
        assert round(self.target.moment_force.forces.direction.yaw, 3) == 90

    def test_force_is_pushing_left(self):
        assert -1 == self.target.moment_force.forces.x

    def test_force_degree_is_positive_45_degrees_from_being_lateral(self):
        assert degrees(self.target.moment_force.radians_force_is_lateral_to_position()) == 45

    def test_force_is_rotating_left(self):
        assert round(self.target.moment_force.delta_yaw, 2) == 26.57


class TestHorizontalEngineAt45DegreesOff(object):

    def setup(self):
        model = model_factory.manufacture("engine", position=[1, 0, -1], rotation=[0, 0, 0])
        self.gamepad = InputHandler()
        self.target = controller_factory.manufacture(model, self.gamepad)

    def test_engine_force_offsets_is_up(self):
        x, y, z = self.target.moment_force.forces
        assert (0, 0, -1) == (x, y, z)

    def test_engine_force_direction_is_left(self):
        assert round(self.target.moment_force.forces.direction.yaw, 3) == 0

    def test_force_is_pushing_up(self):
        assert -1 == self.target.moment_force.forces.z

    def test_force_degree_offset_is_negative_45_degrees_from_being_lateral(self):
        assert degrees(self.target.moment_force.radians_force_is_lateral_to_position()) == -45

    def test_force_is_rotating_left(self):
        assert round(self.target.moment_force.delta_yaw, 2) == 26.57
