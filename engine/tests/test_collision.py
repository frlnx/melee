from itertools import chain

import pytest

from engine.models.factories import ShipModelFactory, AsteroidModelFactory
from engine.physics.line import Line

factory = ShipModelFactory()
amf = AsteroidModelFactory()


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
        self.ship1 = factory.manufacture("ship", position=[10, 0, 0])
        self.ship2 = factory.manufacture("ship", position=[-10, 0, 0])

    def test_ships_do_not_overlap(self):
        collides, x, y = self.ship1.intersection_point(self.ship2)
        assert not collides

    def test_moving_ships_moves_bounding_box(self):
        bb_xes = list(chain(*[[line.x1, line.x2] for line in self.ship1.bounding_box.lines]))
        bb_yes = list(chain(*[[line.y1, line.y2] for line in self.ship1.bounding_box.lines]))
        self.ship1.set_position_and_rotation(0, 0, 0, 0, 0, 0)
        self.ship1.update_bounding_box()
        moved_coords = list(chain(*[[line.x1, line.x2] for line in self.ship1.bounding_box.lines]))
        assert bb_xes != list(chain(*[[line.x1, line.x2] for line in self.ship1.bounding_box.lines]))
        assert [round(x - 10, 1) for x in bb_xes] == [round(x, 1) for x in moved_coords]
        assert bb_yes == list(chain(*[[line.y1, line.y2] for line in self.ship1.bounding_box.lines]))


class TestAsteroidShipCollision(object):

    def setup(self):
        self.asteroid = amf.manufacture(position=[-50, 0, 0])
        self.ship = factory.manufacture("ship", position=[10, 0, 0])

    def test_asteroid_has_no_movement(self):
        assert all(p[0] < 0 for p in self.asteroid.bounding_box._moving_points)
        assert self.asteroid.bounding_box.moving_right < 0
        for bb in self.asteroid.bounding_box:
            assert all(p[0] < 0 for p in bb._moving_points)
            assert bb.moving_right < 0

    def test_collision(self):
        self.ship.set_position(-50, 0, 0)
        self.ship.update_bounding_box()
        my_parts, asteroid_parts = self.ship.intersected_polygons(self.asteroid)
        assert 0 < len(my_parts)
        assert 1 == len(asteroid_parts)


test_data = [
    (
        amf.manufacture(position=(-50, 0, 0), rotation=(0, d, 0)),
        factory.manufacture("ship", position=(50, 0, 0))
    ) for d in range(0, 360, 10)]


@pytest.mark.parametrize("asteroid,ship", test_data)
def test_collision_360(asteroid, ship):
    ship.set_position(-50, 0, 0)
    ship.update_bounding_box()
    my_parts, asteroid_parts = ship.intersected_polygons(asteroid)
    assert 0 < len(my_parts)
    assert 1 == len(asteroid_parts)
