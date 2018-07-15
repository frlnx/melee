from typing import Set

from engine.models.base_model import BaseModel
from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.polygon import Polygon, MultiPolygon


class CompositeModel(BaseModel):
    def __init__(self, parts: Set[BaseModel], position: MutableOffsets,
                 rotation: MutableDegrees, movement: MutableOffsets, spin: MutableDegrees,
                 acceleration: MutableOffsets, torque: MutableDegrees,
                 bounding_box: Polygon):
        super().__init__(position, rotation, movement, spin, acceleration, torque, bounding_box)
        self._parts = {(part.x, part.z): part for part in parts}
        self._part_by_uuid = {part.uuid: part for part in parts}
        self._mass = sum([part.mass for part in self.parts])
        bb_width = (self._bounding_box.right - self._bounding_box.left)
        bb_height = (self._bounding_box.top - self._bounding_box.bottom)
        self.inertia = self._mass / 12 * (bb_width ** 2 + bb_height ** 2)
        self._own_spawns = []
        for part in parts:
            part.observe(lambda: self.remove_part(part) if not part.is_alive else None, "alive")

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

    def set_parts(self, parts):
        self.parts.clear()
        self.parts.update(parts)
        self._part_by_uuid.clear()
        for part in parts:
            part.observe(lambda: self.remove_part(part) if not part.is_alive else None, "alive")
            self._part_by_uuid[part.uuid] = part
        self.rebuild()

    def add_part(self, part):
        x, z = part.x, part.z
        self._parts[(x, z)] = part
        self._part_by_uuid[part.uuid] = part
        part.observe(lambda: self.remove_part(part) if not part.is_alive else None, "alive")
        self.rebuild()

    def remove_part(self, part_model):
        coords = (part_model.x, part_model.z)
        if coords in self._parts:
            del self._parts[coords]
        if part_model.uuid in self._part_by_uuid:
            del self._part_by_uuid[part_model.uuid]
        self.rebuild()

    def rebuild(self):
        if sum(part.is_alive for part in self.parts) > 0:
            self._mass = sum([part.mass if part.is_alive and not part.is_exploding else 0 for part in self.parts])
            bboxes = []
            for part in self.parts:
                if not part.is_alive or part.is_exploding:
                    continue
                bbox = part.bounding_box.__copy__()
                bbox.part_id = part.uuid
                bbox.set_position_rotation(part.x, part.z, part.rotation.yaw)
                bbox.freeze()
                bbox.clear_movement()
                bboxes.append(bbox)
            bounding_box = MultiPolygon(bboxes)
            bounding_box.freeze()
            bounding_box.set_position_rotation(self.position.x, self.position.z, self.rotation.yaw)
            bounding_box.clear_movement()
            self._bounding_box = bounding_box
            bb_width = (self._bounding_box.right - self._bounding_box.left)
            bb_height = (self._bounding_box.top - self._bounding_box.bottom)
            self.inertia = self._mass / 12 * (bb_width ** 2 + bb_height ** 2)
            self._callback("rebuild")
        else:
            self.set_alive(False)

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
