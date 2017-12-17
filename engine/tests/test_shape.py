from engine.physics.shape import Quad


class TestQuadRotation(object):

    def setup(self):
        self.target = Quad([(-1, -1), (1, -1), (1, 1), (-1, 1)])

    def test_rotation_without_translation_gives_right_coords(self):
        self.target.set_position_rotation(0, 0, 45)
        actual = [(round(x, 2), round(y, 2)) for x, y in self.target._coords]
        assert [(0, -1.41), (1.41, 0), (0, 1.41), (-1.41, 0)] == actual

    def test_rotation_with_translation_gives_right_coords(self):
        self.target.set_position_rotation(1, 1, 45)
        actual = [(round(x, 2), round(y, 2)) for x, y in self.target._coords]
        assert [(1, -.41), (2.41, 1), (1, 2.41), (-.41, 1)] == actual

    def test_outer_bounds_after_rotation(self):
        bounding_box = self.target.outer_bounds_after_rotation(45)
        assert -1.41 == round(bounding_box.left, 2)
        assert 1.41 == round(bounding_box.right, 2)
        assert -1.41 == round(bounding_box.bottom, 2)
        assert 1.41 == round(bounding_box.top, 2)


class TestQuadStraightIntersection(object):

    def setup(self):
        self.q1 = Quad([(-1, -1), (1, -1), (1, 1), (-1, 1)])
        self.q2 = Quad([(0, -1), (2, -1), (2, 1), (0, 1)])

    def test_intersects_on_outer_bounds(self):
        assert self.q1.outer_bounding_box.intersects(self.q2.outer_bounding_box)

    def test_intersects_on_outer_bounds_after_rotation(self):
        assert self.q1.outer_bounds_after_rotation(45).intersects(self.q2.outer_bounding_box)


class TestQuadSkewedIntersection(object):

    def setup(self):
        self.q1 = Quad([(-1, -1), (1, -1), (1, 1), (-1, 1)])
        self.q2 = Quad([(0, -1), (2, -1), (2, 1), (0, 1)])

    def test_intersects_on_outer_bounds(self):
        assert self.q1.outer_bounding_box.intersects(self.q2.outer_bounding_box)
