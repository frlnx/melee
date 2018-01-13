import json
from copy import deepcopy
from functools import partial
from math import sin, cos

from engine.models.projectiles import PlasmaModel
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
        bounding_box.set_position_rotation(position.x, position.z, rotation.yaw)
        bounding_box.freeze()
        ship = ShipModel(ship_id=ship_id, parts=parts, position=position, rotation=rotation,
                         movement=movement, spin=spin, bounding_box=bounding_box)
        return ship


class ShipPartModelFactory(object):

    def __init__(self):
        with open("ship_parts.json", 'r') as f:
            ship_parts = json.load(f)
        self.ship_parts = {ship_part['name']: ship_part for ship_part in ship_parts}

    def manufacture(self, name,  **placement_config) -> ShipPartModel:
        config = deepcopy(self.ship_parts[name])
        config['button'] = placement_config.get('button')
        config['axis'] = placement_config.get('axis')
        position = MutableOffsets(*placement_config.get('position', (0, 0, 0)))
        rotation = MutableDegrees(*placement_config.get('rotation', (0, 0, 0)))
        config['position'] = position
        config['rotation'] = rotation
        config['movement'] = MutableOffsets(*placement_config.get('movement', (0, 0, 0)))
        config['spin'] = MutableDegrees(*placement_config.get('spin', (0, 0, 0)))
        config['target_indicator'] = placement_config.get('target_indicator', False)
        bounding_box = Polygon.manufacture([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)],
                            x=position.x, y=position.z, rotation=rotation.yaw)
        config['bounding_box'] = bounding_box
        part = ShipPartModel(**config)
        return part


class ProjectileModelFactory(object):

    def __init__(self):
        self.projectiles = {"plasma": {}}

    def manufacture(self, name,
                    position: MutableOffsets, rotation: MutableDegrees,
                    movement: MutableOffsets, spin: MutableDegrees) -> PlasmaModel:
        config = deepcopy(self.projectiles[name])
        bounding_box = Polygon.manufacture([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)],
                            x=position.x, y=position.z, rotation=rotation.yaw)
        projectile = PlasmaModel(position, rotation, movement, spin, bounding_box)
        print("Pang model")
        return projectile


class ProjectileModelSpawnFunctionFactory(object):

    def __init__(self):
        self.factory = ProjectileModelFactory()

    def manufacture(self, name, ship_model: ShipModel, ship_part_model: ShipPartModel):
        spawn_func = partial(self._manufacture, name, ship_model, ship_part_model)
        return spawn_func

    def _manufacture(self, name, ship_model: ShipModel, ship_part_model: ShipPartModel) -> PlasmaModel:
        rotation = ship_model.rotation + ship_part_model.rotation
        position = ship_part_model.position
        ship_model.mutate_offsets_to_global(position)
        position += MutableOffsets(sin(rotation.yaw_radian), 0, -cos(rotation.yaw_radian))
        rotation = ship_model.rotation.__copy__()
        movement = MutableOffsets(sin(rotation.yaw_radian) * 5, 0, -cos(rotation.yaw_radian) * 5)
        movement += ship_model.global_momentum_at(ship_part_model.position).forces
        spin = -ship_model.spin
        return self.factory.manufacture(name, position, rotation, movement, spin)
