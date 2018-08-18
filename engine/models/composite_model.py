from functools import partial
from itertools import combinations, chain
from typing import Set

from engine.models.base_model import BaseModel
from engine.models.part_connection import PartConnectionModel, ShieldConnectionModel, PartConnectionError
from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.polygon import MultiPolygon


class CompositeModel(BaseModel):
    def __init__(self, parts: Set[ShipPartModel], position: MutableOffsets,
                 rotation: MutableDegrees, movement: MutableOffsets, spin: MutableDegrees,
                 acceleration: MutableOffsets, torque: MutableDegrees):
        self._part_by_uuid = {part.uuid: part for part in parts}
        self._connections: Set[PartConnectionModel] = set()
        self._position = position
        self._rotation = rotation
        self._bounding_box = self._build_bounding_box(self.parts_of_bbox)
        super().__init__(position, rotation, movement, spin, acceleration, torque, self.bounding_box)
        self.rebuild_connections()
        self._calculate_mass()
        self._calculate_inertia()
        self._own_spawns = []
        for part in parts:
            part.observe(lambda: self.remove_part(part) if not part.is_alive else None, "alive")
            part.observe(self.prune_dead_parts_from_bounding_box, "explode")
            part.observe(self.rebuild, "move")
            part.observe(lambda: self.rebuild_connections_for(part), "move")

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
        for part in self.parts:
            if part.bounding_box.point_inside(x, z):
                return part

    @property
    def parts(self) -> Set[ShipPartModel]:
        return set(self._part_by_uuid.values())

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
        self._part_by_uuid.clear()
        for part in parts:
            self._add_part(part)
        self.rebuild()
        self.rebuild_connections()

    def add_part(self, part):
        self._add_part(part)
        self.rebuild()

    def _add_part(self, part):
        self._part_by_uuid[part.uuid] = part
        part.observe(lambda: self.remove_part(part) if not part.is_alive else None, "alive")
        part.observe(self.prune_dead_parts_from_bounding_box, "explode")
        part.observe(self.rebuild, "move")
        part.observe(lambda: self.rebuild_connections_for(part), "move")

    def remove_part(self, part_model):
        if part_model.uuid in self._part_by_uuid:
            del self._part_by_uuid[part_model.uuid]
            part_model.unobserve(self.prune_dead_parts_from_bounding_box, "explode")
            part_model.unobserve(self.rebuild, "move")
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
            bbox.set_position_rotation(part.x, part.z, part.yaw)
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

    def rebuild_connections(self):
        for part in self.parts:
            part.disconnect_all()
        self._connections.clear()
        for part1, part2 in combinations(self.parts, 2):
            self._try_to_connect(part1, part2)
        print(f'made {len(self._connections)} connections')
        for part in self.parts:
            part.update_working_status()

    def rebuild_connections_for(self, model: ShipPartModel):
        for part in self.parts:
            self._try_to_connect(model, part)

    def _try_to_connect(self, part1, part2):
        if part1 == part2:
            return False
        if not part1.can_connect_to(part2):
            return False
        try:
            connection = self._make_connection(part1, part2)
        except PartConnectionError as e:
            print(e)
            return False
        else:
            self._add_connection(connection)
            return True

    def disconnect_invalid_connections(self):
        for connection in self._connections.copy():
            if not connection.is_alive:
                self._remove_connection(connection)
                connection.disconnect_all()

    def _add_connection(self, connection: PartConnectionModel):
        if connection not in self._connections:
            self._connections.add(connection)
            connection.observe(lambda: self._remove_connection(connection), "broken")
            connection.observe(lambda: self._remove_connection(connection), "alive")
            self._callback("connection", added=connection)

    def _remove_connection(self, connection: PartConnectionModel):
        try:
            self._connections.remove(connection)
            connection.remove_all_observers()
            self._callback("disconnect", removed=connection)
        except KeyError:
            pass

    def _make_connection(self, part1: "ShipPartModel", part2: "ShipPartModel"):
        class_map = {"ShieldConnection": ShieldConnectionModel}
        config = part1.connection_configs.get(part2.name, {})
        connection_class = class_map.get(config.get('connection_class'), PartConnectionModel)
        func = partial(self._validation_function, {part1, part2})
        connection = connection_class(part1, part2,
                                      validate_connection_function=func,
                                      max_distance=config.get('distance', 1.7))
        if connection.is_valid:
            connection.observe(lambda: self._remove_connection(connection), "broken")
        else:
            raise PartConnectionError("Too far")
        return connection

    def _validation_function(self, ignored_parts: Set[ShipPartModel], polygon: "Polygon"):
        if not polygon:
            return False
        _, intersected_bboxes = polygon.intersected_polygons(self.bounding_box)
        ignored_uuids = {part.uuid for part in ignored_parts}
        intersected_uuids = {bbox.part_id for bbox in intersected_bboxes if bbox != polygon}
        return len(intersected_uuids - ignored_uuids) == 0

    @property
    def parts_of_bbox(self):
        return [part for part in chain(self.parts, self._connections) if part.is_alive and not part.is_exploding]

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
