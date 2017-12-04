from engine.physics.vector import Vector, Position, Direction


class TestPhysicsVector(object):

    def setup(self):
        position = Position(1, 0, 0)
        direction = Direction(0, 0, 0)
        self.target = Vector(1, position, direction)

    def test_vector_impacts_yaw_negatively(self):
        pitch, yaw, bank = self.target.rotational_forces
        assert pitch == 0
        assert yaw < 0
        assert bank == 0

    def test_vector_impacts_yaw_negatively(self):
        pitch, yaw, bank = self.target.rotational_forces
        assert pitch == 0
        assert yaw < 0
        assert bank == 0

    def test_vector_impacts_yaw_negatively(self):
        pitch, yaw, bank = self.target.rotational_forces
        assert pitch == 0
        assert yaw < 0
        assert bank == 0
