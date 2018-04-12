from engine.physics.moving_shapes import MovingLine
from engine.physics.force import MutableOffsets, MutableDegrees


class TestMovingLineIntersection(object):

    def setup(self):
        movement = MutableOffsets(-1, 0, -1)
        spin = MutableDegrees(0, 0, 0)
        self.right_line = MovingLine([(10, 10), (10, 11)], movement, spin)
        movement = MutableOffsets(1, 0, -1)
        self.left_line = MovingLine([(-10, 10), (-10, 11)], movement, spin)
        self.target = self.right_line.time_to_impact(self.left_line)

    def test_impacts_after_ten_seconds(self):
        assert self.target == 10.0
