from engine.controllers.base_controller import BaseController
from engine.models.factories import ShipModelFactory
from engine.input_handlers import InputHandler


model_factory = ShipModelFactory()
dummy_input = InputHandler()

class TestCollisions(object):

    def setup(self):
        self.target1 = model_factory.manufacture("wolf")
        self.target2 = model_factory.manufacture("wolf")

    def test_collision_on_same_location(self):
        assert BaseController._collides(self.target1, self.target2)
        assert BaseController._collides(self.target2, self.target1)

    def test_collision_on_translation(self):
        self.target2.set_position(1, 0, 0)
        assert BaseController._collides(self.target1, self.target2)
        assert BaseController._collides(self.target2, self.target1)

    def test_collision_on_rotation(self):
        self.target2.set_rotation(0, 90, 0)
        assert BaseController._collides(self.target1, self.target2)
        assert BaseController._collides(self.target2, self.target1)

    def test_collision_on_rotation_and_translation(self):
        self.target2.set_position(1, 0, 0)
        self.target2.set_rotation(0, 90, 0)
        assert BaseController._collides(self.target1, self.target2)
        assert BaseController._collides(self.target2, self.target1)
