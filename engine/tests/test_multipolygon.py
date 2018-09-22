from engine.physics.polygon import MultiPolygon, PolygonPart


class TestMultiPolygonMovement(object):

    def setup(self):
        self.polygon_part = PolygonPart.manufacture([(0, 0), (2, 0), (2, 2), (0, 2)], x=1, y=1)
        self.polygon_part.set_position_rotation(1, 1, 0)
        self.polygon_part.freeze()
        self.target = MultiPolygon([self.polygon_part])

    def test_creation(self):
        assert self.polygon_part.x == 0
        assert self.polygon_part.y == 0
        assert self.target.x == 0
        assert self.target.y == 0

    def test_centroid(self):
        assert 2, 2 == self.polygon_part._centroid()

    def test_movement_keeps_each_polygons_offsets_in_mind(self):
        self.target.set_position_rotation(10, 10, 0)
        assert (12, 12) == self.polygon_part._centroid()


class TestMultiPolygonCollision(object):

    def setup(self):
        coords = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        polygons = {PolygonPart.manufacture(coords, x=px, y=py) for px, py in coords}
        target = MultiPolygon(polygons)
        collider = MultiPolygon.manufacture([(-.9, -10), (-.9, -10)])
        collider.set_position_rotation(-.9, 20, 0)
        self.polygon_part_sets = target.intersected_polygons(collider)
        self.polygon_part_sets_reversed = collider.intersected_polygons(target)

    def test_polygon_parts_are_reversed_when_called_in_reverse(self):
        first, second = self.polygon_part_sets
        assert (second, first) == self.polygon_part_sets_reversed

    def test_two_collisions_on_target(self):
        target_set, _ = self.polygon_part_sets
        assert 2 == len(target_set)

    def test_one_collision_on_collider(self):
        _, collider_set = self.polygon_part_sets
        assert 1 == len(collider_set)

    def test_polygons_at_minus_one_got_hit(self):
        target_set, collider_set = self.polygon_part_sets
        assert all([p.x == -1 for p in target_set])
