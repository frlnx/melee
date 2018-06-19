from .base_model import BaseModel
from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.polygon import Polygon

class AsteroidModel(BaseModel):

    def __init__(self, position: MutableOffsets, rotation: MutableDegrees, movement: MutableOffsets,
                 spin: MutableDegrees, acceleration: MutableOffsets, torque: MutableDegrees, bounding_box: Polygon):
        super().__init__(position, rotation, movement, spin, acceleration, torque, bounding_box)
        self._mass = 100000000
