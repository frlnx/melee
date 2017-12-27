from typing import Callable

from engine.physics.shape import Quad
from engine.physics.force import MutableOffsets, MutableDegrees, MutableForce


class BaseModel(object):

    def __init__(self,
                 position: MutableOffsets,
                 rotation: MutableDegrees,
                 movement: MutableOffsets,
                 spin: MutableDegrees):
        self._mass = 1
        self._position = position
        self._rotation = rotation
        self._movement = movement
        self._spin = spin
        self._observers = set()
        self._mesh = None
        x, z = position.x, position.z
        self._bounding_box = Quad([(-0.5 + x, -0.5 + z), (0.5 + x, -0.5 + z),
                                   (0.5 + x, 0.5 + z), (-0.5 + x, 0.5 + z)])
        bb_width = (self._bounding_box.right - self._bounding_box.left)
        bb_height = (self._bounding_box.top - self._bounding_box.bottom)
        self._inertia = self._mass / 12 * (bb_width ** 2 + bb_height ** 2)


    @property
    def mass(self):
        return self._mass

    @property
    def bounding_box(self):
        return self._bounding_box

    @property
    def outer_bounding_box(self):
        return self._bounding_box.outer_bounding_box

    def update(self):
        self._bounding_box.set_position_rotation(self.x, self.z, self.yaw)
        self._callback()

    def outer_bounding_box_after_rotation(self, degrees):
        return self._bounding_box.outer_bounds_after_rotation(degrees)

    @property
    def name(self):
        return self.__class__.__name__

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
        self._position.set(x, y, z)
        self._rotation.set(pitch, yaw, roll)
        self.update()

    def set_position(self, x, y, z):
        self._position.set(x, y, z)
        self.update()

    def translate(self, *xyz):
        self._position += xyz
        self.update()

    def rotate(self, *pitch_yaw_roll):
        self._rotation += pitch_yaw_roll
        self.update()

    def set_rotation(self, *pitch_yaw_roll):
        self._rotation.set(*pitch_yaw_roll)
        self.update()

    def set_movement(self, dx, dy, dz):
        self._movement.set(dx, dy, dz)

    def add_movement(self, *xyz: list):
        self._movement += xyz

    def set_spin(self, *pitch_yaw_roll):
        self._spin.set(*pitch_yaw_roll)

    def add_spin(self, *pitch_yaw_roll):
        self._spin += pitch_yaw_roll

    @property
    def spin(self):
        return self._spin

    @property
    def movement(self):
        return self._movement

    @property
    def position(self):
        return self._position

    @property
    def rotation(self):
        return self._rotation

    @property
    def x(self):
        return self._position.x

    @property
    def y(self):
        return self._position.y

    @property
    def z(self):
        return self._position.z

    @property
    def pitch(self):
        return self._rotation.pitch

    @property
    def yaw(self):
        return self._rotation.yaw

    @property
    def roll(self):
        return self._rotation.roll
