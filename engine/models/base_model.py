from typing import Tuple, Callable


class BaseModel(object):

    def __init__(self,
                 position: Tuple[float, float, float],
                 rotation: Tuple[float, float, float],
                 movement: Tuple[float, float, float],
                 spin: Tuple[float, float, float]):
        self._x, self._y, self._z = position
        self._pitch, self._yaw, self._roll = rotation
        self._dx, self._dy, self._dz = movement
        self._dpitch, self._dyaw, self._droll = spin
        self._observers = set()
        self._mesh = None

    @property
    def name(self):
        return "base"

    @property
    def mesh(self):
        return self._mesh

    def observe(self, func: Callable):
        self._observers.add(func)

    def _callback(self):
        for observer in self._observers:
            observer()

    def unobserve(self, func: Callable):
        try:
            self._observers.remove(func)
        except KeyError:
            pass

    def set_position_and_rotation(self, x, y, z, pitch, yaw, roll):
        self._x, self._y, self._z = x, y, z
        self._pitch, self._yaw, self._roll = pitch, yaw, roll
        self._callback()

    def set_position(self, x, y, z):
        self._x, self._y, self._z = x, y, z
        self._callback()

    def set_rotation(self, pitch, yaw, roll):
        self._pitch, self._yaw, self._roll = pitch, yaw, roll
        self._callback()

    def set_movement(self, dx, dy, dz):
        self._dx, self._dy, self._dz = dx, dy, dz

    def add_movement(self, dx, dy, dz):
        self._dx += dx
        self._dy += dy
        self._dz += dz

    def set_spin(self, dpitch, dyaw, droll):
        self._dpitch, self._dyaw, self._droll = dpitch, dyaw, droll

    def add_spin(self, dpitch, dyaw, droll):
        self._dpitch += dpitch
        self._dyaw += dyaw
        self._droll += droll

    @property
    def spin(self):
        return self._dpitch, self._dyaw, self._droll

    @property
    def movement(self):
        return self._dx, self._dy, self._dz

    @property
    def position(self):
        return self._x, self._y, self._z

    @property
    def rotation(self):
        return self._pitch, self._yaw, self._roll

    @property
    def pitch(self):
        return self._pitch

    @property
    def yaw(self):
        return self._yaw

    @property
    def roll(self):
        return self._roll
