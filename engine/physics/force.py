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
        return Degrees(*[(((s % 360) - (o % 360) + 180) % 360) - 180 for s, o in zip(self, other)])

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


class Offsets(Vector):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.direction = Degrees(0, degrees(atan2(-self.x, -self.z)), 0)

    def rotated(self, theta):
        theta = radians(theta)
        x = self.x * cos(theta) - self.z * sin(theta)
        z = self.x * sin(theta) + self.z * cos(theta)
        return Offsets(x, self.y, z)


class Force(object):

    def __init__(self, position: Offsets, forces: Offsets):
        self.position = position
        self.forces = forces
        if self.position.distance == 0:
            self.yaw_force = lambda x: 0
            self.yaw_momentum = 0
        else:
            self.yaw_momentum = cos(self.c_radian())

    def __add__(self, other):
        return self.__class__(self.position + other.position, self.forces + other.forces)

    def __mul__(self, other):
        return self.__class__(self.position * other, self.forces * other)

    def diff_yaw_of_force_to_pos(self):
        return (((self.forces.direction.yaw % 360) - (self.position.direction.yaw % 360) + 180) % 360) - 180

    def c_radian(self):
        return radians(90 - self.diff_yaw_of_force_to_pos())

    def a_radian(self):
        return radians(self.diff_yaw_of_force_to_pos() - 90)

    def translation_part_of_force(self):
        return abs(sin(self.c_radian()))

    def translation_forces(self):
        return self.forces.xyz * self.translation_part_of_force()

    def yaw_force(self, force):
        return degrees(self.yaw_momentum * (force / self.position.distance))

    def __repr__(self):
        return "{} {}".format(self.position, self.forces)

    def rotate(self, theta):
        position = self.position.rotated(theta)
        forces = self.forces.rotated(theta)
        return Force(position, forces)
