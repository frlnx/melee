from math import pi

from engine.physics.force import Offsets, Degrees, Force


class TestPosition(object):

    def setup(self):
        self.target = Offsets(1, 0, 0)

    def test_distance_is_one(self):
        assert 1 == self.target.distance

    def test_angle_is_yaw_90(self):
        assert [0, -90, 0] == self.target.direction.xyz.tolist()


class TestLeftRotationalPhysicsVector(object):

    def setup(self):
        position = Offsets(1, 0, 0)
        forces = Offsets(0, 0, -1)
        self.target = Force(position, forces)

    def test_position_direction(self):
        assert self.target.position.direction.xyz.tolist() == [0, -90, 0]

    def test_force_direction(self):
        assert self.target.forces.direction.xyz.tolist() == [0, 0, 0]

    def test_diff(self):
        assert self.target.diff_yaw_of_force_to_pos() == 90

    def test_vector_impacts_yaw_positively(self):
        assert 0 < self.target.yaw_momentum

    def test_c_radian(self):
        assert self.target.c_radian() == 0

    def test_vector_does_not_move_object(self):
        x, y, z = self.target.translation_forces()
        assert 0 == round(x, 6)
        assert 0 == round(y, 6)
        assert -1 == round(z, 6)


class TestRightRotationalPhysicsVector(object):

    def setup(self):
        position = Offsets(-1, 0, 0)
        forces = Offsets(0, 0, -1)
        self.target = Force(position, forces)

    def test_position_direction(self):
        assert self.target.position.direction.xyz.tolist() == [0, 90, 0]

    def test_force_direction(self):
        assert self.target.forces.direction.xyz.tolist() == [0, 0, 0]

    def test_vector_impacts_yaw_negatively(self):
        assert 0 > self.target.yaw_momentum

    def test_vector_does_not_move_object(self):
        x, y, z = self.target.translation_forces()
        assert 0 == round(x, 6)
        assert 0 == round(y, 6)
        assert -1 == round(z, 6)


class TestVectorThroughCenterOfMassFromRight(object):

    def setup(self):
        position = Offsets(1, 0, 0)
        forces = Offsets(-1, 0, 0)
        self.target = Force(position, forces)
        self.target.force_multiplier = 1.0

    def test_position_direction_is_90(self):
        assert self.target.position.direction == Offsets(0, -90, 0)

    def test_object_moves_left(self):
        x, y, z = self.target.translation_forces()
        assert -1 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)


class TestVectorThroughCenterOfMassFromLeft(object):

    def setup(self):
        position = Offsets(-1, 0, 0)
        forces = Offsets(1, 0, 0)
        self.target = Force(position, forces)
        self.target.force_multiplier = 1.0

    def test_object_moves_right(self):
        x, y, z = self.target.translation_forces()
        assert 1 == round(x, 6)
        assert 0 == round(y, 6)
        assert 0 == round(z, 6)


class TestForceAtPositiveXAndYOffset(object):

    def setup(self):
        position = Offsets(1, 0, 1)
        forces = Offsets(0, 0, -1)
        self.target = Force(position, forces)
        self.target.force_multiplier = 1.0

    def test_object_moves_forwards(self):
        x, y, z = self.target.translation_forces()
        assert 0 == round(x, 6)
        assert 0 == round(y, 6)
        assert -1.0 == round(z, 1)

    def test_rotational_force_rotates_positive_yaw(self):
        assert self.target.yaw_momentum > 0


class TestForceAtNegativeXAndYOffset(object):

    def setup(self):
        position = Offsets(-1, 0, -1)
        forces = Offsets(0, 0, -1)
        self.target = Force(position, forces)
        self.target.force_multiplier = 1.0

    def test_object_moves_forwards(self):
        x, y, z = self.target.translation_forces()
        assert 0 == round(x, 6)
        assert 0 == round(y, 6)
        assert -1.0 == round(z, 1)

    def test_rotational_force_rotates_positive_yaw(self):
        assert self.target.yaw_momentum < 0


class TestSumTwoRotationalForces(object):

    def setup(self):
        self.left_force = Force(Offsets(-1, 0, 0), Offsets(0, 0, -1))
        self.right_force = Force(Offsets(1, 0, 0), Offsets(0, 0, -1))
        self.force = self.left_force + self.right_force
        self.force.force_multiplier = 1.0

    def test_position_of_summed_forces_is_origo(self):
        assert self.force.position == Offsets(0, 0, 0)

    def test_force_of_summed_forces_is_two_forwards(self):
        assert self.force.forces == Offsets(0, 0, -2)


class TestSumTwoNegativeRotationalForces(object):

    def setup(self):
        self.left_force = Force(Offsets(-1, 0, 0), Offsets(0, 0, -1))
        self.right_force = Force(Offsets(1, 0, 0), Offsets(0, 0, -1))
        self.force = self.left_force + self.right_force
        self.force.force_multiplier = 1.0

    def test_position_of_summed_forces_is_origo(self):
        assert self.force.position == Offsets(0, 0, 0)

    def test_force_of_summed_forces_is_two_forwards(self):
        assert self.force.forces == Offsets(0, 0, -2)

    def test_force_does_not_rotate(self):
        assert round(self.force.yaw_momentum, 4) == 0


class TestHorizontalForce45DegreesOff(object):

    def setup(self):
        position = Offsets(1, 0, -1)
        forces = Offsets(-1, 0, 0)
        self.target = Force(position, forces)
        self.target.force_multiplier = 1.0

    def test_object_moves_left(self):
        x, y, z = self.target.translation_forces()
        assert -1.0 == round(x, 1)
        assert 0 == round(y, 6)
        assert 0 == round(z, 1)


class TestRotatingAForce(object):

    def setup(self):
        position = Offsets(1, 0, -1)
        forces = Offsets(-1, 0, 0)
        self.target = Force(position, forces)
        self.target.force_multiplier = 1.0

    def test_no_rotation_changes_nothing(self):
        target = self.target.rotated(0)
        assert target.forces == self.target.forces
        assert target.position == self.target.position

    def test_positive_rotation_90_degrees_rotates_forces(self):
        target = self.target.rotated(90)
        assert round(target.forces.x, 3) == 0
        assert target.forces.y == 0
        assert target.forces.z == -1
