import json
from copy import deepcopy
from functools import partial
from itertools import chain
from math import sin, cos, radians
from random import normalvariate

from shapely.geometry import MultiPoint

from engine.models.asteroid import AsteroidModel
from engine.models.projectiles import PlasmaModel
from engine.models.shield import ShieldArcModel
from engine.models.ship import ShipModel
from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.polygon import Polygon


class ShipModelFactory(object):

    def __init__(self):
        with open("ships.json", 'r') as f:
            ships = json.load(f)
        self.ships = {ship['name']: ship for ship in ships}
        self.ship_part_model_factory = ShipPartModelFactory()
        self.ship_id_counter = 0

    def manufacture(self, name, position=None, rotation=None, movement=None, spin=None,
                    acceleration=None, torque=None) -> ShipModel:
        config = deepcopy(self.ships[name])
        parts = self.ship_part_model_factory.manufacture_all(config['parts'])
        points = MultiPoint(list(chain(*[[(l.x1, l.y1) for l in part.bounding_box.lines] for part in parts])))

        bounding_box = Polygon.manufacture(points.convex_hull.exterior.coords)
        #for part in parts:
        #    bounding_box += part.bounding_box
        ship_id = "Unknown ship {}".format(self.ship_id_counter)
        self.ship_id_counter += 1
        position = position or (0, 0, 0)
        rotation = rotation or (0, 0, 0)
        movement = movement or (0, 0, 0)
        spin = spin or (0, 0, 0)
        acceleration = acceleration or (0, 0, 0)
        torque = torque or (0, 0, 0)
        position = MutableOffsets(*position)
        rotation = MutableDegrees(*rotation)
        movement = MutableOffsets(*movement)
        spin = MutableDegrees(*spin)
        acceleration = MutableOffsets(*acceleration)
        torque = MutableDegrees(*torque)
        bounding_box.freeze()
        bounding_box.set_position_rotation(position.x, position.z, rotation.yaw)
        ship = ShipModel(ship_id=ship_id, parts=parts, position=position, rotation=rotation,
                         movement=movement, spin=spin, acceleration=acceleration, torque=torque,
                         bounding_box=bounding_box)
        return ship


class ShipPartModelFactory(object):

    ship_parts = {}
    model_map = {"shield arc": ShieldArcModel}

    def __init__(self):
        if len(self.ship_parts) == 0:
            with open("ship_parts.json", 'r') as f:
                ship_parts = json.load(f)
            self.ship_parts = {ship_part['name']: ship_part for ship_part in ship_parts}

    def manufacture_all(self, part_configs: list):
        parts = set()
        for part_config in part_configs:
            part = self.manufacture(**part_config)
            parts.add(part)
            for sub_part_name in part_config.get('sub_parts', []):
                model_class = self.model_map.get(sub_part_name, ShipPartModel)
                sub_part = model_class(part)
                parts.add(sub_part)
        return parts

    def manufacture(self, name, model_class=None, **placement_config) -> ShipPartModel:
        config = deepcopy(self.ship_parts[name])
        build_configs = [
            {"key": "button"}, {"key": "keyboard"}, {"key": "axis"}, {"key": "mouse", "default": []},
            {"key": "position", "default": (0, 0, 0), "class": MutableOffsets},
            {"key": "rotation", "default": (0, 0, 0), "class": MutableDegrees},
            {"key": "movement", "default": (0, 0, 0), "class": MutableOffsets},
            {"key": "spin", "default": (0, 0, 0), "class": MutableDegrees},
            {"key": "acceleration", "default": (0, 0, 0), "class": MutableOffsets},
            {"key": "torque", "default": (0, 0, 0), "class": MutableDegrees}
        ]
        for build_config in build_configs:
            key = build_config['key']
            config[key] = placement_config.get(key, build_config.get('default'))
            if 'class' in build_config:
                config[key] = build_config['class'](*config[key])

        x = config['position'].x
        y = config['position'].y
        yaw = config['rotation'].yaw
        bounding_box = Polygon.manufacture([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)],
                                           x=x, y=y, rotation=yaw)
        config['bounding_box'] = bounding_box
        model_class = model_class or self.model_map.get(name, ShipPartModel)
        part = model_class(**config)
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
                                MutableOffsets(0, 0, 0), MutableDegrees(0, 0, 0),
                                MutableOffsets(0, 0, 0), MutableDegrees(0, 0, 0))

    def repurpose(self, name,
                  position: MutableOffsets, rotation: MutableDegrees,
                  movement: MutableOffsets, spin: MutableDegrees,
                  acceleration: MutableOffsets, torque: MutableDegrees):
        projectile = self.projectiles[name].pop()
        print(len(self.projectiles[name]), "left")
        projectile.set_movement(*movement)
        projectile.set_position_and_rotation(*position, *rotation)
        projectile.set_spin(*spin)
        return projectile

    def manufacture(self, name,
                    position: MutableOffsets, rotation: MutableDegrees,
                    movement: MutableOffsets, spin: MutableDegrees,
                    acceleration: MutableOffsets, torque: MutableDegrees) -> PlasmaModel:
        if self.projectiles[name]:
            return self.repurpose(name, position, rotation, movement, spin)
        #  config = deepcopy(self.projectiles[name])
        bounding_box = Polygon.manufacture([(0, 0), (0, 1)],
                                           x=position.x, y=position.z, rotation=rotation.yaw)
        no_acc = MutableOffsets(0, 0, 0)
        no_torque = MutableDegrees(0, 0, 0)
        projectile = PlasmaModel(position.__copy__(), rotation.__copy__(),
                                 movement.__copy__(), spin.__copy__(), no_acc, no_torque, bounding_box)
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
        acceleration = MutableOffsets(0, 0, 0)
        torque = MutableDegrees(0, 0, 0)
        return self.factory.manufacture(name, position, rotation, movement, spin, acceleration, torque)


class AsteroidModelFactory(object):

    def __init__(self):
        pass

    @staticmethod
    def manufacture(position):
        position = MutableOffsets(*position)
        rotation = MutableDegrees(0, 0, 0)
        movement = MutableOffsets(0, 0, 0)
        spin = MutableDegrees(0, 0, 0)
        acceleration = MutableOffsets(0, 0, 0)
        torque = MutableDegrees(0, 0, 0)
        coords = [(sin(radians(d)), cos(radians(d))) for d in range(0, 360, 18)]
        distances = [abs(normalvariate(25, 5)) for _ in coords]
        coords = [(x * d, y * d) for (x, y), d in zip(coords, distances)]
        bounding_box = Polygon.manufacture(coords=coords, x=position.x, y=position.z, rotation=rotation.yaw)
        return AsteroidModel(position, rotation, movement, spin, acceleration, torque, bounding_box)
