from engine.models.factories import ShipModelFactory
from engine.controllers.base_controller import BaseController
from engine.physics.force import MutableOffsets
import json

my_model_json = """{"movement": [2.748108688345605,0.0,1.0486111822461213], "rotation": [0.0,-121.07833578764465,0.0], "position": [4.949705974629591,0.0,1.394527032023651], "spin": [0.0,6.828170260674056,0.0]}"""
other_model_json = """{"movement": [-0.0007693501685857157,0.0,-0.0015387003524503548], "rotation": [0.0,-6.823375505192384e-07,0.0], "position": [9.997651582697356,0.0,1.9953031653716429], "spin": [0.0,-2.2353629869817982e-07,0.0]}"""
factory = ShipModelFactory()

class _TestIntegratedCollision(object):

    def setup(self):
        config = json.loads(my_model_json)
        self.ship1 = factory.manufacture("wolf", **config)
        config = json.loads(other_model_json)
        self.ship2 = factory.manufacture("wolf", **config)
        x, z = self._colliding_position(self.ship1, self.ship2)
        position = MutableOffsets(x, 0, z)
        self.my_force = self.ship1.global_momentum_at(position)
        self.other_force = self.ship2.global_momentum_at(position)

    @staticmethod
    def _colliding_position(model1, model2):
        if not BaseController._collides(model1, model2):
            raise ValueError("Models don't collide")
        part_zip = zip(model1.parts, model2.parts)
        # TODO: Check each part against other outer bounding box to determine which needs individual checks
        parts = set()
        for part1, part2 in part_zip:
            if part1.position.y != 0 or part2.position.y != 0:
                continue
            if BaseController._collides(part1, part2):
                pos1 = part1.position.__copy__()
                model1.mutate_offsets_to_global(pos1)
                parts.add(pos1)
                pos2 = part2.position.__copy__()
                model1.mutate_offsets_to_global(pos2)
                parts.add(pos2)
        if len(parts) == 0:
            raise ValueError("Models don't collide")
        else:
            x = sum([position.x for position in parts]) / len(parts)
            z = sum([position.z for position in parts]) / len(parts)
            return x, z

    def test_force_position_x_is_between_ships(self):
        # Translate my force to local, check direction is in 180 degree arc of other
        sorted_positions = sorted([self.ship1.position.x, self.my_force.position.x, self.ship2.position.x])
        assert sorted_positions[1] == self.my_force.position.x

    def test_force_position_z_is_between_ships(self):
        assert sorted([self.ship1.position.z, self.my_force.position.z, self.ship2.position.z])[1] == self.my_force.position.z

    def test_my_global_force_is_left(self):
        assert self.my_force.forces.z < 0

    def test_other_global_force_is_right(self):
        print(self.my_force.forces, self.other_force.forces)
        assert self.other_force.forces.z > 0
