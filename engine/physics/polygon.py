from typing import List
from math import radians
from itertools import compress

from shapely.geometry import LinearRing, LineString, MultiPoint

from engine.physics.line import Line


class BasePolygon(object):

    closed_shape_class_map = {
        True: LinearRing,
        False: LineString
    }

    def __init__(self, lines: List[Line], closed=True):
        self._lines = lines
        self._shape_class = self.closed_shape_class_map[closed]
        self.rotation = 0
        self.x = 0
        self.y = 0
        self._left = self._right = self._top = self._bottom = None
        self._moving_left = self._moving_right = self._moving_top = self._moving_bottom = None
        self.shape = self.make_shape
        self._moving_points = [(l.x1, l.y1) for l in self.lines]
        self._moving_shape = None

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

    @property
    def moving_shape(self):
        self._moving_shape = self._moving_shape or MultiPoint(self._moving_points).convex_hull
        return self._moving_shape

    def make_shape(self):
        coords = [(l.x1, l.y1) for l in self.lines]
        coords.append((self.lines[-1].x2, self.lines[-1].y2))
        self._shape = self._shape_class(coords)
        self.shape = self._default_shape_function
        return self._shape

    def shape(self):
        return self._shape

    def _default_shape_function(self):
        return self._shape

    def set_position_rotation(self, x, y, yaw_degrees):
        coords = [(l.x1, l.y1) for l in self.lines]
        for line in self.lines:
            line.set_position_rotation(x, y, radians(yaw_degrees))
        coords += [(l.x1, l.y1) for l in self.lines]
        self._moving_points = coords
        self._moving_shape = None
        self._left = self._right = self._top = self._bottom = None
        self._moving_left = self._moving_right = self._moving_top = self._moving_bottom = None
        self.shape = self.make_shape

    def clear_movement(self):
        self._moving_points = [(l.x1, l.y1) for l in self.lines]
        self._moving_left = self._moving_right = self._moving_top = self._moving_bottom = None

    def freeze(self):
        for line in self.lines:
            line.freeze()
        self.x = 0
        self.y = 0
        self.rotation = 0

    @property
    def left(self):
        self._left = self._left or min([line.left for line in self.lines])
        return self._left

    @property
    def right(self):
        self._right = self._right or max([line.right for line in self.lines])
        return self._right

    @property
    def top(self):
        self._top = self._top or max([line.top for line in self.lines])
        return self._top

    @property
    def bottom(self):
        self._bottom = self._bottom or min([line.bottom for line in self.lines])
        return self._bottom

    @property
    def moving_left(self):
        self._moving_left = self._moving_left or min([x for x, y in self._moving_points])
        return self._moving_left

    @property
    def moving_right(self):
        self._moving_right = self._moving_right or max([x for x, y in self._moving_points])
        return self._moving_right

    @property
    def moving_top(self):
        self._moving_top = self._moving_top or max([y for x, y in self._moving_points])
        return self._moving_top

    @property
    def moving_bottom(self):
        self._moving_bottom = self._moving_bottom or min([y for x, y in self._moving_points])
        return self._moving_bottom


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

    def movement_box_intersects(self, other: BasePolygon):
        if self.moving_right < other.moving_left:
            return False
        if self.moving_left > other.moving_right:
            return False
        if self.moving_top < other.moving_bottom:
            return False
        if self.moving_bottom > other.moving_top:
            return False
        return True

    def intersection_point(self, other: "Polygon"):
        return self._intersection_point(other)

    def _intersection_point(self, other: BasePolygon):
        if not self.movement_box_intersects(other):
            return False, None, None
        p1 = self.moving_shape
        p2 = other.moving_shape
        intersection = p1.intersection(p2)

        if not intersection.is_empty:
            point_x, point_y = intersection.centroid.x, intersection.centroid.y
        else:
            point_x, point_y = None, None
        return not intersection.is_empty, point_x, point_y

    def __iadd__(self, other: "Polygon"):
        p1 = self.make_shape()
        p2 = other.make_shape()
        new_shape = p1.union(p2)
        return self.manufacture(new_shape.coords)

    def __copy__(self):
        return self.manufacture([(l.original_x1, l.original_y1) for l in self.lines],self.x, self.y, self.rotation)


class TemporalPolygon(Polygon):

    def __init__(self, lines: List[Line], closed=True, line_mask=None):
        super().__init__(lines, closed=closed)
        self._line_mask = line_mask or [False] * len(lines)

    def enable_percent_lines(self, p: float):
        n = int(round(len(self._lines) * p))
        self._line_mask = [True] * n + [False] * (len(self._lines) - n)

    def set_line_mask(self, line_mask):
        self._line_mask = line_mask

    @property
    def lines(self) -> List[Line]:
        return list(compress(self.lines, self._line_mask))

    def intersection_point(self, other: "Polygon"):
        if sum(self._line_mask) == 0:
            return False, None, None
        return super(TemporalPolygon, self).intersection_point(other)
