from engine.models.base_model import BaseModel


class PlasmaModel(BaseModel):

    def __init__(self, position: MutableOffsets, rotation: MutableDegrees, movement: MutableOffsets,
                 spin: MutableDegrees, bounding_box: Polygon):
        super(PlasmaModel).__init__(position, rotation, movement, spin, bounding_box)

    @property
    def mesh(self):
        return "plasma"
