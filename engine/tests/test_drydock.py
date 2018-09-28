from engine.models.factories import ShipModelFactory
from engine.tests.fake_view_factory import FakeFactory
from engine.views.menus.drydock import Drydock


class TestDryDockSave(object):

    def setup(self):
        smf = ShipModelFactory()
        self.ship = smf.manufacture("ship")
        self.original_parts = self.ship.parts
        drydock = Drydock(0, 1, 0, 1, self.ship, FakeFactory())
        drydock.save_all()
        self.parts_after_save = self.ship.parts

    def test_saving_replaces_all_parts_on_ship(self):
        assert self.original_parts != self.parts_after_save

    def test_no_old_parts_are_present_on_ship_after_save(self):
        assert not (self.original_parts & self.parts_after_save)

    def test_new_parts_connect_to_new_parts(self):
        for part in self.parts_after_save:
            assert part.connected_parts
            assert not part.connected_parts - self.parts_after_save

    def test_nothing_observes_no_old_parts(self):
        for part in self.original_parts:
            for signal in ["working", "explode", "alive"]:
                part._prune_removed_observers(signal)
                assert not part._observers[signal]

    def test_ship_observes_new_parts(self):
        for part in self.parts_after_save:
            for signal in ["alive"]:
                part._introduce_new_observers(signal)
                assert part._observers[signal]
