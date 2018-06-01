from engine.physics.moving_shapes import MovingLine
from engine.physics.force import MutableOffsets, MutableDegrees
import pytest


@pytest.mark.parametrize("y,expected", [(-10, None), (-5, 10), (0, 10), (5, 10), (10, None)])
def _test_collision_while_moving_right(y, expected):
    right_movement = MutableOffsets(1, 0, 0)
    no_movement = MutableOffsets(0, 0, 0)
    no_spin = MutableDegrees(0, 0, 0)
    target_line = MovingLine([(10, -5), (10, 5)], no_movement, no_spin)
    moving_line = MovingLine([(0, -1 + y), (0, 1 + y)], right_movement, no_spin)
    assert moving_line.time_to_impact(target_line) == expected


@pytest.mark.parametrize("y,expected", [(-10, None), (-5, -10), (0, -10), (5, -10), (10, None)])
def _test_collision_in_the_past_while_moving_left(y, expected):
    left_movement = MutableOffsets(-1, 0, 0)
    no_movement = MutableOffsets(0, 0, 0)
    no_spin = MutableDegrees(0, 0, 0)
    target_line = MovingLine([(10, -5), (10, 5)], no_movement, no_spin)
    moving_line = MovingLine([(0, -1 + y), (0, 1 + y)], left_movement, no_spin)
    assert moving_line.time_to_impact(target_line) == expected


@pytest.mark.parametrize("x,expected", [(-10, None), (0, 5), (10, None)])
def _test_coming_right_down_on_target(x, expected):
    down_movement = MutableOffsets(0, 0, 1)
    no_movement = MutableOffsets(0, 0, 0)
    no_spin = MutableDegrees(0, 0, 0)
    target_line = MovingLine([(0, -5), (0, 5)], no_movement, no_spin)
    moving_line = MovingLine([(-1 + x, -10), (1 + x, -10)], down_movement, no_spin)
    assert moving_line.time_to_impact(target_line) == expected

@pytest.mark.parametrize("x,expected", [(-10, None), (0, 5), (10, None)])
def _test_coming_right_down_on_target_inversed(x, expected):
    down_movement = MutableOffsets(0, 0, 1)
    no_movement = MutableOffsets(0, 0, 0)
    no_spin = MutableDegrees(0, 0, 0)
    target_line = MovingLine([(0, -5), (0, 5)], no_movement, no_spin)
    moving_line = MovingLine([(-1 + x, -10), (1 + x, -10)], down_movement, no_spin)
    assert target_line.time_to_impact(moving_line) == expected


class _TestMovingLineIntersection(object):

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
        movement = MutableOffsets(-0.5, 0, -0.5)
        spin = MutableDegrees(0, 0, 0)
        impacting_line = MovingLine([(-11, -9), (-9, -11)], movement, spin)
        target = impacting_line.time_to_impact(self.target_line)
        assert round(target, 2) == 10.0

    def test_line_touching_target_with_own_center_inverse(self):
        movement = MutableOffsets(-0.5, 0, -0.5)
        spin = MutableDegrees(0, 0, 0)
        impacting_line = MovingLine([(-11, -9), (-9, -11)], movement, spin)
        target = self.target_line.time_to_impact(impacting_line)
        assert round(target, 2) == 10.0
