from __future__ import division
from math import sqrt, atan2, cos, sin, degrees, radians

from numpy import array, cross, dot


class Vector(object):

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.xyz = array([x, y, z])
        self.distance = sqrt(sqrt(self.x ** 2 + self.y ** 2) ** 2 + self.z ** 2)

    def __add__(self, other):
        return self.__class__(*[x + y for x, y in zip(self, other)])

    def __sub__(self, other):
        return self.__class__(*[x - y for x, y in zip(self, other)])

    def __mul__(self, other: float):
        return self.__class__(*[x * other for x in self])

    def __floordiv__(self, other):
        return self.__div__(other)

    def __div__(self, other):
        return self.__class__(*[x / other for x in self])

    def __truediv__(self, other):
        return self.__div__(other)

    def cross(self, other):
        return self.__class__(*cross(self.xyz, other.xyz))

    def dot(self, other):
        return self.__class__(*dot(self.xyz, other.xyz))

    def __repr__(self):
        return "V: {} {} {}".format(*self.xyz)

    def __eq__(self, other):
        return self.xyz.tolist() == other.xyz.tolist()

    def __hash__(self):
        return self.xyz.tolist().__hash__()

    def __getitem__(self, item):
        return self.xyz[item]


class MutableVector(Vector):

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    @property
    def xyz(self):
        return [self._x, self._y, self._z]

    def set(self, x, y, z):
        if x == self._x and y == self._y and z == self._z:
            return
        self._x = x
        self._y = y
        self._z = z
        self.update()

    def update(self):
        pass

    def __iadd__(self, other):
        self.set(*[x + y for x, y in zip(self, other)])
        return self

    def __isub__(self, other):
        self.set(*[x - y for x, y in zip(self, other)])
        return self

    def __imul__(self, other: float):
        self.set(*[x + other for x in self])
        return self

    def icross(self, other):
        self.set(*cross(self.xyz, other.xyz))
        return self

    def idot(self, other):
        self.set(*dot(self.xyz, other.xyz))
        return self

    @property
    def distance(self):
        return sqrt(sqrt(self.x ** 2 + self.y ** 2) ** 2 + self.z ** 2)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z


class Degrees(Vector):

    def __sub__(self, other: Vector):
        return self.__class__(*[(((s % 360) - (o % 360) + 180) % 360) - 180 for s, o in zip(self, other)])

    @property
    def pitch(self):
        return self.x

    @property
    def yaw(self):
        return self.y

    @property
    def roll(self):
        return self.z

    @property
    def pitch_radian(self):
        return radians(self.pitch)

    @property
    def yaw_radian(self):
        return radians(self.yaw)

    @property
    def roll_radian(self):
        return radians(self.roll)


class MutableDegrees(MutableVector, Degrees):

    def __isub__(self, other: Vector):
        self.set(*[(((s % 360) - (o % 360) + 180) % 360) - 180 for s, o in zip(self, other)])
        return self


class Offsets(Vector):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.direction = Degrees(0, degrees(atan2(-self.x, -self.z)), 0)

    def rotated(self, theta):
        theta = radians(theta)
        x = self.x * cos(theta) - self.z * sin(theta)
        z = self.x * sin(theta) + self.z * cos(theta)
        return Offsets(x, self.y, z)


class MutableOffsets(MutableVector, Offsets):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.direction = MutableDegrees(0, degrees(atan2(-self.x, -self.z)), 0)

    def rotate(self, theta):
        theta = radians(theta)
        x = self.x * cos(theta) - self.z * sin(theta)
        z = self.x * sin(theta) + self.z * cos(theta)
        self.set(x, self._y, z)
        self.update()

    def update(self):
        super().update()
        self.direction.set(self.direction.x, degrees(atan2(-self._x, -self._z)), self.direction.z)


class Force(object):

    def __init__(self, position: Offsets, forces: Offsets):
        self.position = position
        self.forces = forces
        self.yaw_momentum = cos(self.c_radian())
        self._force_multiplier = 1.0

    def __add__(self, other):
        return self.__class__(self.position + other.position, self.forces + other.forces)

    def __mul__(self, other):
        return self.__class__(self.position * 1, self.forces * other)

    def diff_yaw_of_force_to_pos(self):
        return (((self.forces.direction.yaw % 360) - (self.position.direction.yaw % 360) + 180) % 360) - 180

    def c_radian(self):
        return radians(90 - self.diff_yaw_of_force_to_pos())

    def a_radian(self):
        return radians(self.diff_yaw_of_force_to_pos() - 90)

    def translation_forces(self):
        return self.forces * self._force_multiplier

    @property
    def delta_yaw(self):
        return degrees(cos(self.c_radian())) * self._force_multiplier

    def __repr__(self):
        return "{} {}".format(self.position, self.forces)

    def rotated(self, theta):
        position = self.position.rotated(theta)
        forces = self.forces.rotated(theta)
        return Force(position, forces)

    def translate(self, offset: Offsets):
        self.position = self.position + offset


class MutableForce(Force):

    def __init__(self, position: MutableOffsets, forces: MutableOffsets):
        super().__init__(position, forces)
        self.position = position
        self._original_forces = MutableOffsets(*forces)
        self.forces = forces
        self.set_force(0)

    def __iadd__(self, other):
        self.position += other.position
        self.forces += other.forces
        return self

    def __imul__(self, other):
        self.position *= other
        self.forces *= other
        return self

    def set_force(self, force):
        x, y, z = self._original_forces
        self._force_multiplier = force
        self.forces.set(x * force, y * force, z * force)

    def translation_forces(self):
        return self.forces

    @property
    def delta_yaw(self):
        return degrees(cos(self.c_radian())) * self._force_multiplier

    def _rotate(self, theta):
        self.position.rotate(theta)
        self.forces.rotate(theta)
        return self

    def translate(self, offset):
        self.position = self.position + offset
