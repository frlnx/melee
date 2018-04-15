from engine.physics.moving_shapes import MovingLine
from engine.physics.force import MutableOffsets, MutableDegrees


class TestMovingLineIntersection(object):

    def setup(self):
        movement = MutableOffsets(-1, 0, 0)
        spin = MutableDegrees(0, 0, 0)
        self.target_line = MovingLine([(-1, 1), (1, -1)], movement, spin)

    def test_delta_movement(self):
        movement = MutableOffsets(-2, 0, -0.01)
        spin = MutableDegrees(0, 0, 0)
        impacting_line = MovingLine([(10, 0), (11, 1)], movement, spin)
        actual = impacting_line.movement_in_relation_to(self.target_line)
        assert actual.x == -1
        assert actual.y == 0
        assert actual.z == -0.01

    def test_line_touching_target_center_with_first_coord(self):
        movement = MutableOffsets(-2, 0, 0)
        spin = MutableDegrees(0, 0, 0)
        impacting_line = MovingLine([(10, 0), (11, 1)], movement, spin)
        target = impacting_line.time_to_impact(self.target_line)
        assert round(target, 2) == 10.0

    def test_line_touching_target_center_with_second_coord(self):
        movement = MutableOffsets(-2, 0, 0)
        spin = MutableDegrees(0, 0, 0)
        impacting_line = MovingLine([(11, 1), (10, 0)], movement, spin)
        target = impacting_line.time_to_impact(self.target_line)
        assert round(target, 2) == 10.0

    def test_delta_movement2(self):
        movement = MutableOffsets(-0.5, 0, -0.5)
        spin = MutableDegrees(0, 0, 0)
        impacting_line = MovingLine([(-11, -9), (-9, -11)], movement, spin)
        actual = impacting_line.movement_in_relation_to(self.target_line)
        assert actual.x == 0.5
        assert actual.y == 0
        assert actual.z == -0.5

    def test_line_touching_target_with_own_center(self):
        # Test may be correct, should fail with this code...
        movement = MutableOffsets(-0.5, 0, -0.5)
        spin = MutableDegrees(0, 0, 0)
        impacting_line = MovingLine([(-11, -9), (-9, -11)], movement, spin)
        target = impacting_line.time_to_impact(self.target_line)
        assert round(target, 2) == 10.0
