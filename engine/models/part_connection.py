from math import *
from typing import List, Callable

from engine.physics.line import Line
from engine.physics.polygon import Polygon
from .base_model import PositionalModel
from .ship_part import ShipPartModel


class PartConnectionModel(PositionalModel):
    
    def __init__(self, *ship_parts, validate_connection_function: Callable, max_distance=1.7):
        self._ship_parts: List[ShipPartModel] = list(ship_parts)
        if self._ship_parts[0].uuid > self._ship_parts[-1].uuid:
            self._ship_parts.reverse()
        super().__init__()
        self._max_distance = max_distance
        self.validate_connection_function = validate_connection_function
        self._connect()
        self._polygon: Polygon = self.build_polygon()
        self.uuid = self.generate_uuid()
        for part in self._ship_parts:
            part.observe(self.update_polygon)

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
        else:
            try:
                self._polygon = self.build_polygon()
            except AttributeError as e:
                self.disconnect_all()
        self._callback()

    @property
    def is_alive(self):
        return self.is_valid and sum(1 for p in self._ship_parts if p.is_alive) > 1

    @property
    def is_valid(self):
        return self.validate_connection_function(self._polygon) and self.distance <= self._max_distance

    @property
    def bounding_box(self):
        return self._polygon

    def build_polygon(self):
        lines = []
        for part, next_part in self._pairwise():
            lines.append(Line([(part.position.x, part.position.z), (next_part.position.x, next_part.position.z)]))
        polygon = Polygon(lines)
        if self.validate_connection_function(polygon):
            return polygon
        raise AttributeError(f"can't connect {self._ship_parts}")

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
        self.uuid = self.generate_uuid()
        if len(self._ship_parts) <= 1:
            self._callback("broken")

    def disconnect(self, part):
        self._disconnect(part)
        self.uuid = self.generate_uuid()
        if len(self._ship_parts) <= 1:
            self._callback("broken")

    def _disconnect(self, part: ShipPartModel):
        self._ship_parts.remove(part)
        part.unobserve(self.update_polygon)
        for other_part in self._ship_parts:
            part.disconnect(other_part)

    def __repr__(self):
        return str(self._ship_parts)


class ShieldConnectionModel(PartConnectionModel):

    base_arc = [(sin(radians(d)), cos(radians(d))) for d in range(0, 181, 36)]

    def build_polygon(self):
        arc: Polygon = None
        for part, next_part in self._pairwise():
            step_arc = self._build_arc(part, next_part)
            arc = arc and Polygon(arc.lines + step_arc.lines) or step_arc
        return arc
    
    def _build_arc(self, part1: ShipPartModel, part2: ShipPartModel) -> Polygon:
        start_point = part1.position.x, part1.position.z
        end_point = part2.position.x, part2.position.z
        straight_line = Line([start_point, end_point])
        c_x, c_y = straight_line.centroid
        for swell in range(0, 81, 20):
            swell /= 100
            radius = straight_line.length / 2
            for sign in [1, -1]:
                x_factor = swell * radius * sign
                coords = [(x * x_factor, y * radius) for x, y in self.base_arc]
                arc = Polygon.manufacture_open(coords, x=c_x, y=c_y, rotation=straight_line.degrees)
                arc.freeze()
                if self.validate_connection_function(arc):
                    return arc
        raise AttributeError(f'{part1} and {part2} have no valid arc')
