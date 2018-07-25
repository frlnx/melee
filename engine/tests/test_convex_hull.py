from engine.physics.polygon import Polygon


class TestConvexHullAngles(object):

    def setup(self):
        points = [(1, 1), (-1, 1), (-1, -1), (1, -1), (.1, .1), (-.1, .1), (-.1, -.1), (.1, -.1)]
        self.angles = Polygon.get_angles_for_points_from_point((0, 0), points)
        self.relative_angles = [Polygon.delta_angle(a, 90) for a in self.angles]

    def test_angles(self):
        assert [45.0, 135.0, -135.0, -45.0, 45.0, 135.0,  -135.0, -45.0] == self.angles

    def test_relative_angles(self):
        assert [-45.0, 45.0, 135.0, -135.0, -45.0, 45.0, 135.0, -135.0] == self.relative_angles


class TestConvexHull(object):

    def setup(self):
        points = [(0, 0), (1, 1), (-1, 1), (-1, -1), (1, -1), (.1, .1), (-.1, .1), (-.1, -.1), (.1, -.1)]
        self.hull = Polygon.convex_hull(points)

    def test_zero_not_in_hull(self):
        assert (0, 0) not in self.hull

    def test_hull_has_four_points(self):
        assert len(self.hull) == 4

    def test_hull(self):
        assert {(1, 1), (-1, 1), (-1, -1), (1, -1)} == set(self.hull)

