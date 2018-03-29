from engine.models.factories import ShipModelFactory
from engine.physics.line import Line
from itertools import chain


factory = ShipModelFactory()


class TestLine(object):

    def setup(self):
        self.target = Line([(0, 0), (10, 10)])

    def test_set_position_rotation(self):
        self.target.set_position_rotation(10, 0, 0)
        assert self.target.x1 == 10
        assert self.target.x2 == 20
        assert self.target.y1 == 0
        assert self.target.y2 == 10

    def test_freeze(self):
        self.target.set_position_rotation(10, 0, 0)
        self.target.freeze()
        assert self.target.x1 == 10
        assert self.target.x2 == 20
        assert self.target.y1 == 0
        assert self.target.y2 == 10

    def test_moving_after_freeze(self):
        self.target.set_position_rotation(10, 0, 0)
        self.target.freeze()
        self.target.set_position_rotation(10, 0, 0)
        assert self.target.x1 == 20
        assert self.target.x2 == 30
        assert self.target.y1 == 0
        assert self.target.y2 == 10


class TestBoundingBox(object):

    def setup(self):
        self.ship1 = factory.manufacture("wolf", position=[10, 0, 0])
        self.ship2 = factory.manufacture("wolf", position=[-10, 0, 0])

    def test_ships_do_not_overlap(self):
        collides, x, y = self.ship1.intersection_point(self.ship2)
        assert not collides

    def test_moving_ships_moves_bounding_box(self):
        bb_xes = list(chain(*[[line.x1, line.x2] for line in self.ship1.bounding_box.lines]))
        bb_yes = list(chain(*[[line.y1, line.y2] for line in self.ship1.bounding_box.lines]))
        self.ship1.set_position_and_rotation(0, 0, 0, 0, 0, 0)
        assert bb_xes == list(chain(*[[line.x1 - 10, line.x2 - 10] for line in self.ship1.bounding_box.lines]))
        assert bb_yes == list(chain(*[[line.y1, line.y2] for line in self.ship1.bounding_box.lines]))

