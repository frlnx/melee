from math import hypot

from engine.physics.force import Vector


class Debris(object):

    def __init__(self, x, y, z, i, movement: Vector):
        self.x = x
        self.y = y
        self.z = z
        self.i = i
        self.x1, self.x2, self.z1, self.z2 = x, x, z, z
        self._v3f = [self.x1, self.y - 10, self.z1, self.x2, self.y - 10, self.z2]
        distance = hypot(self.x2, self.z2)
        color = 255 / (distance ** 2 + 1)
        self._c4f = [0, 0, 0, 0, color, color, color, color]
        self._movement = movement

    def update(self, dt):
        x_offset, _, z_offset = -self._movement
        self.i += dt
        self.i %= 1
        self.x1 = (self.x + x_offset * 2 * (self.i - 0.05)) - x_offset
        self.x2 = (self.x + x_offset * 2 * self.i) - x_offset
        self.z1 = (self.z + z_offset * 2 * (self.i - 0.05)) - z_offset
        self.z2 = (self.z + z_offset * 2 * self.i) - z_offset
        self._v3f.clear()
        self._v3f += [self.x1, self.y - 10, self.z1, self.x2, self.y - 10, self.z2]
        distance = hypot(self.x2, self.z2)
        color = 255 / (distance ** 2 + 1)
        self._c4f.clear()
        self._c4f += [0, 0, 0, 0, color, color, color, color]

    @property
    def v3f(self):
        return self._v3f

    @property
    def c4f(self):
        return self._c4f
