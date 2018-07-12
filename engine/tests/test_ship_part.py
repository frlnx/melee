from engine.controllers.factories import ShipPartControllerFactory
from engine.models.factories import ShipPartModelFactory
from engine.input_handlers import InputHandler

from math import degrees

controller_factory = ShipPartControllerFactory()
model_factory = ShipPartModelFactory()


class TestHorizontalEngineAt135DegreesOff(object):

    def setup(self):
        model = model_factory.manufacture("engine", position=[1, 0, -1], rotation=[0, 90, 0])
        self.target = model
        self.target.set_state("active")
        self.target.set_input_value(1.0)

    def test_engine_force_offsets_is_left(self):
        x, y, z = self.target.acceleration
        assert (-5.0, 0, 0) == tuple(round(v) for v in (x, y, z))

    def test_engine_force_direction_is_left(self):
        assert round(self.target.acceleration.direction.yaw, 3) == 90

    def test_force_is_pushing_left(self):
        assert -5.0 == self.target.acceleration.x

    def test_force_degree_is_positive_45_degrees_from_being_lateral(self):
        assert 135 == self.target.diff_yaw_of_force_to_pos  # Was 45 before refactor

    def test_force_is_rotating_left(self):
        assert 132.83 == round(self.target.torque.yaw, 2)


class TestHorizontalEngineAt45DegreesOff(object):

    def setup(self):
        model = model_factory.manufacture("engine", position=[1, 0, -1], rotation=[0, 0, 0])
        self.target = model
        self.target.set_state("active")
        self.target.set_input_value(1.0)

    def test_engine_force_offsets_is_up(self):
        x, y, z = self.target.acceleration
        assert (0, 0, -5.0) == tuple(round(v) for v in (x, y, z))

    def test_engine_force_direction_is_left(self):
        assert round(self.target.acceleration.direction.yaw, 3) == 0

    def test_force_is_pushing_up(self):
        assert -5.0 == self.target.acceleration.z

    def test_force_degree_offset_is_negative_45_degrees_from_being_lateral(self):
        assert 45 == self.target.diff_yaw_of_force_to_pos

    def test_force_is_rotating_left(self):
        assert 132.83 == round(self.target.torque.yaw, 2)
