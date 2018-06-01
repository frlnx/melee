from math import radians, degrees, atan2

from engine.input_handlers import InputHandler
from engine.models.factories import ShipModelFactory
from engine.physics.force import MutableOffsets, MutableForce

model_factory = ShipModelFactory()
dummy_input = InputHandler()


class TestBoundingBox(object):

    def setup(self):
        ship = model_factory.manufacture("ship")
        self.target = ship.bounding_box
        ship.set_position_and_rotation(10, 0, 10, 0, 0, 0)

    def test_bounding_box_width_is_5(self):
        assert 5.4 == round(self.target.right - self.target.left, 1)

    def _test_bounding_box_height_is_3(self):
        assert self.target.top - self.target.bottom == 2

    def test_bounding_box_x_is_at_10(self):
        xes = [line.x for line in self.target.lines]
        assert all([x == 10 for x in xes])

    def test_bounding_box_y_is_at_10(self):
        yes = [line.y for line in self.target.lines]
        assert all([y == 10 for y in yes])

    def test_bounding_box_lines_coords_have_moved_10_right_and_10_down(self):
        reference_bb = model_factory.manufacture("ship").bounding_box
        for actual, original in zip(self.target.lines, reference_bb.lines):
            assert actual.x1 == original.x1 + 10
            assert actual.y1 == original.y1 + 10
            assert actual.x2 == original.x2 + 10
            assert actual.y2 == original.y2 + 10



class TestCollisions(object):

    def setup(self):
        self.target1 = model_factory.manufacture("ship")
        self.target2 = model_factory.manufacture("ship")

    def test_collision_on_same_location(self):
        assert self.target1.intersection_point(self.target2)[0]
        assert self.target2.intersection_point(self.target1)[0]

    def test_collision_on_translation(self):
        self.target2.set_position(1, 0, 0)
        self.target2.bounding_box.clear_movement()
        assert self.target1.intersection_point(self.target2)[0]
        assert self.target2.intersection_point(self.target1)[0]

    def test_collision_on_rotation(self):
        self.target2.set_rotation(0, 90, 0)
        self.target2.bounding_box.clear_movement()
        assert self.target1.intersection_point(self.target2)[0]
        assert self.target2.intersection_point(self.target1)[0]

    def test_collision_on_rotation_and_translation(self):
        self.target2.set_position(1, 0, 0)
        self.target2.set_rotation(0, 90, 0)
        self.target2.bounding_box.clear_movement()
        assert self.target1.intersection_point(self.target2)[0]
        assert self.target2.intersection_point(self.target1)[0]

    def test_non_collision_on_big_translation(self):
        self.target2.set_position(100, 0, 0)
        self.target2.bounding_box.clear_movement()
        assert not self.target1.intersection_point(self.target2)[0]
        assert not self.target2.intersection_point(self.target1)[0]


class TestGlobalMomentumAt(object):

    def setup(self):
        self.target = model_factory.manufacture("ship")
        self.target.set_position(-2, 0, 0)

    def test_force_on_right_side_is_the_movement_of_target_times_mass(self):
        self.target.set_movement(1, 0, 0)
        force = self.target.global_momentum_at(MutableOffsets(2, 0, 0))
        assert force.forces.x == 1 #* self.target.mass
        assert force.forces.y == 0 #* self.target.mass
        assert force.forces.z == 0 #* self.target.mass

    def test_tangent_force_on_right_side_spins_clockwise_when_positive_yaw_is_applied(self):
        yaw_degrees_per_second = 1
        self.target.set_spin(0, yaw_degrees_per_second, 0)
        momentum = self.target.tangent_momentum_at(MutableOffsets(2, 0, 0))
        assert momentum.z > 0

    def _test_force_on_right_side_is_the_spin_of_target_times_mass(self):
        yaw_degrees_per_second = 1
        yaw_radians_per_second = radians(yaw_degrees_per_second)
        measure_point = MutableOffsets(2, 0, 0)
        distance_to_measure_point = measure_point.distance
        rotation_speed_at_distance = distance_to_measure_point * yaw_radians_per_second
        self.target.set_spin(0, yaw_degrees_per_second, 0)
        force = self.target.global_momentum_at(measure_point)
        assert round(force.forces.x, 2) == 0
        assert round(force.forces.y, 2) == 0
        assert round(force.forces.z, 2) == round(rotation_speed_at_distance * self.target.inertia, 2)


class TestApplyForce(object):

    def setup(self):
        self.target = model_factory.manufacture("ship")

    def test_force_applied_to_center_of_mass_does_not_rotate(self):
        force = MutableForce(MutableOffsets(2, 0, 0), MutableOffsets(-1, 0, 0))
        force.set_force(1.0)
        self.target.apply_global_force(force)
        x, y, z = self.target.spin
        assert (round(x, 2), round(y, 2), round(z, 2)) == (0, 0, 0)

    def test_force_applied_to_center_of_mass_translates(self):
        force = MutableForce(MutableOffsets(2, 0, 0), MutableOffsets(-1, 0, 0))
        force.set_force(1.0)
        self.target.apply_global_force(force)
        x, y, z = self.target.movement
        assert (round(x, 1), round(y, 1), round(z, 1)) == (-0.1, 0, 0)

    def _test_force_applied_lateral_to_center_of_mass_rotates_and_moves(self):
        x_offset = 2
        z_offset = -1
        degrees_at_offset = round(degrees(atan2(z_offset, x_offset)), 2)
        force = MutableForce(MutableOffsets(x_offset, 0, 0), MutableOffsets(0, 0, z_offset))
        force.set_force(1.0)
        assert force.diff_yaw_of_force_to_pos() == 90
        assert round(force.delta_yaw, 2) == degrees_at_offset
        self.target.apply_global_force(force)
        pitch, yaw, roll = self.target.spin
        assert (round(pitch, 2), round(yaw, 2), round(roll, 2)) == \
               (0, round(degrees_at_offset / self.target.inertia, 2), 0)


class TestForceTranslationGlobalLocal(object):

    def setup(self):
        self.ship_model = model_factory.manufacture("ship", position=(10, 0, 10))
        self.target = MutableForce(MutableOffsets(9, 0, 9), MutableOffsets(0, 0, -1))
        self.target.set_force(1.0)
        self.ship_model.mutate_force_to_local(self.target)

    def test_force_position_is_minus_one_in_x_and_z(self):
        assert self.target.position.x == -1
        assert self.target.position.z == -1

    def test_force_direction_is_unchanged(self):
        assert self.target.forces.x == 0
        assert self.target.forces.z == -1


class TestForceTranslationGlobalLocalWithRotation(object):

    def setup(self):
        self.ship_model = model_factory.manufacture("ship", position=(10, 0, 10), rotation=(0, 45, 0))
        self.target = MutableForce(MutableOffsets(9, 0, 9), MutableOffsets(0, 0, -1))
        self.target.set_force(1.0)
        self.ship_model.mutate_force_to_local(self.target)

    def test_force_position_is_minus_one_in_x_and_z(self):
        assert round(self.target.position.x, 2) == 0
        assert round(self.target.position.z, 2) == -1.41

    def test_force_direction_is_rotated(self):
        assert round(self.target.forces.x, 2) == .71
        assert round(self.target.forces.z, 2) == -.71


class TestForceTranslationLocalGlobal(object):

    def setup(self):
        self.ship_model = model_factory.manufacture("ship", position=(10, 0, 10))
        self.target = MutableForce(MutableOffsets(-1, 0, -1), MutableOffsets(0, 0, -1))
        self.target.set_force(1.0)
        self.ship_model.mutate_force_to_global(self.target)

    def test_force_position_is_nine_in_x_and_z(self):
        assert round(self.target.position.x, 2) == 9
        assert round(self.target.position.z, 2) == 9

    def test_force_direction_is_unchanged(self):
        assert round(self.target.forces.x, 2) == 0
        assert round(self.target.forces.z, 2) == -1


class TestForceTranslationLocalGlobalWithRotation(object):

    def setup(self):
        self.ship_model = model_factory.manufacture("ship", position=(10, 0, 10), rotation=(0, 45, 0))
        self.target = MutableForce(MutableOffsets(-1, 0, -1), MutableOffsets(0, 0, -1))
        self.target.set_force(1.0)
        self.ship_model.mutate_force_to_global(self.target)

    def test_force_position_is_minus_one_in_x_and_z(self):
        assert round(self.target.position.x, 2) == (10 - 1.41)
        assert round(self.target.position.z, 2) == 10

    def test_force_direction_is_rotated(self):
        assert round(self.target.forces.x, 2) == -.71
        assert round(self.target.forces.z, 2) == -.71
