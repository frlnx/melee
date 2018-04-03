from .composite_model import CompositeModel
from .base_model import BaseModel


class AsteroidModel(CompositeModel):
    pass


class AsteroidPartModel(BaseModel):

    def __init__(self, position: 'MutableOffsets', rotation: 'MutableDegrees', movement: 'MutableOffsets',
                 spin: 'MutableDegrees', bounding_box: 'Polygon'):
        super().__init__(position, rotation, movement, spin, bounding_box)
        self._mesh = 'stone'
