from engine.physics.polygon import Polygon


class TestPolygonManufacture(object):

    def setup(self):
        self.target = Polygon.manufacture([(-5, 0), (-2, -3), (1, 0), (-2, 3)])

    def test_polygon_has_four_lines(self):
        assert len(self.target.lines) == 4


class TestPolygonIntersection(object):

    def setup(self):
        poly1 = Polygon.manufacture([(-5, 0), (-2, -3), (1, 0), (-2, 3)])
        poly2 = Polygon.manufacture([(5, 0), (2, -3), (-1, 0), (2, 3)])
        self.bb_intersection = poly1.bounding_box_intersects(poly2)
        self.intersects, self.x, self.y = poly1.intersection_point(poly2)

    def test_bb_intersection(self):
        assert self.bb_intersection

    def test_polygons_intersect(self):
        assert self.intersects

    def test_intersection_is_at_origo(self):
        assert round(self.x, 2) == 0
        assert round(self.y, 2) == 0

class TestPolygonMovement(object):

    def setup(self):
        self.target = Polygon.manufacture([(-5, -5), (5, -5), (5, 5), (-5, 5)])

    def test_moving_left_moves_all_lines_left(self):
        self.target.set_position_rotation(-1, 0, 0)
        assert set([line.x1 for line in self.target.lines]) == {-6, 4}

    def test_moving_left_and_freezing_moves_all_original_xes_of_lines_left(self):
        self.target.set_position_rotation(-1, 0, 0)
        self.target.freeze()
        assert set([line.original_x1 for line in self.target.lines]) == {-6, 4}