from engine.physics.line import Line
from math import radians


class TestLineRotation(object):

    def setup(self):
        self.target = Line([(-1, 0), (1, 0)])

    def test_line_is_vertical(self):
        self.target.rotate(radians(90))
        assert round(self.target.x1, 4) == round(self.target.x2, 4)

    def test_line_is_same_length(self):
        self.target.rotate(radians(90))
        assert abs(round(self.target.dy, 4)) == 2

    def test_line_radi_is_zero(self):
        assert self.target.radii == radians(90)


class TestLineIntersection(object):

    def setup(self):
        line1 = Line([(-1, -1), (1, 1)])
        line2 = Line([(-1, 1), (1, -1)])
        self.target = line1.intersection_point(line2)

    def test_intersection_point_x_is_zero(self):
        assert round(self.target[1], 2) == 0

    def test_intersection_point_y_is_zero(self):
        assert round(self.target[2], 2) == 0

    def test_lines_intersects(self):
        assert self.target[0]


class _TestAnotherLineIntersection(object):

    def setup(self):
        line1 = Line([(-2, -3), (1, 0)])
        line2 = Line([(2, 3), (5, 0)])
        self.target = line1.intersection_point(line2)
        self.target2 = line2.intersection_point(line1)

    def test_intersection_point_x_is_3(self):
        assert round(self.target[1], 2) == 3
        assert round(self.target2[1], 2) == 3

    def test_intersection_point_y_is_2(self):
        assert round(self.target[2], 2) == 2
        assert round(self.target2[2], 2) == 2

    def test_lines_intersects(self):
        assert not self.target[0]
        assert not self.target2[0]


class TestLineInvertedIntersection(object):

    def setup(self):
        line1 = Line([(1, 1), (-1, -1)])
        line2 = Line([(-1, 1), (1, -1)])
        self.target = line1.intersection_point(line2)

    def test_intersection_point_x_is_zero(self):
        assert round(self.target[1], 2) == 0

    def test_intersection_point_y_is_zero(self):
        assert round(self.target[2], 2) == 0

    def test_lines_intersects(self):
        assert self.target[0]


class TestNonLineIntersection(object):
    def setup(self):
        line1 = Line([(-2, 0), (-1, 0)])
        line2 = Line([(0, -2), (0, -1)])
        self.target = line1.intersection_point(line2)

    def test_intersection_point_x_is_zero(self):
        assert round(self.target[1], 2) == 0

    def test_intersection_point_y_is_zero(self):
        assert round(self.target[2], 2) == 0

    def test_lines_intersects(self):
        assert not self.target[0]


class TestLineIntersectionMutation(object):
    def setup(self):
        self.line1 = Line([(-2, 0), (-1, 0)])
        self.line2 = Line([(0, -2), (0, -1)])
        self.line1.intersection_point(self.line2)

    def test_finding_intersection_point_does_not_alter_left_hand_line(self):
        assert self.line1.x1 == -2
        assert self.line1.x2 == -1
        assert self.line1.y1 == 0
        assert self.line1.y2 == 0

    def test_finding_intersection_point_does_not_alter_right_hand_line(self):
        assert self.line2.x1 == 0
        assert self.line2.x2 == 0
        assert self.line2.y1 == -2
        assert self.line2.y2 == -1


class TestLineIntersectionMutationOnHorizontalLine(object):

    def setup(self):
        self.line1 = Line([(-10, 0), (0, 0)])
        self.line2 = Line([(10, 0), (0, 0)])
        self.line1.intersection_point(self.line2)


    def test_finding_intersection_point_does_not_alter_left_hand_line(self):
        assert self.line1.x1 == -10
        assert self.line1.x2 == 0
        assert self.line1.y1 == 0
        assert self.line1.y2 == 0

    def test_finding_intersection_point_does_not_alter_right_hand_line(self):
        assert self.line2.x1 == 10
        assert self.line2.x2 == 0
        assert self.line2.y1 == 0
        assert self.line2.y2 == 0
