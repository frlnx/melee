from collections import defaultdict
from math import cos, sin, radians
from typing import Callable, Set
from uuid import uuid4

from engine.physics.force import MutableOffsets, MutableDegrees, Offsets, MutableForce
from engine.physics.polygon import Polygon


class PositionalModel(object):

    def __init__(self, x=0, y=0, z=0, pitch=0, yaw=0, roll=0, name=None):
        self._x, self._y, self._z, self._pitch, self._yaw, self._roll = x, y, z, pitch, yaw, roll
        self._mesh_name = name
        self._name = name
        self._action_observers = defaultdict(set)
        self._material_observers = set()
        self.material_value = 0.0

    @property
    def name(self):
        return self._name

    def observe(self, func: Callable, action=None):
        self._action_observers[action].add(func)

    def _observe_original(self, func: Callable, action=None):
        self._action_observers[action].add(func)

    def _callback(self, action=None):
        for observer in self._action_observers[action]:
            observer()

    def unobserve(self, func: Callable, action=None):
        try:
            self._action_observers[action].remove(func)
        except KeyError:
            pass

    def remove_all_observers(self):
        self._action_observers.clear()

    def set_material_value(self, value):
        self.material_value = value
        self._callback("material")

    @property
    def mesh_name(self):
        return self._mesh_name

    @property
    def position(self):
        return self.x, self.y, self.z

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @property
    def pitch(self):
        return self._pitch

    @property
    def yaw(self):
        return self._yaw

    @property
    def roll(self):
        return self._roll


class BaseModel(PositionalModel):

    def __init__(self,
                 position: MutableOffsets,
                 rotation: MutableDegrees,
                 movement: MutableOffsets,
                 spin: MutableDegrees,
                 acceleration: MutableOffsets,
                 torque: MutableDegrees,
                 bounding_box: Polygon):
        super(BaseModel, self).__init__()
        self.uuid = uuid4()
        self._mass = 1
        self._position = position
        self._rotation = rotation
        self._movement = movement
        self._spin = spin
        self._acceleration = acceleration
        self._torque = torque
        self._bounding_box = bounding_box
        self._time_consumed = 0
        try:
            bb_width = (self._bounding_box.right - self._bounding_box.left)
            bb_height = (self._bounding_box.top - self._bounding_box.bottom)
            self.inertia = self._mass / 12 * (bb_width ** 2 + bb_height ** 2)
        except AttributeError:
            self.inertia = 1
        self.update_needed = False
        self._alive = True
        self._exploding = False
        self._explosion_time = 0.0
        self._collisions_to_solve = set()

    def parts_by_bounding_boxes(self, bounding_boxes: set):
        return {self}

    @property
    def destructive_energy(self):
        return 0

    def damage(self):
        pass

    @property
    def collisions_to_solve(self) -> Set[MutableForce]:
        return self._collisions_to_solve

    def energy_on_impact_relative_to(self, interception_vector):
        return self.mass * interception_vector.distance

    def __repr__(self):
        return "{} {}".format(self.__class__.__name__, self.uuid)

    def __getstate__(self):
        d = {k: val for k, val in self.__dict__.items()}
        d['_action_observers'] = set()
        d['_collisions_to_solve'] = set()
        return d

    def explode(self):
        if not self.is_exploding:
            self._exploding = True
            self._callback("explode")

    @property
    def explosion_timer(self):
        return self._explosion_time

    @property
    def is_exploding(self):
        return self._exploding

    @property
    def is_alive(self):
        return self._alive

    def set_alive(self, state):
        callback = self._alive != state
        self._alive = state
        if callback:
            self._callback("alive")

    @property
    def data_dict(self):
        return {"uuid": self.uuid, "position": list(self.position.xyz), "rotation": self.rotation.yaw,
                "movement": list(self.movement.xyz), "spin": self.spin.yaw,
                "acceleration": list(self.acceleration.xyz), "torque": self.torque.yaw}

    def set_data(self, data_dict: dict):
        assert data_dict['uuid'] == self.uuid
        self._position.set(*data_dict['position'])
        self._rotation.set(0, data_dict['rotation'], 0)
        self._movement.set(*data_dict['movement'])
        self._spin.set(0, data_dict['spin'], 0)
        self._acceleration.set(*data_dict['acceleration'])
        self._torque.set(0, data_dict['torque'], 0)
        self._bounding_box.set_position_rotation(self.x, self.z, self.yaw)

    def run(self, dt):
        half_of_acceleration = self.acceleration * dt / 2
        half_of_torque = self.torque * dt / 2
        self.reset_collisions()
        self.movement.translate(half_of_acceleration)
        self.spin.translate(half_of_torque)
        self.translate(*(self.movement * dt))
        self.rotate(*(self.spin * dt))
        self.movement.translate(half_of_acceleration)
        self.spin.translate(half_of_torque)
        self.timers(dt)

    def timers(self, dt):
        self._time_consumed += dt
        if self.is_exploding:
            self._explosion_time += dt
            if self.explosion_timer > 3.0:
                self.set_alive(False)
                self._exploding = False

    @property
    def time_consumed(self):
        return self._time_consumed

    @property
    def mass(self):
        return self._mass

    def apply_global_force(self, force: MutableForce):
        self.mutate_force_to_local(force)
        self.add_movement(*(force.translation_forces() / self.mass))
        self.add_spin(0, force.delta_yaw / self.inertia, 0)

    def mutate_force_to_local(self, mf: MutableForce):
        self.mutate_offsets_to_local(mf.position)
        mf.forces.rotate(self.yaw)

    def mutate_offsets_to_local(self, mo: MutableOffsets):
        mo -= self.position
        mo.rotate(self.yaw)

    def global_momentum_at(self, local_coordinates: MutableOffsets) -> MutableForce:
        force = self.momentum_at(local_coordinates)
        self.mutate_force_to_global(force)
        return force

    def momentum_at(self, local_coordinates: MutableOffsets) -> MutableForce:
        local_coordinates = MutableOffsets(*local_coordinates)
        momentum = self._movement  # * self.mass
        momentum += self.tangent_momentum_at(local_coordinates)
        momentum_at = MutableForce(local_coordinates, momentum)
        return momentum_at

    def mutate_force_to_global(self, mf: MutableForce):
        self.mutate_offsets_to_global(mf.position)
        mf.forces.rotate(-self.yaw)

    def mutate_offsets_to_global(self, mo: MutableOffsets):
        mo.rotate(-self.yaw)
        mo.translate(self.position)

    def tangent_momentum_at(self, local_coordinates: Offsets) -> Offsets:
        if local_coordinates.distance == 0:
            return MutableOffsets(0, 0, 0)
        yaw = local_coordinates.rotated(90) * (self._spin.yaw_radian * self.inertia / local_coordinates.distance)
        return yaw

    @property
    def bounding_box(self):
        return self._bounding_box

    def intersection_point(self, other_model):
        return self.bounding_box.intersection_point(other_model.bounding_box)

    def update(self):
        self._bounding_box.set_position_rotation(self.x, self.z, -self.yaw)
        self._callback()
        self.update_needed = True

    @property
    def name(self):
        return self.__class__.__name__

    def set_position_and_rotation(self, x, y, z, pitch, yaw, roll):
        if self._position.set(x, y, z) or self._rotation.set(pitch, yaw, roll):
            self.update()

    def set_position(self, x, y, z):
        if self._position.set(x, y, z):
            self.update()

    def translate(self, *xyz):
        self._position += xyz
        if xyz != (0, 0, 0):
            self.update()

    def rotate(self, *pitch_yaw_roll):
        self._rotation += pitch_yaw_roll
        if pitch_yaw_roll != (0, 0, 0):
            self.update()

    def set_rotation(self, *pitch_yaw_roll):
        if self._rotation.set(*pitch_yaw_roll):
            self.update()

    def set_movement(self, dx, dy, dz):
        if self._movement.set(dx, dy, dz):
            self.update()

    def add_movement(self, *xyz):
        self._movement += xyz
        if xyz != (0, 0, 0):
            self.update()

    def add_local_movement(self, x: float, y: float, z: float):
        theta = radians(self.yaw)
        sin_val = sin(theta)
        cos_val = cos(theta)
        self.add_movement(x * cos_val - z * sin_val, y, x * sin_val + z * cos_val)

    def set_spin(self, *pitch_yaw_roll):
        if self._spin.set(*pitch_yaw_roll):
            self.update()

    def add_spin(self, *pitch_yaw_roll):
        self._spin += pitch_yaw_roll
        if pitch_yaw_roll != (0, 0, 0):
            self.update()

    @property
    def torque(self):
        return self._torque

    @property
    def acceleration(self):
        return self._acceleration

    def set_local_acceleration(self, x: float, y: float, z: float):
        theta = radians(-self.yaw)
        sin_val = sin(theta)
        cos_val = cos(theta)
        self._acceleration.set(x * cos_val - z * sin_val, y, x * sin_val + z * cos_val)

    def add_acceleration(self, *xyz):
        self._acceleration += xyz

    def set_torque(self, *xyz):
        self._torque.set(*xyz)

    def add_torque(self, *xyz):
        self._torque += xyz

    def add_collision(self, force: MutableForce):
        self.mutate_force_to_local(force)
        self._movement += force.forces
        self._spin += (0, force.delta_yaw, 0)

    def reset_collisions(self):
        self._collisions_to_solve.clear()

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
