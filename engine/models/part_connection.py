from itertools import product
from math import *
from typing import List, Callable

from engine.physics.line import Line
from engine.physics.polygon import Polygon
from .base_model import PositionalModel
from .ship_part import ShipPartModel


class PartConnectionModel(PositionalModel):
    
    def __init__(self, *ship_parts, validate_connection_function: Callable = None):
        super().__init__()
        self._ship_parts: List[ShipPartModel] = ship_parts
        self.validate_connection_function = validate_connection_function
        self._connect()
        self._polygon: Polygon = self.build_polygon()
        #for part in self._ship_parts:
        #    part.observe(self.update_polygon)

    def update_polygon(self):
        self._polygon = self.build_polygon()
        self._callback()

    @property
    def bounding_box(self):
        return self._polygon

    def build_polygon(self):
        lines = []
        for i, part in enumerate(self._ship_parts[:-1]):
            next_part = self._ship_parts[i + 1]
            lines.append(Line([(part.position.x, part.position.z), (next_part.position.x, next_part.position.z)]))
        polygon = Polygon(lines)
        if self.validate_connection_function(polygon):
            return polygon
        raise AttributeError(f"can't connect {self._ship_parts}")

    def validate_connection_function(self, polygon: Polygon):
        return False

    def _connect(self):
        for i, part in enumerate(self._ship_parts[:-1]):
            next_part = self._ship_parts[i + 1]
            part.connect(next_part)

    @property
    def distance(self):
        distance = 0
        for i, part in enumerate(self._ship_parts[:-1]):
            next_part = self._ship_parts[i + 1]
            distance += (part.position - next_part.position).distance
        return distance
    
    def _disconnect(self, part: ShipPartModel):
        self._ship_parts.remove(part)
        part.unobserve(self.update_polygon)
        for other_part in self._ship_parts:
            part.disconnect(other_part)
    
    def _disconnect_all(self):
        for p1, p2 in product(self._ship_parts):
            p1.disconnect(p2)


class ShieldConnectionModel(PartConnectionModel):

    def build_polygon(self):
        arc: Polygon = None
        for i, part in enumerate(self._ship_parts[:-1]):
            next_part = self._ship_parts[i + 1]
            step_arc = self._build_arc(part, next_part)
            arc = arc and Polygon(arc.lines + step_arc.lines) or step_arc
        return arc
    
    def _build_arc(self, part1: ShipPartModel, part2: ShipPartModel) -> Polygon:
        start_point = part1.position.x, part1.position.z
        end_point = part2.position.x, part2.position.z
        straight_line = Line([start_point, end_point])
        c_x, c_y = straight_line.centroid
        for swell in range(0, 100, 20):
            swell /= 100
            radius = straight_line.length / 2
            for sign in [1, -1]:
                x_factor = swell * radius * sign
                coords = [(sin(radians(d)) * x_factor, cos(radians(d)) * radius) for d in range(0, 180, 36)]
                arc = Polygon.manufacture(coords, x=c_x, y=c_y, rotation=straight_line.rotation)
                if self.validate_connection_function(arc):
                    return arc
        raise AttributeError(f'{part1} and {part2} have no valid arc')

