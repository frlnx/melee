from engine.models.factories import AsteroidModelFactory


amf = AsteroidModelFactory()

class TestAsteroid(object):

    def setup(self):
        self.target = amf.manufacture([0, 0, 0])

    def test_is_big(self):
        assert self.target.bounding_box.left < -0.5
        assert self.target.bounding_box.right > 0.5
        assert self.target.bounding_box.top > 0.5
        assert self.target.bounding_box.bottom < -0.5
