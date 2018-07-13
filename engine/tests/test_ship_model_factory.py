from engine.models.factories import ShipModelFactory


factory = ShipModelFactory()


class TestShipModelFactory(object):

    def setup(self):
        self.model = factory.manufacture("ship")

    def test_bounding_box_is_the_sum_of_all_parts(self):
        assert self.model.bounding_box.left < -0.5
        assert self.model.bounding_box.right > 0.5

    def test_bouding_box_sub_polygons_are_not_all_the_same(self):
        assert 1 != len(set([(p.lines[0].x1, p.lines[0].y1) for p in self.model.bounding_box._polygons]))
