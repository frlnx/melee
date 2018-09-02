from functools import partial
from itertools import combinations, chain
from typing import Set

from engine.models.base_model import BaseModel, RemoveCallbackException
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
            part.observe_with_self(self.remove_part, "alive")
            part.observe(self.prune_dead_parts_from_bounding_box, "explode")
            part.observe(self.rebuild, "move")
            part.observe_with_self(self.rebuild_connections_for, "move")
        for connection in self._connections:
            connection.update_polygon()

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
        part.observe_with_self(self.remove_part, "alive")
        part.observe(self.prune_dead_parts_from_bounding_box, "explode")
        part.observe(self.rebuild, "move")
        part.observe_with_self(self.rebuild_connections_for, "move")
        self._callback("add_part", added=part)

    def remove_part(self, part):
        if part.uuid in self._part_by_uuid:
            del self._part_by_uuid[part.uuid]
            part.unobserve_with_self(self.remove_part, "alive")
            part.unobserve(self.prune_dead_parts_from_bounding_box, "explode")
            part.unobserve(self.rebuild, "move")
            part.unobserve_with_self(self.rebuild_connections_for, "move")
            self._callback("remove_part", removed=part)
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
            raise RemoveCallbackException()

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
            raise RemoveCallbackException()

    def _calculate_mass(self):
        self._mass = sum([part.mass for part in self.parts_of_bbox])

    def _calculate_inertia(self):
        bb_width = (self._bounding_box.right - self._bounding_box.left)
        bb_height = (self._bounding_box.top - self._bounding_box.bottom)
        self.inertia = self._mass / 12 * (bb_width ** 2 + bb_height ** 2)

    def rebuild_connections(self):
        for connection in self._connections.copy():
            connection.disconnect_all()
        self._connections.clear()
        for part1, part2 in combinations(self.parts, 2):
            self._try_to_connect(part1, part2)
        outwards_parts = list(self.parts)
        outwards_parts.sort(key=lambda part: part.position.distance)
        for part in outwards_parts:
            part.update_working_status()

    def rebuild_connections_for(self, model: ShipPartModel):
        if not self.is_alive or not model.is_alive:
            raise RemoveCallbackException()
        for part in self.parts:
            if part not in model.connected_parts:
                self._try_to_connect(model, part)

    def _try_to_connect(self, part1, part2):
        if part1 == part2:
            return False
        if not part1.can_connect_to(part2):
            return False
        try:
            connection = self._make_connection(part1, part2)
        except PartConnectionError as e:
            return False
        else:
            if connection not in self._connections:
                self._add_connection(connection)
                return True
            else:
                return False

    def disconnect_invalid_connections(self):
        for connection in self._connections.copy():
            if not connection.is_alive:
                self._remove_connection(connection)
                connection.disconnect_all()

    def _add_connection(self, connection: PartConnectionModel):
        if connection not in self._connections:
            self._connections.add(connection)
            connection.observe_with_self(self._remove_connection, "broken")
            connection.observe_with_self(self._remove_connection, "alive")
            self._callback("connection", added=connection)

    def _remove_connection(self, connection: PartConnectionModel):
        try:
            self._connections.remove(connection)
        except KeyError:
            pass
        else:
            self._callback("disconnect", removed=connection)
            if not self.is_alive or not connection.is_alive:
                raise RemoveCallbackException()

    def _make_connection(self, part1: "ShipPartModel", part2: "ShipPartModel"):
        class_map = {"ShieldConnection": ShieldConnectionModel}
        config = part1.connection_configs.get(part2.name, {})
        connection_class = class_map.get(config.get('connection_class'), PartConnectionModel)
        func = partial(self._validation_function, {part1, part2})
        connection = connection_class(part1, part2,
                                      validate_connection_function=func,
                                      max_distance=config.get('distance', 1.7))
        if not connection.is_valid:
            connection.disconnect_all()
            raise PartConnectionError("Too far")
        return connection

    def _validation_function(self, ignored_parts: Set[ShipPartModel], local_polygon: "Polygon"):
        if not local_polygon:
            return False
        global_polygon = local_polygon.copy_to(self.bounding_box.x, self.bounding_box.y, self.bounding_box.rotation)
        _, intersected_bboxes = global_polygon.intersected_polygons(self.bounding_box)
        ignored_uuids = {part.uuid for part in ignored_parts}
        intersected_uuids = {bbox.part_id for bbox in intersected_bboxes
                             if bbox.part_id != global_polygon.part_id and bbox.part_id in self._part_by_uuid}
        intersected_uuids -= ignored_uuids
        return len(intersected_uuids) == 0

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
