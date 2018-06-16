from engine.models.base_model import BaseModel
from engine.physics.force import MutableDegrees, MutableOffsets
from engine.physics.polygon import Polygon


class PlasmaModel(BaseModel):

    def __init__(self, position: MutableOffsets, rotation: MutableDegrees, movement: MutableOffsets,
                 spin: MutableDegrees, acceleration: MutableOffsets, torque: MutableDegrees, bounding_box: Polygon):
        super(PlasmaModel, self).__init__(position, rotation, movement, spin, acceleration, torque, bounding_box)
        self._ttl = 4
        self._explosive_energy = 400

    def energy_on_impact_relative_to(self, interception_vector):
        return self.mass * interception_vector.distance + self._explosive_energy

    @property
    def explosive_energy(self):
        return self._explosive_energy

    @property
    def is_alive(self):
        return self._ttl > 0 and self._alive

    def count_down(self, dt):
        if self._ttl > 0:
            self._ttl -= dt

    def timers(self, dt):
        super(PlasmaModel, self).timers(dt)
        self.count_down(dt)

    @property
    def mesh_name(self):
        return "plasma"
