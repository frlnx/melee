from math import pi

from engine.physics.force import Offsets, Degrees, RotationalForce


class TestPosition(object):

    def setup(self):
        self.target = Offsets(1, 0, 0)

    def test_distance_is_one(self):
        assert 1 == self.target.distance

    def test_angle_is_yaw_90(self):
        assert [0, 90, 0] == self.target.direction.xyz.tolist()


class TestLeftRotationalPhysicsVector(object):

    def setup(self):
        position = Offsets(1, 0, 0)
        forces = Offsets(0, 0, 1)
        self.target = RotationalForce(position, forces)

    def test_position_direction(self):
        assert self.target.position.direction.xyz.tolist() == [0, 90, 0]

    def test_force_direction(self):
        assert self.target.forces.direction.xyz.tolist() == [0, 0, 0]

    def test_diff(self):
        assert self.target.diff_yaw_of_force_to_pos() == -90

    def test_vector_impacts_yaw_positively(self):
        assert 0 < self.target.yaw_momentum

    def test_c_radian(self):
        assert self.target.c_radian() == pi

    def test_translation_force_is_zero(self):
        assert 0 == round(self.target.translation_part_of_force(), 6)

    def test_vector_does_not_move_object(self):
        x, y, z = self.target.translation_forces()
        assert 0 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)


class TestRightRotationalPhysicsVector(object):

    def setup(self):
        position = Offsets(-1, 0, 0)
        forces = Offsets(0, 0, 1)
        self.target = RotationalForce(position, forces)

    def test_position_direction(self):
        assert self.target.position.direction.xyz.tolist() == [0, -90, 0]

    def test_force_direction(self):
        assert self.target.forces.direction.xyz.tolist() == [0, 0, 0]

    def test_vector_impacts_yaw_negatively(self):
        assert 0 > self.target.yaw_momentum

    def test_translation_force_is_zero(self):
        assert 0 == round(self.target.translation_part_of_force(), 6)

    def test_vector_does_not_move_object(self):
        x, y, z = self.target.translation_forces()
        assert 0 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)


class TestVectorThroughCenterOfMassFromRight(object):

    def setup(self):
        position = Offsets(1, 0, 0)
        direction = Degrees(0, -90, 0)
        forces = Offsets(-1, 0, 0)
        self.target = RotationalForce(position, forces)

    def test_position_direction_is_90(self):
        assert self.target.position.direction == Offsets(0, 90, 0)

    def test_all_force_is_translation_force(self):
        assert 1 == self.target.translation_part_of_force()

    def test_object_moves_left(self):
        x, y, z = self.target.translation_forces()
        assert -1 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)


class TestVectorThroughCenterOfMassFromLeft(object):

    def setup(self):
        position = Offsets(-1, 0, 0)
        forces = Offsets(1, 0, 0)
        self.target = RotationalForce(position, forces)

    def test_all_force_is_translation_force(self):
        assert 1 == self.target.translation_part_of_force()

    def test_object_moves_right(self):
        x, y, z = self.target.translation_forces()
        assert 1 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)

