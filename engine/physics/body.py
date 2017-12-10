from engine.physics.force import Degrees


class Body(object):

    def __init__(self, direction: Degrees, mass_grams: int):
        self._direction = direction
        self._mass_grams = mass_grams
        self._forces = set()

    def update(self):
        x_force_y_position = 1
