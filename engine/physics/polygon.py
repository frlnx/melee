from typing import List
from math import radians
from itertools import product
from functools import reduce

from shapely.geometry import LinearRing, LineString

from engine.physics.line import Line


class BasePolygon(object):


    def __init__(self, lines: List[Line]):
        self._lines = lines
        self.rotation = 0
        self.x = 0
        self.y = 0

    @classmethod
    def coords_to_lines(cls, coords, **kwargs):
        last_coord = coords[0]
        lines = [Line([coords[-1], coords[0]])]
        for coord in coords[1:]:
            lines.append(Line([last_coord, coord]))
            last_coord = coord
        return lines

    @classmethod
    def manufacture(cls, coords, x=0, y=0, rotation=0):
        lines = cls.coords_to_lines(coords)
        polygon = Polygon(lines)
        polygon.set_position_rotation(x, y, rotation)
        return polygon

    @property
    def lines(self) -> List[Line]:
        return self._lines

    def make_shape(self):
        if len(self.lines) > 1:
            coords = [(l.x1, l.y1) for l in self.lines]
            coords.append((self.lines[-1].x2, self.lines[-1].y2))
            return LinearRing(coords)
        else:
            line = self.lines[0]
            return LineString([(line.x1, line.y1), (line.x2, line.y2)])

    def set_position_rotation(self, x, y, yaw_degrees):
        for line in self.lines:
            line.set_position_rotation(x, y, radians(yaw_degrees))

    def freeze(self):
        for line in self.lines:
            line.freeze()
        self.x = 0
        self.y = 0
        self.rotation = 0

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

    def intersection_point(self, other: "Polygon"):
        return self._intersection_point(other)

    def _intersection_point(self, other: BasePolygon):
        if not self.bounding_box_intersects(other):
            return False, None, None
        p1 = self.make_shape()
        p2 = other.make_shape()
        intersection = p1.intersection(p2)
        if not intersection.is_empty:
            point_x, point_y = intersection.centroid.x, intersection.centroid.y
        else:
            point_x, point_y = 0, 0
        return not intersection.is_empty, point_x, point_y
        #
        # x_es = []
        # y_es = []
        # for line1, line2 in product(self.lines, other.lines):
        #     if not line1.bounding_box_intersects(line2):
        #         continue
        #     intersects, x, y = line1.intersection_point(line2)
        #     if intersects:
        #         x_es.append(x)
        #         y_es.append(y)
        # if x_es:
        #     x = reduce(lambda a, b: a + b, x_es) / len(x_es)
        #     y = reduce(lambda a, b: a + b, y_es) / len(y_es)
        #     return True, x, y
        # return False, None, None

    def __iadd__(self, other: "Polygon"):
        p1 = self.make_shape()
        p2 = other.make_shape()
        new_shape = p1.union(p2)
        return self.manufacture(new_shape.coords)
        #self._lines += [Line([(line.x1, line.y1), (line.x2, line.y2)]) for line in other.lines]
        #return self

    def __copy__(self):
        return self.manufacture([(l.original_x1, l.original_y1) for l in self.lines],self.x, self.y, self.rotation)
