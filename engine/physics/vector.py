from math import sqrt, atan2, cos, sin, degrees


class BaseDirection(object):

    def __init__(self, pitch, yaw, bank):
        self._pitch = pitch
        self._yaw = yaw
        self._bank = bank
        self._pitch_yaw_bank = [self._pitch, self._yaw, self._bank]

    @property
    def cos(self):
        return [cos(x) for x in self._pitch_yaw_bank]

    @property
    def sin(self):
        return [sin(x) for x in self._pitch_yaw_bank]

    def __repr__(self):
        return "Pitch: {}, Yaw: {}, Bank: {}".format(*self._pitch_yaw_bank)

class Direction(BaseDirection):

    def __sub__(self, other: BaseDirection):
        return Direction(self._pitch - other._pitch, self._yaw - other._yaw, self._bank - other._bank)


class BasePosition(object):

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z
        self._distance = sqrt(sqrt(self._x ** 2 + self._y ** 2) ** 2 + self._z ** 2)
        self._direction = Direction(0, degrees(atan2(self._x, self._z)), 0)


class Position(BasePosition):

    @property
    def distance(self):
        return self._distance

    @property
    def direction(self) -> Direction:
        return self._direction


class BaseVector(object):

    def __init__(self, force, position: Position, direction: Direction):
        self._force = force
        self._position = position
        self._direction = direction
        self._offset_direction = self._direction - self._position.direction
        self._rotational_forces = [self._force * offset_direction for offset_direction in self._offset_direction.sin]
        # Needs a transformation matrix
        self._directional_forces = [self._force * offset_direction for offset_direction in self._offset_direction.cos]

    @property
    def rotational_forces(self):
        return self._rotational_forces

    @property
    def directional_forces(self):
        return self._directional_forces


class Vector(BaseVector):
    pass