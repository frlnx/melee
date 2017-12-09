from engine.physics.force import Force, Position, Direction


class TestPosition(object):

    def setup(self):
        self.target = Position(1, 0, 0)

    def test_distance_is_one(self):
        assert 1 == self.target.distance

    def test_angle_is_yaw_90(self):
        assert [0, 90, 0] == self.target.direction.xyz.tolist()


class TestRotationalPhysicsVector(object):

    def setup(self):
        position = Position(1, 0, 0)
        direction = Direction(0, 0, 0)
        self.target = Force(position, direction)

    def test_vector_impacts_yaw_negatively(self):
        assert 0 > self.target.yaw_momentum

    def test_translation_force_is_zero(self):
        assert self.target.translation_force == 0

    def test_vector_does_not_move_object(self):
        x, y, z = self.target.directional_forces(1)
        assert 0 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)


class TestVectorThroughCenterOfMassFromRight(object):

    def setup(self):
        position = Position(1, 0, 0)
        direction = Direction(0, -90, 0)
        self.target = Force(position, direction)

    def test_position_direction_is_90(self):
        assert self.target.position.direction == Position(0, 90, 0)

    def test_all_force_is_translation_force(self):
        assert 1 == self.target.translation_force

    def test_object_moves_left(self):
        x, y, z = self.target.directional_forces(1)
        assert -1 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)


class TestVectorThroughCenterOfMassFromLeft(object):

    def setup(self):
        position = Position(-1, 0, 0)
        direction = Direction(0, 90, 0)
        self.target = Force(position, direction)

    def test_all_force_is_translation_force(self):
        assert 1 == self.target.translation_force

    def test_object_moves_right(self):
        x, y, z = self.target.directional_forces(1)
        assert 1 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)

