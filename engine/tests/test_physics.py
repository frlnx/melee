from engine.physics.vector import Vector, Position, Direction


class TestPosition(object):

    def setup(self):
        self.target = Position(1, 0, 0)

    def test_distance_is_one(self):
        assert 1 == self.target.distance

    def test_angle_is_yaw_90(self):
        assert [0, 90, 0] == self.target.direction._pitch_yaw_bank


class TestRotationalPhysicsVector(object):

    def setup(self):
        position = Position(1, 0, 0)
        direction = Direction(0, 0, 0)
        self.target = Vector(position, direction)

    def test_offset_direction_is_minus_90_degrees(self):
        assert [0, -90, 0] == self.target._offset_direction._pitch_yaw_bank

    def test_vector_impacts_yaw_negatively(self):
        pitch, yaw, bank = self.target.rotational_forces
        assert 0 > yaw

    def test_vector_does_not_impact_pitch(self):
        pitch, yaw, bank = self.target.rotational_forces
        assert 0 == pitch

    def test_vector_does_not_impact_bank(self):
        pitch, yaw, bank = self.target.rotational_forces
        assert 0 == bank

    def test_vector_does_not_move_object(self):
        x, y, z = self.target.directional_forces
        assert 0 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)


class TestVectorThroughCenterOfMassFromRight(object):

    def setup(self):
        position = Position(1, 0, 0)
        direction = Direction(0, -90, 0)
        self.target = Vector(position, direction)

    def test_offset_force_is_opposite_direction(self):
        assert [0, 180, 0] == self.target._offset_direction._pitch_yaw_bank

    def test_object_moves_left(self):
        x, y, z = self.target.directional_forces
        assert -1 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)


class TestVectorThroughCenterOfMassFromLeft(object):

    def setup(self):
        position = Position(-1, 0, 0)
        direction = Direction(0, 90, 0)
        self.target = Vector(position, direction)

    def test_offset_force_is_opposite_direction(self):
        assert [0, 180, 0] == self.target._offset_direction._pitch_yaw_bank

    def test_object_moves_right(self):
        x, y, z = self.target.directional_forces
        assert 1 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)
