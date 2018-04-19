from typing import List, Tuple
from itertools import product
from math import hypot, degrees

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

    def set_position_rotation(self, x, y, radii):
        super(MovingLine, self).set_position_rotation(x, y, radii)


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

    def movement_in_relation_to(self, other: 'MovingLine') -> MutableOffsets:
        delta_movement = self._movement - other._movement
        return delta_movement

    def time_to_impact(self, other: 'MovingLine'):
        original_other_radii = other.radii
        delta_movement = self.movement_in_relation_to(other)
        other.rotate(-original_other_radii)
        self.rotate(-original_other_radii)

        other_x = other.x1
        dx1 = other_x - self.x1
        dx2 = other_x - self.x2

        if self.dx != 0:
            own_k = self.dy / self.dx
            own_impact_y = self.y1 + own_k * dx1
        else:
            own_impact_y = self.y1
        if self.left < other_x < self.right and other.bottom < own_impact_y < other.top:
            return 0

        delta_movement.rotate(-degrees(original_other_radii))
        if delta_movement.x == 0:
            return None

        k = delta_movement.z / delta_movement.x

        if (dx1 > 0) != (dx2 > 0):
            print("Invert the lines!")
            return None

        impact_y1 = self.y1 + k * dx1
        impact_y2 = self.y2 + k * dx2
        if min(impact_y1, impact_y2) < other.bottom < other.top < max(impact_y1, impact_y2):
            print("Invert the lines!")
            return None

        impact1 = other.bottom < impact_y1 < other.top
        impact2 = other.bottom < impact_y2 < other.top
        print(dx1, dx2, k)
        print(other.bottom, other.top, impact_y1, impact_y2)

        other.rotate(original_other_radii)
        self.rotate(original_other_radii)

        if not impact1 and not impact2:
            return None

        time_to_impact1 = dx1 / delta_movement.x
        time_to_impact2 = dx2 / delta_movement.x

        if impact1 and not impact2:
            return time_to_impact1
        if impact2 and not impact1:
            return time_to_impact2
        return min(time_to_impact1, time_to_impact2)


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