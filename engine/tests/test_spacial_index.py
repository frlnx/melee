from engine.models.factories import ShipModelFactory
from engine.physics.spacial_index import SpacialIndex


class TestSpacialIndexAtZero(object):

    def setup(self):
        self.target = SpacialIndex()
        smf = ShipModelFactory()
        self.ship = smf.manufacture('ship')
        self.target.init_model_into_2d_space_index(self.ship)

    def test_ship_occupies_zero_and_minus_one(self):
        assert {(0, 0), (0, -1), (-1, -1), (-1, 0)} == self.ship.bounding_box.quadrants

    def test_zero_and_minus_one_holds_ship(self):
        assert {self.ship} == self.target.all_models([(0, 0)])
        assert {self.ship} == self.target.all_models([(-1, 0)])
        assert {self.ship} == self.target.all_models([(-1, -1)])
        assert {self.ship} == self.target.all_models([(0, -1)])

    def test_anything_outside_zero_and_minus_one_is_empty(self):
        assert set() == self.target.all_models([(1, 0)])
        assert set() == self.target.all_models([(1, -1)])
        assert set() == self.target.all_models([(-2, 0)])
        assert set() == self.target.all_models([(-2, -1)])
        assert set() == self.target.all_models([(0, 1)])
        assert set() == self.target.all_models([(-1, 1)])
        assert set() == self.target.all_models([(0, -2)])
        assert set() == self.target.all_models([(-1, -2)])


class TestSpacialIndexAfterHullRebuild(object):

    def setup(self):
        self.target = SpacialIndex()
        smf = ShipModelFactory()
        self.ship = smf.manufacture('ship')
        self.target.init_model_into_2d_space_index(self.ship)
        list(self.ship.parts)[0].explode()

    def test_ship_occupies_zero_and_minus_one(self):
        assert {(0, 0), (0, -1), (-1, -1), (-1, 0)} == self.ship.bounding_box.quadrants

    def test_zero_and_minus_one_holds_ship(self):
        assert {self.ship} == self.target.all_models([(0, 0)])
        assert {self.ship} == self.target.all_models([(-1, 0)])
        assert {self.ship} == self.target.all_models([(-1, -1)])
        assert {self.ship} == self.target.all_models([(0, -1)])

    def test_anything_outside_zero_and_minus_one_is_empty(self):
        assert set() == self.target.all_models([(1, 0)])
        assert set() == self.target.all_models([(1, -1)])
        assert set() == self.target.all_models([(-2, 0)])
        assert set() == self.target.all_models([(-2, -1)])
        assert set() == self.target.all_models([(0, 1)])
        assert set() == self.target.all_models([(-1, 1)])
        assert set() == self.target.all_models([(0, -2)])
        assert set() == self.target.all_models([(-1, -2)])


class TestSpacialIndexCollisionPairGeneration(object):

    def setup(self):
        self.target = SpacialIndex()
        smf = ShipModelFactory()
        self.ship = smf.manufacture('ship')
        self.target.init_model_into_2d_space_index(self.ship)
        self.ship2 = smf.manufacture('ship')
        self.target.init_model_into_2d_space_index(self.ship2)
        self.pairs = self.target.all_pairs_deduplicated({self.ship, self.ship2})

    def test_ship_and_ship2_has_same_quadrants(self):
        assert self.ship.bounding_box.quadrants == self.ship2.bounding_box.quadrants

    def test_ship2_is_other_model_to_ship(self):
        assert {self.ship2} == self.target.other_models(self.ship)

    def test_ship_and_ship2_are_paired_once(self):
        assert {(self.ship, self.ship2)} == self.pairs or {(self.ship2, self.ship)} == self.pairs
