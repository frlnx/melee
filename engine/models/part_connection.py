from math import *
from typing import List, Callable

from engine.models.observable import RemoveCallbackException
from engine.physics.line import Line
from engine.physics.polygon import Polygon, ClippingPolygon
from .base_model import AnimationModel
from .ship_part import ShipPartModel


class PartConnectionError(AttributeError):
    pass


class PartConnectionModel(AnimationModel):

    mass = 0

    def __init__(self, *ship_parts, validate_connection_function: Callable, max_distance=1.7):
        self._ship_parts: List[ShipPartModel] = list(ship_parts)
        if self._ship_parts[0].uuid > self._ship_parts[-1].uuid:
            self._ship_parts.reverse()
        super().__init__()
        self.uuid = self.generate_uuid()
        self._max_distance = max_distance
        self.validate_connection_function = validate_connection_function
        self._polygon: Polygon = self.build_polygon()
        self.adjust_polygon()
        self._connect()
        self._alive = self.is_valid
        for part in self._ship_parts:
            part.observe(self.update_polygon, "move")
            part.observe(lambda: self._callback("alive"), "alive")
            part.observe(lambda: self._callback("alive"), "explode")

    def _pairwise(self):
        return zip(self._ship_parts[:-1], self._ship_parts[1:])

    def __eq__(self, other: "PartConnectionModel"):
        return self._ship_parts.__eq__(other._ship_parts)

    def __hash__(self):
        return self.uuid.__hash__()

    def generate_uuid(self):
        return "|".join(part.uuid.hex for part in self._ship_parts)

    def update_polygon(self):
        if self.distance > self._max_distance:
            self.disconnect_all()
            raise RemoveCallbackException()
        else:
            try:
                self.adjust_polygon()
            except PartConnectionError:
                self.disconnect_all()
                raise RemoveCallbackException()
            finally:
                self._callback("move")

    def adjust_polygon(self):
        if self._n_parts_alive <= 1:
            self._callback("broken")
            raise PartConnectionError("Not enough parts")
        start = self._ship_parts[0].position.x, self._ship_parts[0].position.z
        end = self._ship_parts[-1].position.x, self._ship_parts[-1].position.z
        line = self._polygon.lines[0]
        line.set_points(start, end)
        if not self.is_valid:
            self._alive = False
            self.disconnect_all()
            raise PartConnectionError(f'{self._ship_parts} have no valid arc')

    @property
    def is_alive(self):
        return self._alive and self._n_parts_alive > 1

    @property
    def _n_parts_alive(self):
        return sum(1 for p in self._ship_parts if p.is_alive and not p.is_exploding)

    @property
    def is_valid(self):
        return self.distance <= self._max_distance and self.validate_connection_function(self._polygon)

    @property
    def bounding_box(self):
        return self._polygon

    def build_polygon(self):
        if self._n_parts_alive <= 1:
            self._callback("broken")
            raise PartConnectionError("Not enough parts")
        lines = []
        for part, next_part in self._pairwise():
            lines.append(Line([(part.position.x, part.position.z), (next_part.position.x, next_part.position.z)]))
        polygon = Polygon(lines)
        #if self.validate_connection_function(polygon):
        return polygon
        #raise PartConnectionError(f"can't connect {self._ship_parts}")

    def validate_connection_function(self, polygon: Polygon):
        return False

    def _connect(self):
        for part, next_part in self._pairwise():
            part.connect(next_part)

    @property
    def distance(self):
        distance = 0
        for part, next_part in self._pairwise():
            distance += (part.position - next_part.position).distance
        return distance

    def disconnect_all(self):
        for part in self._ship_parts:
            self._disconnect(part)
        if self._n_parts_alive <= 1:
            self._callback("broken")

    def disconnect(self, part):
        self._disconnect(part)
        if self._n_parts_alive <= 1:
            self._callback("broken")
        self.uuid = self.generate_uuid()

    def _disconnect(self, part: ShipPartModel):
        self._ship_parts.remove(part)
        part.unobserve(self.update_polygon, "move")
        for other_part in self._ship_parts:
            part.disconnect(other_part)

    def __repr__(self):
        return "PartConnection: " + " -> ".join([part.name for part in self._ship_parts])

    @property
    def is_shield(self):
        return False


class ShieldConnectionModel(PartConnectionModel):

    base_arc = [(sin(radians(d)), cos(radians(d))) for d in range(0, 181, 36)]
    swells = [swell / 100 * sign for swell in range(0, 81, 5) for sign in [1, -1]][1:]
    mass = 0
    _polygon: ClippingPolygon

    def __init__(self, *ship_parts, validate_connection_function: Callable, max_distance=1.7):
        super().__init__(*ship_parts, validate_connection_function=validate_connection_function,
                         max_distance=max_distance)
        self._charge = 0
        for part in self._ship_parts:
            part.observe(self.load_charge, "load_charge")

    def _disconnect(self, part):
        part.unobserve(self.load_charge, "load_charge")
        super(ShieldConnectionModel, self)._disconnect(part)

    def load_charge(self, amount):
        if self._charge < 1.0:
            self._charge += amount
            self._charge = max(self._charge, 1.0)
            n_lines = len(self.base_arc)
            self._polygon.set_active_lines(*[(i - n_lines / 2) / n_lines / 2 < self._charge for i in range(n_lines)])

    @property
    def is_shield(self):
        return True

    def damage(self):
        self._polygon.set_active_lines(*[False] * len(self.base_arc))
        self._callback("move")

    def build_polygon(self):
        if self._n_parts_alive <= 1:
            self._callback("broken")
            raise PartConnectionError("Not enough parts")
        start_x, start_y = self._ship_parts[0].position.x, self._ship_parts[0].position.z
        end_x, end_y = self._ship_parts[-1].position.x, self._ship_parts[-1].position.z
        dx, dy = end_x - start_x, end_y - start_y
        cx, cy = start_x + dx / 2, start_y + dy / 2
        rotation = degrees(atan2(dx, dy))
        coords = [(i * dx / 6, i * dy / 6) for i in range(6)]
        arc: Polygon = ClippingPolygon.manufacture_open(coords, cx, cy, rotation, self.uuid)
        return arc

    def adjust_polygon(self):
        if self._n_parts_alive <= 1:
            self._callback("broken")
            raise PartConnectionError("Not enough parts")
        start_x, start_y = self._ship_parts[0].position.x, self._ship_parts[0].position.z
        end_x, end_y = self._ship_parts[-1].position.x, self._ship_parts[-1].position.z
        dx, dy = end_x - start_x, end_y - start_y
        cx, cy = start_x + dx / 2, start_y + dy / 2
        rotation = degrees(atan2(-dx, dy))
        radius = hypot(dx, dy) / 2
        for swell in self.swells:
            coords = self._build_arc_coords(swell, radius)
            self._polygon.update_coords(coords, cx, cy, rotation)
            if self.is_valid:
                return
        self.disconnect_all()
        self._alive = False
        raise PartConnectionError(f'{self._ship_parts} have no valid arc')

    def _build_arc_coords(self, swell, radius):
        x_factor = swell * radius
        coords = [(x * x_factor, y * radius) for x, y in self.base_arc]
        return coords
