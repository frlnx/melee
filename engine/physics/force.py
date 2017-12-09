from math import sqrt, atan2, cos, sin, degrees, radians, pi
from numpy import array, cross, dot, matrix


class Vector(object):

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.xyz = array([x, y, z])
        self.distance = sqrt(sqrt(self.x ** 2 + self.y ** 2) ** 2 + self.z ** 2)

    def __add__(self, other):
        return self.__class__(*(self.xyz + other.xyz))

    def __mul__(self, other: float):
        return self.__class__(*(self.xyz * other))

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


class Degrees(Vector):

    def __sub__(self, other: Vector):
        return Degrees(*[(((s % 360)) - ((o % 360)) % 360) - 180 for s, o in zip(self, other)])

    @property
    def pitch(self):
        return self.x

    @property
    def yaw(self):
        return self.y

    @property
    def bank(self):
        return self.z

    @property
    def pitch_radian(self):
        return radians(self.pitch)

    @property
    def yaw_radian(self):
        return radians(self.yaw)

    @property
    def bank_radian(self):
        return radians(self.bank)


class Offsets(Vector):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.direction = Degrees(0, degrees(atan2(self.x, self.z)), 0)


class BaseForce(object):

    def __init__(self, position: Offsets, forces: Offsets):
        self.position = position
        self.forces = forces

    def __add__(self, other):
        return BaseForce(self.position + other.position, self.forces + other.forces)

    def __mul__(self, other):
        return BaseForce(self.position * other, self.forces * other)

    def diff_yaw_of_force_to_pos(self):
        return (self.forces.direction.yaw % 360) - (self.position.direction.yaw % 360)

    def c_radian(self):
        return radians(90 - self.diff_yaw_of_force_to_pos())

    def a_radian(self):
        return radians(self.diff_yaw_of_force_to_pos() - 90)

    def translation_part_of_force(self):
        return abs(sin(self.c_radian()))

    def translation_forces(self):
        return self.forces.xyz * self.translation_part_of_force()


class RotationalForce(BaseForce):

    def __init__(self, position: Offsets, forces: Offsets):
        super().__init__(position, forces)
        if self.position.distance == 0:
            self.yaw_force = lambda x: 0
        else:
            self.yaw_momentum = -cos(self.c_radian())

    def yaw_force(self, force):
        return degrees(self.yaw_momentum * (force / self.position.distance))
