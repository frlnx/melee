from unittest.mock import MagicMock

from engine.models import ShipModel
from engine.models.factories import ShipPartModelFactory
from engine.physics.force import MutableDegrees, MutableOffsets
from engine.tests.fake_view_factory import FakeFactory
from engine.views.menus.drydock import Drydock, DockableItem


class TestReconnection(object):

    def setup(self):
        spmf = ShipPartModelFactory()
        null_offset = MutableOffsets(0, 0, 0)
        null_rotation = MutableDegrees(0, 0, 0)
        self.target = spmf.manufacture("generator", position=(10, 0, 0))
        self.cockpit = spmf.manufacture("cockpit")
        parts = {self.cockpit, self.target}
        self.ship = ShipModel("foo", parts, null_offset.__copy__(), null_rotation.__copy__(), null_offset.__copy__(),
                              null_rotation.__copy__(), null_offset.__copy__(), null_rotation.__copy__())

    def test_distance(self):
        self.target.teleport_to(1, 0, 0)
        assert list(self.ship._connections)[0].distance == 1

    def test_inital_state_is_unconnected(self):
        assert set() == self.ship._connections
        assert set() == self.target.connected_parts

    def test_moving_part_closer_connects_it(self):
        self.target.teleport_to(1, 0, 0)
        assert 1 == len(self.ship._connections)
        assert {self.cockpit} == self.target.connected_parts

    def test_disconnecting(self):
        self.target.teleport_to(1, 0, 0)
        self.target.teleport_to(10, 0, 0)
        assert set() == self.ship._connections
        assert set() == self.target.connected_parts

    def test_reconnecting(self):
        self.target.teleport_to(1, 0, 0)
        self.target.teleport_to(10, 0, 0)
        self.target.teleport_to(1, 0, 0)
        assert 1 == len(self.ship._connections)
        assert {self.cockpit} == self.target.connected_parts


class TestDrydockReconnection(object):

    def setup(self):
        spmf = ShipPartModelFactory()
        null_offset = MutableOffsets(0, 0, 0)
        null_rotation = MutableDegrees(0, 0, 0)
        target = spmf.manufacture("generator", position=(10, 0, 0))
        cockpit = spmf.manufacture("cockpit")
        parts = {cockpit, target}
        self.ship = ShipModel("foo", parts, null_offset.__copy__(), null_rotation.__copy__(), null_offset.__copy__(),
                              null_rotation.__copy__(), null_offset.__copy__(), null_rotation.__copy__())
        self.drydock = Drydock(0, 1000, 0, 1000, self.ship, view_factory=FakeFactory())
        self.ship = self.drydock.ship
        self.target_item: DockableItem = [item for item in self.drydock.items if item.model.name == "generator"][0]
        self.target_item.held = True
        self.target_item._highlight = True
        self.target = self.target_item.model
        self.cockpit_item: DockableItem = [item for item in self.drydock.items if item.model.name == "cockpit"][0]
        self.cockpit = self.cockpit_item.model
        self.ship_rebuild_callback = MagicMock()
        self.ship.observe(self.ship_rebuild_callback, "rebuild")
        self.target_callback = MagicMock()
        self.target.observe(self.target_callback, "move")

    def test_distance(self):
        self.target_item.drag(1.1, 0)
        assert self.target_callback.called
        self.target_callback.reset_mock()
        assert self.target.position == (1.1, 0, 0)
        assert list(self.ship._connections)[0].distance == 1.1
        assert self.ship_rebuild_callback.called

    def test_inital_state_is_unconnected(self):
        assert set() == self.ship._connections
        assert set() == self.target.connected_parts
        assert not self.ship_rebuild_callback.called
        assert not self.target_callback.called

    def test_moving_part_closer_connects_it(self):
        self.target_item.drag(1.1, 0)
        assert self.target_callback.called
        self.target_callback.reset_mock()
        assert 1 == len(self.ship._connections)
        assert {self.cockpit} == self.target.connected_parts
        assert self.ship_rebuild_callback.called

    def test_disconnecting(self):
        self.target_item.drag(1.1, 0)
        assert self.target_callback.called
        self.target_callback.reset_mock()
        assert self.ship_rebuild_callback.called
        self.ship_rebuild_callback.reset_mock()
        self.target_item.drag(10, 0)
        assert self.target_callback.called
        self.target_callback.reset_mock()
        assert set() == self.ship._connections
        assert set() == self.target.connected_parts
        assert self.ship_rebuild_callback.called

    def test_reconnecting(self):
        self.target_item.drag(1.1, 0)
        assert self.target_callback.called
        self.target_callback.reset_mock()
        assert self.ship_rebuild_callback.called
        self.ship_rebuild_callback.reset_mock()
        self.target_item.drag(10, 0)
        assert self.target_callback.called
        self.target_callback.reset_mock()
        assert self.ship_rebuild_callback.called
        self.ship_rebuild_callback.reset_mock()
        self.target_item.drag(1.1, 0)
        assert self.target_callback.called
        self.target_callback.reset_mock()
        assert self.ship_rebuild_callback.called
        assert 1 == len(self.ship._connections)
        assert {self.cockpit} == self.target.connected_parts
