import json
from copy import deepcopy

from engine.models.ship_part import ShipPartModel
from engine.models.ship import ShipModel
from engine.physics.force import MutableOffsets, MutableDegrees


class ShipModelFactory(object):

    def __init__(self):
        with open("ships.json", 'r') as f:
            ships = json.load(f)
        self.ships = {ship['name']: ship for ship in ships}
        self.ship_part_model_factory = ShipPartModelFactory()

    def manufacture(self, name) -> ShipModel:
        config = deepcopy(self.ships[name])
        parts = set()
        for part_config in config['parts']:
            part = self.ship_part_model_factory.manufacture(**part_config)
            parts.add(part)
        ship = ShipModel(parts, position=MutableOffsets(0, 0, 0), rotation=MutableDegrees(0, 0, 0),
                         movement=MutableOffsets(0, 0, 0), spin=MutableDegrees(0, 0, 0))
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
        config['position'] = MutableOffsets(*placement_config.get('position', (0, 0, 0)))
        config['rotation'] = MutableDegrees(*placement_config.get('rotation', (0, 0, 0)))
        config['movement'] = MutableOffsets(*placement_config.get('movement', (0, 0, 0)))
        config['spin'] = MutableDegrees(*placement_config.get('spin', (0, 0, 0)))
        config['target_indicator'] = placement_config.get('target_indicator', False)
        part = ShipPartModel(**config)
        return part
