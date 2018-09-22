from engine.models.base_model import BaseModel
from engine.physics.force import MutableDegrees, MutableOffsets
from engine.physics.polygon import MultiPolygon


class WeldedModel(BaseModel):

    def __init__(self, position: MutableOffsets, rotation: MutableDegrees, movement: MutableOffsets,
                 spin: MutableDegrees, acceleration: MutableOffsets, torque: MutableDegrees,
                 bounding_box: MultiPolygon):
        super().__init__(position, rotation, movement, spin, acceleration, torque, bounding_box)