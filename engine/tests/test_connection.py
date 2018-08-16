from engine.models import ShipModel
from engine.models.factories import ShipPartModelFactory
from engine.physics.force import MutableDegrees, MutableOffsets


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

    def test_inital_state_is_unconnected(self):
        assert self.ship._connections == set()
        assert self.target.connected_parts == set()

    def test_moving_part_closer_connects_it(self):
        self.target.teleport_to(1, 0, 0)
        assert len(self.ship._connections) == 1
        assert self.target.connected_parts == {self.cockpit}
