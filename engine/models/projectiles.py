from engine.models.base_model import BaseModel
from engine.physics.force import MutableDegrees, MutableOffsets
from engine.physics.polygon import Polygon


class PlasmaModel(BaseModel):

    def __init__(self, position: MutableOffsets, rotation: MutableDegrees, movement: MutableOffsets,
                 spin: MutableDegrees, bounding_box: Polygon):
        super(PlasmaModel, self).__init__(position, rotation, movement, spin, bounding_box)
        self._ttl = 4

    @property
    def is_alive(self):
        return self._ttl > 0 and self._alive

    def count_down(self, dt):
        if self._ttl > 0:
            self._ttl -= dt

    def timers(self, dt):
        self.count_down(dt)

    @property
    def mesh_name(self):
        return "plasma"
