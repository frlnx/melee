from math import sqrt, atan2, cos, sin, degrees, radians
from numpy import array, cross, dot, matrix


class Vector(object):

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.xyz = array([x, y, z])
        self.distance = sqrt(sqrt(self.x ** 2 + self.y ** 2) ** 2 + self.z ** 2)

    def __add__(self, other):
        return Vector(*(self.xyz + other.xyz))

    def __mul__(self, other: float):
        return Vector(*(self.xyz * other))

    def cross(self, other):
        return Vector(*cross(self.xyz, other.xyz))

    def dot(self, other):
        return Vector(*dot(self.xyz, other.xyz))

    def __repr__(self):
        return "V: {} {} {}".format(*self.xyz)

    def __eq__(self, other):
        return self.xyz.tolist() == other.xyz.tolist()

    def __hash__(self):
        return self.xyz.tolist().__hash__()


class Direction(Vector):

    def __sub__(self, other: Vector):
        return Direction(*[(((s % 360)) - ((o % 360)) % 360) - 180 for s, o in zip(self, other)])


class Position(Vector):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.direction = Direction(0, degrees(atan2(self.x, self.z)), 0)


class BaseForce(object):

    def __init__(self, position: Position, direction: Direction):
        self.position = position
        self.direction = direction


    def __add__(self, other):

class RotationalForce(BaseForce):

    def __init__(self, position: Position, direction: Direction):
        super().__init__(position, direction)
        if self.position.distance == 0:
            self.yaw_force = lambda x: 0
        self.yaw_momentum = sin(radians((self.direction.y % 360) - (self.position.direction.y % 360) - 90))

    def yaw_force(self, force):
        return self.yaw_momentum * (force / self.position.distance)


class MomentumForcesSum(BaseForce):

    def __init__(self, position: Position, direction: Direction, force):
        super().__init__(position, direction)
        self.translation_force = sin(radians(90 - (self.direction.y % 360) - (self.position.direction.y % 360)))
        self._directional_forces = array([sin(radians(self.direction.y)) * self.translation_force,
                                          sin(radians(self.direction.x)) * self.translation_force,
                                          cos(radians(self.direction.y)) * self.translation_force])

    def directional_forces(self, force):
        return self._directional_forces * force