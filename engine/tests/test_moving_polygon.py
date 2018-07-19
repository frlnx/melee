from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.moving_shapes import MovingPolygon


class TestMovingPolygonCollisions(object):

    def setup(self):
        coords = [(1, 0), (1, 1), (0, 1), (0, 0)]
        left_movement = MutableOffsets(1, 0, 0)
        right_movement = MutableOffsets(-1, 0, 0)
        spin = MutableDegrees(0, 0, 0)
        self.left = MovingPolygon.manufacture_moving_polygon(coords, movement=left_movement, spin=spin, x=-10, y=0)
        self.right = MovingPolygon.manufacture_moving_polygon(coords, movement=right_movement, spin=spin, x=10, y=0)

    def test_bounding_boxes_does_not_collide_after_one_second(self):
        collides = self.left.bounding_box_intersects_in_timeframe(self.right, 1.0)
        assert not collides

    def test_bounding_boxes_collides_after_ten_seconds(self):
        collides = self.left.bounding_box_intersects_in_timeframe(self.right, 10.0)
        assert collides

    def test_no_intersection_occurs_after_one_second(self):
        collides, x, y, time = self.left.intersection_point_in_timeframe(self.right, 1.0)
        assert not collides

    def _test_intersection_occurs_after_nine_seconds(self):
        collides, times = self.left.intersection_point_in_timeframe(self.right, 10.0)
        assert collides
        assert round(list(times)[0], 4) == 9
