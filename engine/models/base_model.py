from collections import defaultdict
from math import cos, sin, radians
from uuid import uuid4

from engine.models.observable import Observable
from engine.physics.force import MutableOffsets, MutableDegrees, Offsets, MutableForce, MutableUnboundDegrees
from engine.physics.polygon import MultiPolygon


class PositionalModel(Observable):

    destructable = True

    def __init__(self, x=0, y=0, z=0, pitch=0, yaw=0, roll=0, name=None):
        Observable.__init__(self)
        self._position = MutableOffsets(x, y, z)
        self._rotation = MutableDegrees(pitch, yaw, roll)
        self._mesh_name = name
        self._name = name
        self.material_value = 0.0
        self._mass = 1

    @property
    def mass(self):
        return self._mass

    @property
    def is_alive(self):
        return True

    @property
    def spawns(self):
        return []

    @property
    def name(self):
        return self._name

    @property
    def is_exploding(self):
        return False

    def set_material_value(self, value):
        self.material_value = value
        self._callback("material")

    @property
    def mesh_name(self):
        return self._mesh_name

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


class AnimationModel(PositionalModel):

    def __init__(self, x=0, y=0, z=0, pitch=0, yaw=0, roll=0, name=None):
        super().__init__(x, y, z, pitch, yaw, roll, name)
        self._time_consumed = 0
        self._explosion_time = 0
        self._exploding = False
        self._alive = True

    def run(self, dt):
        self.timers(dt)

    def timers(self, dt):
        self._time_consumed += dt
        if self.is_exploding:
            self._explosion_time += dt
            if self.explosion_timer > 3.0:
                self.set_alive(False)
                self._exploding = False

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


class BaseModel(AnimationModel):

    def __init__(self,
                 position: MutableOffsets,
                 rotation: MutableDegrees,
                 movement: MutableOffsets,
                 spin: MutableUnboundDegrees,
                 acceleration: MutableOffsets,
                 torque: MutableUnboundDegrees,
                 bounding_box: MultiPolygon):
        super(BaseModel, self).__init__()
        self.uuid = uuid4()
        self._position = position
        self._rotation = rotation
        self._movement = movement
        self._spin = spin
        self._acceleration = acceleration
        self._torque = torque
        self._bounding_box = bounding_box
        try:
            bb_width = (self._bounding_box.right - self._bounding_box.left)
            bb_height = (self._bounding_box.top - self._bounding_box.bottom)
            self.inertia = self.mass / 12 * (bb_width ** 2 + bb_height ** 2)
        except AttributeError:
            self.inertia = 1
        self.bounding_box_update_needed = False

    def __eq__(self, other):
        return other is not None and self.__class__ == other.__class__ and self.uuid == other.uuid

    def __hash__(self):
        return self.uuid.__hash__()

    def __gt__(self, other):
        return self.uuid > other.uuid

    def parts_by_bounding_boxes(self, bounding_boxes: set):
        return {self}

    @property
    def destructive_energy(self):
        return 0

    def damage(self):
        pass

    def polygons_in_order_of_collision(self, other: "BaseModel"):
        if self.is_exploding or other.is_exploding:
            return set(), set()
        own_intersections, other_intersections = self.bounding_box.intersected_polygons(other.bounding_box)
        delta_movement = self.movement - other.movement
        r = delta_movement.direction.yaw_radian

        def order_by_direction(part):
            x, y = part._centroid()
            return x * sin(r) + y * cos(r)
        if self.destructable:
            own_intersections = sorted(own_intersections, key=order_by_direction)
        if other.destructable:
            other_intersections = sorted(other_intersections, key=order_by_direction)
            other_intersections.reverse()
        return own_intersections, other_intersections

    def __repr__(self):
        return "{} {}".format(self.__class__.__name__, self.uuid)

    def __getstate__(self):
        d = {k: val for k, val in self.__dict__.items()}
        d['_action_observers'] = defaultdict(set)
        return d

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
        super(BaseModel, self).run(dt)
        half_of_acceleration = self.acceleration * dt / 2
        half_of_torque = self.torque * dt / 2
        self.movement.translate(half_of_acceleration)
        self.spin.translate(half_of_torque)
        self.translate(*(self.movement * dt))
        self.rotate(*(self.spin * dt))
        self.movement.translate(half_of_acceleration)
        self.spin.translate(half_of_torque)
        if self.bounding_box_update_needed:
            self.update_bounding_box()

    def update_bounding_box(self):
        self._bounding_box.set_position_rotation(self.x, self.z, -self.yaw)
        self.bounding_box_update_needed = False

    @property
    def time_consumed(self):
        return self._time_consumed

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
        self._callback("move")
        self.bounding_box_update_needed = True

    @property
    def name(self):
        return self.__class__.__name__

    def set_position_and_rotation(self, x, y, z, pitch, yaw, roll):
        if self._position.set(x, y, z) or self._rotation.set(pitch, yaw, roll):
            self.update()

    def set_position(self, x, y, z):
        if self._position.set(x, y, z):
            self.update()

    def teleport_to(self, x, y, z):
        if self._position.set(x, y, z):
            self.update_bounding_box()
            self.bounding_box.clear_movement()
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

    def teleport_screw(self, *pitch_yaw_roll):
        if self._rotation.set(*pitch_yaw_roll):
            self.update_bounding_box()
            self.bounding_box.clear_movement()
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

    @property
    def spin(self):
        return self._spin

    @property
    def movement(self):
        return self._movement
