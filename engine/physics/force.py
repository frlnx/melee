from __future__ import division

from math import sqrt, atan2, cos, sin, degrees, radians


class Vector(object):

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.distance = sqrt(sqrt(self.x ** 2 + self.y ** 2) ** 2 + self.z ** 2)

    def __add__(self, other):
        return self.__class__(*[x + y for x, y in zip(self, other)])

    def __sub__(self, other):
        return self.__class__(*[x - y for x, y in zip(self, other)])

    def __mul__(self, other: float) -> "Vector":
        return self.__class__(*[x * other for x in self])

    def __floordiv__(self, other):
        return self.__div__(other)

    def __div__(self, other):
        return self.__class__(*[x / other for x in self])

    def __truediv__(self, other):
        return self.__div__(other)

    def __repr__(self):
        return "V: {} {} {}".format(*self)

    def __eq__(self, other):
        x, y, z = other
        return self.x == x and self.y == y and self.z == z

    def __hash__(self):
        return hash(hash(self.x) + hash(self.y) + hash(self.z))

    def __getitem__(self, item):
        return [self.x, self.y, self.z][item]

    def __copy__(self):
        return self.__class__(*self)

    def __neg__(self):
        return self.__class__(*[-x for x in self])

    @property
    def to_json(self):
        return "[{},{},{}]".format(*self)


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
            return False
        self._x = x
        self._y = y
        self._z = z
        self.update()
        return True

    def update(self):
        pass

    def __iadd__(self, other):
        self.set(*[x + y for x, y in zip(self, other)])
        return self

    def __isub__(self, other):
        self.set(*[x - y for x, y in zip(self, other)])
        return self

    def __imul__(self, other: float) -> "MutableVector":
        self.set(*[x + other for x in self])
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

    def __add__(self, other: Vector):
        return self.__class__(*[(((s % 360) + (o % 360) + 180) % 360) - 180 for s, o in zip(self, other)])

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

    def __iadd__(self, other: tuple):
        self.set(*[(((s % 360) + (o % 360) + 180) % 360) - 180 for s, o in zip(self, other)])
        return self

    def translate(self, *xyz):
        self.__iadd__(*xyz)


class Offsets(Vector):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.direction = Degrees(0, degrees(atan2(-self.x, -self.z)), 0)

    def rotated(self, theta) -> "Offsets":
        theta = radians(theta)
        x = self.x * cos(theta) - self.z * sin(theta)
        z = self.x * sin(theta) + self.z * cos(theta)
        return self.__class__(x, self.y, z)


class MutableOffsets(MutableVector, Offsets):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.direction = MutableDegrees(0, degrees(atan2(-self.x, -self.z)), 0)

    def rotate(self, theta):
        if theta == 0:
            return
        theta = radians(theta)
        x = self.x * cos(theta) - self.z * sin(theta)
        z = self.x * sin(theta) + self.z * cos(theta)
        self.set(x, self._y, z)

    def translate(self, *xyz):
        self.__iadd__(*xyz)

    def update(self):
        super().update()
        self.direction.set(self.direction.x, degrees(atan2(-self._x, -self._z)), self.direction.z)


class Force(object):

    def __init__(self, position: Offsets, forces: Offsets):
        self.position = position
        self.forces = forces
        self.yaw_momentum = cos(self.radians_force_is_lateral_to_position())
        self._force_multiplier = 1.0

    def __add__(self, other) -> "Force":
        return self.__class__(self.position + other.position, self.forces + other.forces)

    def __mul__(self, other) -> "Force":
        return self.__class__(self.position * 1, self.forces * other)

    def __neg__(self) -> "Force":
        return self.__class__(self.position.__copy__(), -self.forces)

    def diff_yaw_of_force_to_pos(self):
        return (((self.forces.direction.yaw % 360) - (self.position.direction.yaw % 360) + 180) % 360) - 180

    def radians_force_is_lateral_to_position(self):
        return radians(self.diff_yaw_of_force_to_pos() - 90)

    def translation_forces(self):
        return self.forces * self._force_multiplier

    @property
    def delta_yaw(self):
        amount_of_force_that_rotates = cos(self.radians_force_is_lateral_to_position())
        delta_yaw_radians = atan2(amount_of_force_that_rotates * self.forces.distance, self.position.distance)
        return degrees(delta_yaw_radians) * self._force_multiplier

    def __repr__(self):
        return "{} {}".format(self.position, self.forces)

    def rotated(self, theta):
        position = self.position.rotated(theta)
        forces = self.forces.rotated(theta)
        return Force(position, forces)

    def translate(self, offset: Offsets):
        self.position = self.position + offset

    def __copy__(self):
        return self.__class__(self.position.__copy__(), self.forces.__copy__())


class MutableForce(Force):

    def __init__(self, position: MutableOffsets, forces: MutableOffsets):
        super().__init__(position, forces)
        self.position = position
        self.forces = forces

    def set_forces(self, *xyz):
        x, y, z = xyz
        self.forces.set(x, y, z)

    def __iadd__(self, other) -> "MutableForce":
        self.position += other.position
        self.forces += other.forces
        return self

    def __imul__(self, other) -> "MutableForce":
        self.position *= other
        self.forces *= other
        return self

    def translation_forces(self) -> MutableOffsets:
        return self.forces

    def translate(self, offset):
        self.position = self.position + offset
