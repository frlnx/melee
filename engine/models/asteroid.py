from .base_model import BaseModel


class AsteroidModel(BaseModel):
    pass


class AsteroidPartModel(BaseModel):

    def __init__(self, position: 'MutableOffsets', rotation: 'MutableDegrees', movement: 'MutableOffsets',
                 spin: 'MutableDegrees', bounding_box: 'Polygon'):
        super().__init__(position, rotation, movement, spin, bounding_box)
        self._mesh = 'asteroid'
        self._mass = 100000000
