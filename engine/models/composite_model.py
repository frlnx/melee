from itertools import chain
from typing import Set

from shapely.geometry import MultiPoint

from engine.models.base_model import BaseModel
from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.polygon import Polygon


class CompositeModel(BaseModel):
    def __init__(self, parts: Set[BaseModel], position: MutableOffsets,
                 rotation: MutableDegrees, movement: MutableOffsets, spin: MutableDegrees,
                 acceleration: MutableOffsets, torque: MutableDegrees,
                 bounding_box: Polygon):
        super().__init__(position, rotation, movement, spin, acceleration, torque, bounding_box)
        self._parts = {(part.x, part.z): part for part in parts}
        self._mass = sum([part.mass for part in self.parts])
        bb_width = (self._bounding_box.right - self._bounding_box.left)
        bb_height = (self._bounding_box.top - self._bounding_box.bottom)
        self.inertia = self._mass / 12 * (bb_width ** 2 + bb_height ** 2)
        self._rebuild_observers = set()
        self._own_spawns = []

    def part_at(self, xyz):
        x, y, z = xyz
        return self._parts.get((int(round(x)), int(round(z))), None)

    @property
    def parts(self) -> Set[BaseModel]:
        return set(self._parts.values())

    def __getstate__(self):
        d = super(CompositeModel, self).__getstate__()
        d['_rebuild_observers'] = set()
        return d

    def observe_rebuild(self, func):
        self._rebuild_observers.add(func)

    def rebuild_callback(self):
        for callback in self._rebuild_observers:
            callback(self)

    def add_own_spawn(self, model: BaseModel):
        self._own_spawns.append(model)

    @property
    def spawns(self):
        spawns = self._own_spawns
        self._own_spawns = []
        for part in self.parts:
            if part.spawn:
                spawns.append(part.pop_spawn())
        return spawns

    def set_parts(self, parts):
        self.parts.clear()
        self.parts.update(parts)
        self.rebuild()

    def add_part(self, part_model):
        x, z = part_model.x, part_model.z
        self._parts[(x, z)] = part_model
        self.rebuild()

    def remove_part(self, part_model):
        coords = (part_model.x, part_model.z)
        if coords in self._parts:
            del self._parts[coords]
            self.rebuild()

    def rebuild(self):
        self._mass = sum([part.mass for part in self.parts])
        bb_width = (self._bounding_box.right - self._bounding_box.left)
        bb_height = (self._bounding_box.top - self._bounding_box.bottom)
        self.inertia = self._mass / 12 * (bb_width ** 2 + bb_height ** 2)
        points = MultiPoint(list(chain(*[[(l.x1, l.y1) for l in part.bounding_box.lines] for part in self.parts])))
        bounding_box = Polygon.manufacture(points.convex_hull.exterior.coords)
        bounding_box.freeze()
        bounding_box.set_position_rotation(self.position.x, self.position.z, self.rotation.yaw)
        self.rebuild_callback()

    def parts_intersected_by(self, other_model):
        intersects, x, z = self.intersection_point(other_model)
        if intersects:
            intersection_point = MutableOffsets(x, 0, z)
            self.mutate_offsets_to_local(intersection_point)
            part = self.part_at(intersection_point)
            if part:
                return [part]
        return []
