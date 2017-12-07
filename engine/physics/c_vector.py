class Vector(object):

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.xyz = [x, y, z]

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, other: float):
        return Vector(self.x * other, self.y * other, self.z * other)


class TranslateState(object):

    def __init__(self, position: Vector, momentum: Vector, mass: float):
        self._position = position
        self._momentum = momentum
        self.mass = mass
        self.inverse_mass = 1 / mass
        self.velocity = self._momentum * self.inverse_mass

    @property
    def momentum(self):
        return self._momentum

    @property
    def position(self):
        return self._position

    def update(self):
        self.velocity = self._momentum * self.inverse_mass

    def set_momentum(self, momentum: Vector):
        self._momentum = momentum
        self.update()


class Derivative(object):

    def __init__(self, velocity: Vector, force: Vector):
        self.velocity = velocity
        self.force = force

class Quaternion(object):

    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z
        self.wxyz = [w, x, y, z]

    def __mul__(self, other):
        if isinstance(other, float):
            return Quaternion(other * self.w, other * self.x, other * self.y, other * self.z)
        elif isinstance(other, Quaternion):
            return Quaternion(*[x * y for x, y in zip(self.wxyz, other.wxyz)])

class AngularState(object):

    def __init__(self, orientation: Quaternion, angular_momentum: Vector, intertia: float):
        self.orientation = orientation
        self.angular_momentum = angular_momentum
        self.intertia = intertia
        self.inverse_intertia = 1 / intertia
        self.angular_velocity = self.angular_momentum * self.inverse_intertia
        self.spin = Quaternion(0, *self.angular_velocity.xyz) * self.orientation * 0.5