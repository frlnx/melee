import json
from copy import deepcopy
from functools import partial
from math import sin, cos, radians
from random import normalvariate

from engine.models.projectiles import PlasmaModel
from engine.models.asteroid import AsteroidModel
from engine.models.ship_part import ShipPartModel
from engine.models.ship import ShipModel
from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.polygon import Polygon


class ShipModelFactory(object):

    def __init__(self):
        with open("ships.json", 'r') as f:
            ships = json.load(f)
        self.ships = {ship['name']: ship for ship in ships}
        self.ship_part_model_factory = ShipPartModelFactory()
        self.ship_id_counter = 0

    def manufacture(self, name, position=None, rotation=None, movement=None, spin=None) -> ShipModel:
        config = deepcopy(self.ships[name])
        bounding_box = Polygon.manufacture([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)])
        parts = set()
        for part_config in config['parts']:
            part = self.ship_part_model_factory.manufacture(**part_config)
            parts.add(part)
            if part.position.y == 0:
                bounding_box += part.bounding_box
        ship_id = self.ship_id_counter
        self.ship_id_counter += 1
        if position is None:
            position = (0, 0, 0)
        position = MutableOffsets(*position)
        if rotation is None:
            rotation = (0, 0, 0)
        rotation = MutableDegrees(*rotation)
        if movement is None:
            movement = (0, 0, 0)
        movement = MutableOffsets(*movement)
        if spin is None:
            spin = (0, 0, 0)
        spin = MutableDegrees(*spin)
        bounding_box.freeze()
        bounding_box.set_position_rotation(position.x, position.z, rotation.yaw)
        ship = ShipModel(ship_id=ship_id, parts=parts, position=position, rotation=rotation,
                         movement=movement, spin=spin, bounding_box=bounding_box)
        return ship


class ShipPartModelFactory(object):

    ship_parts = {}

    def __init__(self):
        if len(self.ship_parts) == 0:
            with open("ship_parts.json", 'r') as f:
                ship_parts = json.load(f)
            self.ship_parts = {ship_part['name']: ship_part for ship_part in ship_parts}

    def manufacture(self, name,  **placement_config) -> ShipPartModel:
        config = deepcopy(self.ship_parts[name])
        config['button'] = placement_config.get('button')
        config['keyboard'] = placement_config.get('keyboard')
        config['axis'] = placement_config.get('axis')
        position = MutableOffsets(*placement_config.get('position', (0, 0, 0)))
        rotation = MutableDegrees(*placement_config.get('rotation', (0, 0, 0)))
        config['position'] = position
        config['rotation'] = rotation
        config['movement'] = MutableOffsets(*placement_config.get('movement', (0, 0, 0)))
        config['spin'] = MutableDegrees(*placement_config.get('spin', (0, 0, 0)))
        bounding_box = Polygon.manufacture([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)],
                                           x=position.x, y=position.z, rotation=rotation.yaw)
        config['bounding_box'] = bounding_box
        part = ShipPartModel(**config)
        return part

    @property
    def all_parts(self):
        return self.ship_parts.values()


class ProjectileModelFactory(object):

    def __init__(self):
        self.projectile_configs = {"plasma": {}}
        self.projectiles = {"plasma": []}
        plasmas = [self._pre_manufacture("plasma") for _ in range(100)]
        self.projectiles["plasma"] = plasmas

    def _pre_manufacture(self, name):
        return self.manufacture(name, MutableOffsets(0, 0, 0), MutableDegrees(0, 0, 0),
                                MutableOffsets(0, 0, 0), MutableDegrees(0, 0, 0))

    def repurpose(self, name,
                  position: MutableOffsets, rotation: MutableDegrees,
                  movement: MutableOffsets, spin: MutableDegrees):
        projectile = self.projectiles[name].pop()
        print(len(self.projectiles[name]), "left")
        projectile.set_movement(*movement)
        projectile.set_position_and_rotation(*position, *rotation)
        projectile.set_spin(*spin)
        return projectile

    def manufacture(self, name,
                    position: MutableOffsets, rotation: MutableDegrees,
                    movement: MutableOffsets, spin: MutableDegrees) -> PlasmaModel:
        if self.projectiles[name]:
            return self.repurpose(name, position, rotation, movement, spin)
        #  config = deepcopy(self.projectiles[name])
        bounding_box = Polygon.manufacture([(0, 0), (0, 1)],
                                           x=position.x, y=position.z, rotation=rotation.yaw)
        projectile = PlasmaModel(position.__copy__(), rotation.__copy__(),
                                 movement.__copy__(), spin.__copy__(), bounding_box)
        return projectile


class ProjectileModelSpawnFunctionFactory(object):

    def __init__(self):
        self.factory = ProjectileModelFactory()

    def manufacture(self, name, ship_model: ShipModel, ship_part_model: ShipPartModel):
        spawn_func = partial(self._manufacture, name, ship_model, ship_part_model)
        return spawn_func

    def _manufacture(self, name, ship_model: ShipModel, ship_part_model: ShipPartModel) -> PlasmaModel:
        yaw_radian = ship_model.rotation.yaw_radian + ship_part_model.rotation.yaw_radian
        position = ship_part_model.position.__copy__()
        position.set(position.x, position.y, position.z - 3)
        ship_model.mutate_offsets_to_global(position)
        rotation = ship_model.rotation.__copy__()
        movement = MutableOffsets(-sin(yaw_radian) * 25, 0, -cos(yaw_radian) * 25)
        movement += ship_model.global_momentum_at(ship_part_model.position).forces
        spin = -ship_model.spin
        return self.factory.manufacture(name, position, rotation, movement, spin)


class AsteroidModelFactory(object):

    def __init__(self):
        pass

    @staticmethod
    def manufacture(position):
        position = MutableOffsets(*position)
        rotation = MutableDegrees(0, 0, 0)
        movement = MutableOffsets(0, 0, 0)
        spin = MutableDegrees(0, 0, 0)
        coords = [(sin(radians(d)), cos(radians(d))) for d in range(0, 360, 18)]
        distances = [abs(normalvariate(25, 5)) for _ in coords]
        coords = [(x * d, y * d) for (x, y), d in zip(coords, distances)]
        bounding_box = Polygon.manufacture(coords=coords, x=position.x, y=position.z, rotation=rotation.yaw)
        return AsteroidModel(position, rotation, movement, spin, bounding_box)
