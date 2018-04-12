from typing import List, Tuple
from itertools import product
from math import hypot

from engine.physics.force import MutableOffsets, MutableDegrees
from .line import Line
from .polygon import Polygon


class MovingLine(Line):

    def __init__(self, coords: List[Tuple[float, float]], movement: MutableOffsets, spin: MutableDegrees):
        super().__init__(coords)
        self._movement = movement
        self._spin = spin
        self._sides = [Line(coords), Line(coords)]
        self._opposite = Line(coords)

    def render_movement_area(self, timeframe):
        side1, side2 = self._sides
        side1.x1 = self.x1
        side1.y1 = self.y1
        side2.x1 = self.x2
        side2.y1 = self.y2
        self._opposite.x1 = side1.x2 = self.x1 + self._movement.x * timeframe
        self._opposite.y1 = side1.y2 = self.y1 + self._movement.z * timeframe
        self._opposite.x2 = side2.x2 = self.x2 + self._movement.x * timeframe
        self._opposite.y2 = side2.y2 = self.y2 + self._movement.z * timeframe
        side1.freeze()
        side2.freeze()
        self._opposite.freeze()
        return side1, side2, self._opposite

    def bounding_box_intersects_in_timeframe(self, other: 'MovingLine', timeframe: float):
        self_x = self._movement.x * timeframe
        self_y = self._movement.z * timeframe
        other_x = other._movement.x * timeframe
        other_y = other._movement.z * timeframe
        if self.right + max(0, self_x) < other.left + min(0, other_x):
            return False
        if self.left + min(0, self_x) > other.right + max(0, other_x):
            return False
        if self.top + max(0, self_y) < other.bottom + min(0, other_y):
            return False
        if self.bottom + min(0, self_y) > other.top + max(0, other_y):
            return False
        return True

    def intersection_point_in_timeframe(self, other: 'MovingLine', timeframe: float):
        my_lines = self.render_movement_area(timeframe)
        other_lines = other.render_movement_area(timeframe)
        collision_times = set()
        for line1, line2 in product(my_lines[:-1], other_lines):
            if not line1.bounding_box_intersects(line2):
                continue
            intersects, x, y = line1.intersection_point(line2)
            if not intersects:
                continue
            intersection_distance = hypot(line1.x1 - x, line1.y1 - y)
            collision_time = self._movement.distance / intersection_distance
            collision_times.add(collision_time)
        return collision_times != set(), collision_times

    def time_to_impact(self, other: 'MovingLine'):
        delta_movement = self._movement - other._movement
        original_other_radii = other.radii
        other.rotate(-original_other_radii)
        self.rotate(-original_other_radii)
        delta_movement.rotate(-original_other_radii)
        if delta_movement.x == 0:
            intersects = self.left < other.x1 < self.right
            self.dx
        else:
            dx, dy = self.min_distance(other)
            k = delta_movement.y / delta_movement.x
            if other.x1 < self.left:
                dx = self.left - other.x1
            elif other.x1 > self.right:
                dx = self.right - other.x1
            elif self.left < other.x1 < self.right:
                dx = 0
            else:
                dx = 0
            rotated_y = k * dx +
            ############################
            k = self.dy / self.dx
            dx = self.x1 - other.x1
            rotated_y = k * dx + self.y1
            rotated_x = other.x1
            intersects = other.bottom < rotated_y < other.top and self.left < rotated_x < self.right
            cos_val = cos(original_other_radii)
            sin_val = sin(original_other_radii)
            point_x = rotated_x * cos_val - rotated_y * sin_val
            point_y = rotated_x * sin_val + rotated_y * cos_val
        other.rotate(original_other_radii)
        self.rotate(original_other_radii)
        return intersects, point_x, point_y


class MovingPolygon(Polygon):

    _line_class = MovingLine

    def __init__(self, lines: List[Line], movement: MutableOffsets, spin: MutableDegrees):
        super().__init__(lines)
        self._movement = movement
        self._spin = spin

    @classmethod
    def coords_to_lines(cls, coords, **kwargs):
        last_coord = coords[0]
        lines = [MovingLine([coords[-1], coords[0]], **kwargs)]
        for coord in coords[1:]:
            lines.append(MovingLine([last_coord, coord], **kwargs))
            last_coord = coord
        return lines

    @classmethod
    def manufacture_moving_polygon(cls, coords, movement, spin, x=0, y=0, rotation=0):
        lines = cls.coords_to_lines(coords, movement=movement, spin=spin)
        polygon = cls(lines, movement=movement, spin=spin)
        polygon.set_position_rotation(x, y, rotation)
        return polygon

    def bounding_box_intersects_in_timeframe(self, other: 'MovingPolygon', timeframe: float):
        self_x = self._movement.x * timeframe
        self_y = self._movement.z * timeframe
        other_x = other._movement.x * timeframe
        other_y = other._movement.z * timeframe
        if self.right + max(0, self_x) < other.left + min(0, other_x):
            return False
        if self.left + min(0, self_x) > other.right + max(0, other_x):
            return False
        if self.top + max(0, self_y) < other.bottom + min(0, other_y):
            return False
        if self.bottom + min(0, self_y) > other.top + max(0, other_y):
            return False
        return True

    def intersection_point_in_timeframe(self, other: 'MovingPolygon', timeframe: float):
        if not self.bounding_box_intersects_in_timeframe(other, timeframe):
            return False, None, None, None
        times = set()
        for line1, line2 in product(self.lines, other.lines):
            if not line1.bounding_box_intersects_in_timeframe(line2, timeframe):
                continue
            intersects, new_times = line1.intersection_point_in_timeframe(line2, timeframe)
            times.update(new_times)
        return times != set(), times