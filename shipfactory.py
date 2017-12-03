import json
from ship import Ship, ShipPart


class ShipFactory(object):
    def __init__(self):
        with open("ships.json", 'r') as f:
            ships = json.load(f)
        self.ships = {ship['name']: ship for ship in ships}

    def manufacture(self, name) -> Ship:
        config = self.ships[name]
        parts = {}
        for part in config['parts']:
            position = part['position']
            position.insert(1, 0)
            position = [n * 2 for n in position]
            part['position'] = position
            parts[tuple(part['position'])] = ShipPart(**part)
        ship = Ship(parts)
        return ship
