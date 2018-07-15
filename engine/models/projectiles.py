from engine.models.base_model import BaseModel
from engine.physics.force import MutableDegrees, MutableOffsets, MutableForce
from engine.physics.polygon import Polygon


class PlasmaModel(BaseModel):

    def __init__(self, position: MutableOffsets, rotation: MutableDegrees, movement: MutableOffsets,
                 spin: MutableDegrees, acceleration: MutableOffsets, torque: MutableDegrees, bounding_box: Polygon):
        super(PlasmaModel, self).__init__(position, rotation, movement, spin, acceleration, torque, bounding_box)
        self._ttl = 4
        self._mass = 0.001
        self._destructive_energy = 400

    @property
    def destructive_energy(self):
        return self._destructive_energy

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

    def add_collision(self, force: MutableForce):
        self.set_movement(0, 0, 0)
        #self.explode()
        #self.set_alive(False)
