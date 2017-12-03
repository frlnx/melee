import json
from copy import deepcopy

from engine.models.ship_part import ShipPartModel
from engine.models.ship import ShipModel


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
            parts.add(self.ship_part_model_factory.manufacture(part_config))
        ship = ShipModel(parts, (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
        return ship


class ShipPartModelFactory(object):

    def __init__(self):
        with open("ship_parts.json", 'r') as f:
            ship_parts = json.load(f)
        self.ship_parts = {ship_part['name']: ship_part for ship_part in ship_parts}

    def manufacture(self, placement_config) -> ShipPartModel:
        config = deepcopy(self.ship_parts[placement_config['name']])
        config['position'] = placement_config.get('position', (0, 0, 0))
        config['rotation'] = placement_config.get('rotation', (0, 0, 0))
        config['movement'] = placement_config.get('movement', (0, 0, 0))
        config['spin'] = placement_config.get('spin', (0, 0, 0))
        part = ShipPartModel(**config)
        return part
