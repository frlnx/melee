from engine.models.factories import ShipModelFactory


factory = ShipModelFactory()

class TestShipModelFactory(object):

    def setup(self):
        self.model = factory.manufacture("wolf")

    def test_bounding_box_is_the_sum_of_all_parts(self):
        assert self.model.bounding_box.left < -0.5
        assert self.model.bounding_box.right > 0.5
