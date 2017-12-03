from typing import Tuple, Callable


class BaseModel(object):

    def __init__(self,
                 position: Tuple[float, float, float],
                 rotation: Tuple[float, float, float],
                 movement: Tuple[float, float, float],
                 spin: Tuple[float, float, float]):
        self._x, self._y, self._z = position
        self._pitch, self._yaw, self._bank = rotation
        self._dx, self._dy, self._dz = movement
        self._dpitch, self._dyaw, self._dbank = spin
        self._observers = set()

    def observe(self, func: Callable):
        self._observers.add(func)

    def _callback(self):
        for observer in self._observers:
            observer()

    def set_position_and_rotation(self, x, y, z, pitch, yaw, bank):
        self._x, self._y, self._z = x, y, z
        self._pitch, self._yaw, self._bank = pitch, yaw, bank
        self._callback()

    def set_position(self, x, y, z):
        self._x, self._y, self._z = x, y, z
        self._callback()

    def set_rotation(self, pitch, yaw, bank):
        self._pitch, self._yaw, self._bank = pitch, yaw, bank
        self._callback()

    def set_movement(self, dx, dy, dz):
        self._dx, self._dy, self._dz = dx, dy, dz

    def set_spin(self, dpitch, dyaw, dbank):
        self._dpitch, self._dyaw, self._dbank = dpitch, dyaw, dbank

    def add_spin(self, dpitch, dyaw, dbank):
        self._dpitch += dpitch
        self._dyaw += dyaw
        self._dbank += dbank

    @property
    def spin(self):
        return self._dpitch, self._dyaw, self._dbank

    @property
    def movement(self):
        return self._dx, self._dy, self._dz

    @property
    def position(self):
        return self._x, self._y, self._z

    @property
    def rotation(self):
        return self._pitch, self._yaw, self._bank

    @property
    def pitch(self):
        return self._pitch

    @property
    def yaw(self):
        return self._yaw

    @property
    def bank(self):
        return self._bank
