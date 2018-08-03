from itertools import combinations
from typing import Set

from engine.models.base_model import BaseModel
from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.polygon import MultiPolygon


class CompositeModel(BaseModel):
    def __init__(self, parts: Set[BaseModel], position: MutableOffsets,
                 rotation: MutableDegrees, movement: MutableOffsets, spin: MutableDegrees,
                 acceleration: MutableOffsets, torque: MutableDegrees):
        self._parts = {(part.x, part.z): part for part in parts}
        self._part_by_uuid = {part.uuid: part for part in parts}
        self._rebuild_connections()
        self._position = position
        self._rotation = rotation
        bounding_box = self._build_bounding_box(self.parts_of_bbox)
        super().__init__(position, rotation, movement, spin, acceleration, torque, bounding_box)
        self._calculate_mass()
        self._calculate_inertia()
        self._own_spawns = []
        for part in parts:
            part.observe(lambda: self.remove_part(part) if not part.is_alive else None, "alive")
            part.observe(self.prune_dead_parts_from_bounding_box, "explode")

    def run(self, dt):
        super(CompositeModel, self).run(dt)
        for part in self.parts:
            part.run(dt)

    def parts_by_bounding_boxes(self, bounding_boxes: set):
        parts = set()
        for bbox in bounding_boxes:
            parts.add(self._part_by_uuid[bbox.part_id])
        return parts

    def part_at(self, x, z) -> ShipPartModel:
        for part in self._parts.values():
            if part.bounding_box.point_inside(x, z):
                return part

    @property
    def parts(self) -> Set[ShipPartModel]:
        return set(self._parts.values())

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

    def set_parts(self, parts: set):
        for removed_part in self.parts:
            removed_part.disconnect_all()
            removed_part.remove_all_observers()
        self._parts.clear()
        self._part_by_uuid.clear()
        self._parts = {(part.x, part.z): part for part in parts}
        self._part_by_uuid = {part.uuid: part for part in parts}
        for part in self.parts:
            part.observe(lambda: self.remove_part(part) if not part.is_alive else None, "alive")
            part.observe(self.rebuild, "explode")
            self._part_by_uuid[part.uuid] = part
        self.rebuild()
        self._rebuild_connections()

    def add_part(self, part):
        x, z = part.x, part.z
        self._parts[(x, z)] = part
        self._part_by_uuid[part.uuid] = part
        part.observe(lambda: self.remove_part(part) if not part.is_alive else None, "alive")
        part.observe(self.prune_dead_parts_from_bounding_box, "explode")
        self.rebuild()

    def remove_part(self, part_model):
        coords = (part_model.x, part_model.z)
        if coords in self._parts:
            del self._parts[coords]
        if part_model.uuid in self._part_by_uuid:
            del self._part_by_uuid[part_model.uuid]
            part_model.unobserve(self.prune_dead_parts_from_bounding_box, "explode")
        self.prune_dead_parts_from_bounding_box()
        if not self.parts:
            self.set_alive(False)

    def rebuild(self):
        if len(self.parts_of_bbox) > 0:
            self._bounding_box = self._build_bounding_box(self.parts_of_bbox)
            self._calculate_mass()
            self._calculate_inertia()
            self._callback("rebuild")
        else:
            self.set_alive(False)

    def _build_bounding_box(self, ship_parts: list) -> MultiPolygon:
        bboxes = set()
        for part in ship_parts:
            bbox = part.bounding_box.__copy__()
            bbox.part_id = part.uuid
            bbox.set_position_rotation(part.x, part.z, part.rotation.yaw)
            bbox.freeze()
            bbox.clear_movement()
            bboxes.add(bbox)
        bounding_box = MultiPolygon(bboxes)
        bounding_box.freeze()
        bounding_box.set_position_rotation(self.position.x, self.position.z, self.rotation.yaw)
        bounding_box.clear_movement()
        return bounding_box

    def prune_dead_parts_from_bounding_box(self):
        if len(self.parts_of_bbox) > 0:
            part_uuids = {part.uuid for part in self.parts if not part.is_alive or part.is_exploding}
            self.bounding_box.remove_polygons(part_uuids)
            self._calculate_mass()
            self._calculate_inertia()
            self._callback("rebuild")
        else:
            self.set_alive(False)

    def _calculate_mass(self):
        self._mass = sum([part.mass for part in self.parts_of_bbox])

    def _calculate_inertia(self):
        bb_width = (self._bounding_box.right - self._bounding_box.left)
        bb_height = (self._bounding_box.top - self._bounding_box.bottom)
        self.inertia = self._mass / 12 * (bb_width ** 2 + bb_height ** 2)

    def _rebuild_connections(self):
        for part in self.parts:
            part.disconnect_all()
        for part1, part2 in combinations(self.parts, 2):
            distance = (part1.position - part2.position).distance
            if distance < 1.7:
                part1.connect(part2)
            else:
                part1.disconnect(part2)
        for part in self.parts:
            part.update_working_status()

    @property
    def parts_of_bbox(self):
        return [part for part in self.parts if part.is_alive and not part.is_exploding]

    @property
    def acceleration(self):
        self._acceleration.set(0, 0, 0)
        for part in self.parts:
            self._acceleration += part.acceleration
        self._acceleration.rotate(-self.yaw)
        return self._acceleration

    @property
    def torque(self):
        self._torque.set(0, 0, 0)
        for part in self.parts:
            self._torque += part.torque
        return self._torque
