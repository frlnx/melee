from unittest.mock import MagicMock

from pytest import raises

from engine.models import ShipModel
from engine.models.factories import ShipPartModelFactory, ShipModelFactory
from engine.models.part_connection import PartConnectionError
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


class TestShieldConnection(object):

    def setup(self):
        spmf = ShipPartModelFactory()
        null_offset = MutableOffsets(0, 0, 0)
        null_rotation = MutableDegrees(0, 0, 0)
        self.target = spmf.manufacture("shield", position=(10, 0, 0))
        self.other = spmf.manufacture("shield")
        parts = {self.other, self.target}
        self.ship = ShipModel("foo", parts, null_offset.__copy__(), null_rotation.__copy__(), null_offset.__copy__(),
                              null_rotation.__copy__(), null_offset.__copy__(), null_rotation.__copy__())

    def test_inital_state_is_unconnected(self):
        assert set() == self.ship._connections
        assert set() == self.target.connected_parts

    def test_moving_part_closer_connects_it(self):
        self.target.teleport_to(3, 0, 0)
        assert 1 == len(self.ship._connections)
        assert {self.other} == self.target.connected_parts

    def test_disconnecting(self):
        self.target.teleport_to(3, 0, 0)
        self.target.teleport_to(10, 0, 0)
        assert set() == self.ship._connections
        assert set() == self.target.connected_parts

    def test_reconnecting(self):
        self.target.teleport_to(3, 0, 0)
        self.target.teleport_to(10, 0, 0)
        self.target.teleport_to(3, 0, 0)
        assert 1 == len(self.ship._connections)
        assert {self.other} == self.target.connected_parts


class TestPartConnectionManualDisconnection(object):

    def setup(self):
        spmf = ShipPartModelFactory()
        null_offset = MutableOffsets(0, 0, 0)
        null_rotation = MutableDegrees(0, 0, 0)
        self.generator = spmf.manufacture("generator", position=(1.5, 0, 0))
        self.cockpit = spmf.manufacture("cockpit")
        parts = {self.cockpit, self.generator}
        self.ship = ShipModel("foo", parts, null_offset.__copy__(), null_rotation.__copy__(), null_offset.__copy__(),
                              null_rotation.__copy__(), null_offset.__copy__(), null_rotation.__copy__())
        self.target = list(self.ship._connections)[0]

    def test_disconnect_all(self):
        assert {self.cockpit} == self.generator.connected_parts
        assert {self.generator} == self.cockpit.connected_parts
        self.target.disconnect_all()
        assert set() == self.generator.connected_parts
        assert set() == self.cockpit.connected_parts


class TestShieldConnectionInvalidArc(object):

    def setup(self):
        spmf = ShipPartModelFactory()
        null_offset = MutableOffsets(0, 0, 0)
        null_rotation = MutableDegrees(0, 0, 0)
        self.shield1 = spmf.manufacture("shield", position=(2, 0, 0))
        self.obstacles = {spmf.manufacture("generator", position=(0, 0, y)) for y in range(-4, 4)}
        self.shield2 = spmf.manufacture("shield", position=(-2, 0, 0))
        parts = self.obstacles | {self.shield1, self.shield2}
        self.ship = ShipModel("foo", parts, null_offset.__copy__(), null_rotation.__copy__(), null_offset.__copy__(),
                              null_rotation.__copy__(), null_offset.__copy__(), null_rotation.__copy__())

    def test_no_valid_arc(self):
        with raises(PartConnectionError):
            self.ship._make_connection(self.shield1, self.shield2)

    def test_shields_have_no_connection(self):
        assert self.shield2 not in self.shield1.connected_parts
        assert self.shield1 not in self.shield2.connected_parts

    def test_connection_does_not_exist(self):
        connections = [c for c in self.ship._connections if set(c._ship_parts) == {self.shield1, self.shield2}]
        assert not connections


class TestShieldConnectionValidArc(object):

    def setup(self):
        spmf = ShipPartModelFactory()
        null_offset = MutableOffsets(0, 0, 0)
        null_rotation = MutableDegrees(0, 0, 0)
        self.shield1 = spmf.manufacture("shield", position=(2.5, 0, 0))
        self.obstacles = {spmf.manufacture("generator", position=(0, 0, 0))}
        self.shield2 = spmf.manufacture("shield", position=(-2.5, 0, 0))
        parts = self.obstacles | {self.shield1, self.shield2}
        self.ship = ShipModel("foo", parts, null_offset.__copy__(), null_rotation.__copy__(), null_offset.__copy__(),
                              null_rotation.__copy__(), null_offset.__copy__(), null_rotation.__copy__())
        self.target = [c for c in self.ship._connections if set(c._ship_parts) == {self.shield1, self.shield2}][0]

    def test_making_connection_does_not_result_in_part_connection_error(self):
        self.ship._make_connection(self.shield1, self.shield2)
        assert True

    def test_connections_between_shields_are_present(self):
        assert self.shield2 in self.shield1.connected_parts
        assert self.shield1 in self.shield2.connected_parts

    def test_connection_is_not_a_straight_line(self):
        assert [0] * len(list(self.target.bounding_box.lines)) != [l.y1 for l in self.target.bounding_box.lines]


class TestDefaultShip(object):

    def setup(self):
        self.ship = ShipModelFactory().manufacture("ship")
        self.targets = self.ship._connections

    def test_ship_has_connections(self):
        assert self.targets

    def test_connections_are_valid(self):
        for connection in self.targets:
            assert connection.is_valid

    def test_connections_valid_after_movement(self):
        a_part = list(self.ship.parts)[0]
        a_part.set_position(*[d + 0.001 for d in a_part.position])
        for connection in self.targets:
            assert connection.is_valid


class TestDrydockShieldReconnectivity(object):

    def setup(self):
        smf = ShipModelFactory()
        smf.add_configuration({"name": "test_ship", "parts": [
            {"position": [1.6, 0, 0.4], "rotation": [0, 0, 0], "name": "shield"},
            {"position": [0, 0, 0], "rotation": [0, 0, 0], "name": "cockpit"},
            {"position": [-1.48, 0, 0.4], "rotation": [0, 0, 0], "name": "shield"}]})
        self.ship = smf.manufacture("test_ship")
        self.drydock = Drydock(0, 1000, 0, 1000, self.ship, view_factory=FakeFactory())
        self.ship = self.drydock.ship
        self.target_item: DockableItem = [item for item in self.drydock.items if item.model.name == "shield"][0]
        self.target_item.held = True
        self.target_item._highlight = True
        self.target = self.target_item.model
        self.ship_rebuild_callback = MagicMock()
        self.ship.observe(self.ship_rebuild_callback, "rebuild")
        self.target_callback = MagicMock()
        self.target.observe(self.target_callback, "move")
        self.connections = list(self.ship._connections)
        self.shield_connections = [c for c in self.connections if all(p.name == "shield" for p in c._ship_parts)]

    def test_ship_has_connections(self):
        assert self.connections

    def test_connections_are_valid(self):
        for connection in self.connections:
            assert connection.is_valid

    def test_connections_valid_after_movement(self):
        self.target_item.drag(self.target_item.x + 0.01, self.target_item.y)
        for connection in self.connections:
            assert connection.is_valid

    def test_connection_is_not_a_straight_line(self):
        for shield_connection in self.shield_connections:
            if len({round(l.degrees, 1) for l in shield_connection.bounding_box.lines}) == 1:
                print(self.ship.bounding_box)
            assert len({round(l.degrees, 1) for l in shield_connection.bounding_box.lines}) != 1

    def test_intersected_polygons(self):
        assert len(self.shield_connections) == 1
        print("TEST START")
        for shield_connection in self.shield_connections:
            print(shield_connection._polygon._moving_points)
            print(shield_connection._polygon.moving_lines)
            expected = {p.uuid for p in shield_connection._ship_parts}
            _, intersected_polygons = shield_connection.bounding_box.intersected_polygons(self.ship.bounding_box)
            actual = {bb.part_id for bb in intersected_polygons}
            diff = actual - expected
            print("Shield", shield_connection.bounding_box.part_id, shield_connection.uuid)
            print("ACTUAL:", ", ".join(str(self.ship._part_by_uuid.get(uuid, uuid)) for uuid in actual))
            print("EXPECTED:", ", ".join(str(self.ship._part_by_uuid.get(uuid, uuid)) for uuid in expected))
            print("DIFF:", ", ".join(str(self.ship._part_by_uuid.get(uuid, uuid)) for uuid in diff))
            assert expected == actual
