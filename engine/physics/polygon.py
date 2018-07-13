from itertools import compress, product, chain
from math import radians
from typing import List, Iterator

from shapely.geometry import LinearRing, LineString, MultiPoint, Point

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
        polygon = cls(lines)
        polygon.set_position_rotation(x, y, rotation)
        polygon.clear_movement()
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
        self.x = x
        self.y = y
        self.rotation = yaw_degrees
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

    def __repr__(self):
        return f"{len(self.lines)}-sided at {self.x}, {self.y}"


class Polygon(BasePolygon):

    def centroid(self):
        c = self.shape().centroid
        return c.x, c.y

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

    def _intersection(self, other: "Polygon"):
        if not self.movement_box_intersects(other):
            return None
        p1 = self.moving_shape
        p2 = other.moving_shape
        intersection = p1.intersection(p2)
        if intersection.is_empty:
            return None
        return intersection

    def intersects(self, other: "Polygon"):
        intersection = self._intersection(other)
        return intersection is not None

    def intersection_point(self, other: "Polygon"):
        intersection = self._intersection(other)
        if intersection:
            point_x, point_y = intersection.centroid.x, intersection.centroid.y
        else:
            point_x, point_y = None, None
        return intersection is not None, point_x, point_y

    def point_inside(self, x, y):
        return self.moving_shape.contains(Point(x, y))

    def __iadd__(self, other: "Polygon"):
        p1 = self.make_shape()
        p2 = other.make_shape()
        new_shape = p1.union(p2)
        return self.manufacture(new_shape.coords)

    def __copy__(self):
        return self.manufacture([(l.original_x1, l.original_y1) for l in self.lines],self.x, self.y, self.rotation)


class PolygonPart(Polygon):

    def __init__(self, lines: List[Line]):
        super().__init__(lines)
        self._original_x = self.x
        self._original_y = self.y
        self._original_rotation = self.rotation

    def set_position_rotation(self, x, y, yaw_degrees):
        x += self._original_x
        y += self._original_y
        yaw_degrees += self._original_rotation
        super(PolygonPart, self).set_position_rotation(x, y, yaw_degrees)

    def freeze(self):
        super(PolygonPart, self).freeze()
        self._original_x = self.x
        self._original_y = self.y
        self._original_rotation = self.rotation
        super(PolygonPart, self).freeze()


class MultiPolygon(Polygon):

    def __init__(self, polygons: List[PolygonPart]):
        points = MultiPoint(list(chain(*[[(l.x1, l.y1) for l in p.lines] for p in polygons])))
        try:
            lines = self.coords_to_lines(points.convex_hull.exterior.coords)
        except AttributeError:
            lines = [Line([(p.x, p.y) for p in points])]
        super().__init__(lines)
        self._polygons = polygons

    def __iter__(self) -> Iterator[Polygon]:
        return self._polygons.__iter__()

    def __len__(self):
        return len(self._polygons)

    def intersected_polygons(self, other: "MultiPolygon"):
        own_intersections = set()
        other_intersections = set()
        if len(self) == 0 or len(other) == 0 or not self.intersects(other):
            return own_intersections, other_intersections

        for p1, p2 in product(self, other):
            if p1.intersects(p2):
                own_intersections.add(p1)
                other_intersections.add(p2)
        return own_intersections, other_intersections

    @classmethod
    def manufacture(cls, coords, x=0, y=0, rotation=0):
        lines = cls.coords_to_lines(coords)
        polygon = MultiPolygon([PolygonPart(lines)])
        polygon.set_position_rotation(x, y, rotation)
        polygon.clear_movement()
        return polygon

    def set_position_rotation(self, x, y, yaw_degrees):
        super(MultiPolygon, self).set_position_rotation(x, y, yaw_degrees)
        for polygon in self._polygons:
            polygon.set_position_rotation(x, y, yaw_degrees)


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
