from math import sqrt, atan2, cos, sin, degrees, radians


class BaseDirection(object):

    def __init__(self, pitch, yaw, bank):
        self._pitch = pitch
        self._yaw = yaw
        self._bank = bank
        self._pitch_yaw_bank = [self._pitch, self._yaw, self._bank]
        self._dimensional_ratios = [sin(radians(self._yaw)),
                                    sin(radians(self._pitch)),
                                    cos(radians(self._yaw))]

    @property
    def cos(self):
        return [cos(radians(x)) for x in self._pitch_yaw_bank]

    @property
    def sin(self):
        return [sin(radians(x)) for x in self._pitch_yaw_bank]

    @property
    def dimensional_ratios(self):
        return self._dimensional_ratios

    def __repr__(self):
        return "Pitch: {}, Yaw: {}, Bank: {}".format(*self._pitch_yaw_bank)

class Direction(BaseDirection):

    def __sub__(self, other: BaseDirection):
        pitch_yaw_bank = [((s % 360)) - ((o % 360)) % 360 for s, o in zip(self._pitch_yaw_bank, other._pitch_yaw_bank)]
        return Direction(*pitch_yaw_bank)


class BasePosition(object):

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z
        self._distance = sqrt(sqrt(self._x ** 2 + self._y ** 2) ** 2 + self._z ** 2)
        self._direction = Direction(0, degrees(atan2(self._x, self._z)), 0)
        self._xyz = [x, y, z]


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
        self._rotational_forces = self._offset_direction.sin
        self.pitch_factor, self.yaw_factor, self.bank_factor = self._offset_direction.cos
        self.pitch, self.yaw, self.bank = self._direction._pitch_yaw_bank
        self._directional_forces = [sin(radians(self.yaw + 180)) * self.yaw_factor,
                                    sin(radians(self.pitch + 180)) * self.pitch_factor,
                                    cos(radians(self.yaw + 180)) * self.yaw_factor]

    @property
    def position(self):
        return self._position

    @property
    def direction(self):
        return self._direction

    def set_force(self, force):
        self._force = force

    @property
    def force(self):
        return self._force

    @property
    def rotational_forces(self):
        return self._rotational_forces

    @property
    def directional_forces(self):
        return self._directional_forces

    def __repr__(self):
        templ = "x: {}, y: {}, z: {}, yaw: {}, offset_yaw: {}, rotation: {}, direction: {}"
        return templ.format(*self._position._xyz, self._direction._yaw, self._offset_direction._yaw,
                            self.rotational_forces, self.directional_forces)

class Vector(BaseVector):

    def __add__(self, other: BaseVector):
        x, y, z = self.direction.dimensional_ratios

        return Vector(force, position, direction)