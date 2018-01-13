from typing import List, Tuple
from math import degrees, radians, cos, sin, atan2
from itertools import product


from engine.physics.line import Line


class BasePolygon(object):

    def __init__(self, lines: List[Line]):
        self._lines = lines

    @staticmethod
    def manufacture(coords, x=0, y=0, rotation=0):
        last_coord = coords[0]
        lines = [Line([coords[-1], coords[0]])]
        for coord in coords[1:]:
            lines.append(Line([last_coord, coord]))
            last_coord = coord
        polygon = Polygon(lines)
        polygon.set_position_rotation(x, y, rotation)
        polygon.freeze()
        return polygon

    @property
    def lines(self) -> List[Line]:
        return self._lines

    def set_position_rotation(self, x, y, yaw_degrees):
        for line in self.lines:
            line.set_position_rotation(x, y, radians(yaw_degrees))

    def freeze(self):
        for line in self.lines:
            line.freeze()

    @property
    def left(self):
        return min([line.left for line in self.lines])

    @property
    def right(self):
        return max([line.right for line in self.lines])

    @property
    def top(self):
        return max([line.top for line in self.lines])

    @property
    def bottom(self):
        return min([line.bottom for line in self.lines])


class Polygon(BasePolygon):

    def bounding_box_intersects(self, other: BasePolygon):
        if self.right < other.left:
            return False
        if self.left > other.right:
            return False
        if self.top < other.bottom:
            return False
        if self.bottom > other.top:
            return False
        return True

    def intersection_point(self, other: BasePolygon):
        n_intersections = 0
        sum_x = 0
        sum_y = 0
        for line1, line2 in product(self.lines, other.lines):
            if not line1.bounding_box_intersects(line2):
                continue
            intersects, x, y = line1.intersection_point(line2)
            if intersects:
                sum_x += x
                sum_y += y
                n_intersections += 1
        if n_intersections > 0:
            return True, sum_x / n_intersections, sum_y / n_intersections
        return False, None, None

    def __iadd__(self, other):
        other.freeze()
        self._lines += other.lines
        return self
