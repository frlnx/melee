from functools import reduce
from itertools import compress, product, chain
from math import radians, atan2, degrees
from typing import List, Iterator
from uuid import uuid4

from engine.physics.line import Line


class BasePolygon(object):

    def __init__(self, lines: List[Line], closed=True, part_id=None):
        self.part_id = part_id or uuid4().hex
        self._lines = lines
        self._shape = None
        self.rotation = 0
        self.x = 0
        self.y = 0
        self._left = self._right = self._top = self._bottom = None
        self._moving_left = self._moving_right = self._moving_top = self._moving_bottom = None
        self._moving_points = [(l.x1, l.y1) for l in self.lines]
        self._moving_shape = None

    def __hash__(self):
        return self.part_id.__hash__()

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.part_id == other.part_id

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
    def moving_polygon(self) -> "Polygon":
        point_string = self.convex_hull(self._moving_points)
        return Polygon.manufacture(coords=point_string)

    @property
    def moving_lines(self):
        return self.moving_polygon.lines

    @classmethod
    def convex_hull(cls, points):
        points = list(set(points))
        if len(points) <= 3:
            return points
        y_es = [p[1] for p in points]
        smallest_y = min(y_es)
        smallest_y_index = y_es.index(smallest_y)
        starting_point = points[smallest_y_index]
        point_string = [starting_point]
        last_angle = 0
        while True:
            last_point = point_string[-1]
            eval_points = list(points)
            eval_points.remove(last_point)
            angles = cls.get_angles_for_points_from_point(last_point, eval_points)
            delta_angles = [cls.delta_angle(a, last_angle) % 360 for a in angles]
            min_angle = min(delta_angles)
            min_angle_point = eval_points[delta_angles.index(min_angle)]
            if min_angle_point in point_string:
                return point_string[point_string.index(min_angle_point):]
            point_string.append(min_angle_point)
            last_angle += min_angle

    @classmethod
    def delta_angle(cls, angle, reference_angle):
        return (((angle % 360) - (reference_angle % 360) + 180) % 360) - 180

    @classmethod
    def get_angles_for_points_from_point(cls, point, points):
        x1, y1 = point
        angles = []
        for p in points:
            x2, y2 = p
            angle = atan2(y2 - y1, x2 - x1)
            angle = degrees(angle)
            angles.append(angle)
        return angles

    def _default_shape_function(self):
        return self._shape

    def set_position_rotation(self, x, y, yaw_degrees):
        self.x = x
        self.y = y
        self.rotation = yaw_degrees
        self._moving_points.clear()
        for line in self.lines:
            self._moving_points.append((line.x1, line.y1))
            if line.set_position_rotation(x, y, radians(yaw_degrees)):
                self._moving_points.append((line.x1, line.y1))
        self._moving_shape = None
        self._left = self._right = self._top = self._bottom = None
        self._moving_left = self._moving_right = self._moving_top = self._moving_bottom = None
        #  self.shape = self.make_shape

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
        return f"{self.part_id} {len(self.lines)}-sided at {self.x}, {self.y}"


class Polygon(BasePolygon):

    def centroid(self):
        points = [l.centroid for l in self.lines]
        centroid = reduce(lambda a, b: (a[0] + b[0], a[1] + b[1]), points)
        return centroid[0] / len(points), centroid[1] / len(points)

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

    def _intersection_polygon(self, other: "Polygon"):
        if not self.movement_box_intersects(other):
            return None




        primary_iter = iter(self.lines)
        secondary_iter = iter(other.lines)
        points = []

        intersects = False
        x, y = None, None
        for l1 in primary_iter:
            for l2 in secondary_iter:
                intersects, x, y = l1.intersection_point(l2)
                if intersects:
                    break
            if intersects:
                break
        if not intersects:
            return None
        points.append((x, y))
        primary_iter, secondary_iter = secondary_iter, primary_iter

        points = set()
        intersects = False
        for l1, l2 in product(self.lines, other.lines):
            line_intersects, point_x, point_y = l1.intersection_point(l2)
            if line_intersects:
                intersects = True
                points.add((point_x, point_y))
        own_break_lines = [Line([l.x1, l.y1, other.left - 1, other.bottom - 1]) for l in self.lines]
        own_break_lines += [Line([l.x2, l.y2, other.left - 1, other.bottom - 1]) for l in self.lines]
        other_break_lines = [Line([l.x1, l.y1, self.left - 1, self.bottom - 1]) for l in other.lines]
        other_break_lines += [Line([l.x2, l.y2, self.left - 1, self.bottom - 1]) for l in other.lines]
        for l1, l2 in product(self.lines, other_break_lines):
            line_intersects, point_x, point_y = l1.intersection_point(l2)
            if line_intersects:
                intersects = True
                points.add((point_x, point_y))

        for l1, l2 in product(own_break_lines, other.lines):
            line_intersects, point_x, point_y = l1.intersection_point(l2)
            if line_intersects:
                intersects = True
                points.add((point_x, point_y))

        return

    def intersects(self, other):
        try:
            for l1, l2 in product(self.moving_lines, other.moving_lines):
                intersects, x, y = l1.intersection_point(l2)
                if intersects:
                    return True
        except AttributeError:
            for l1 in self.moving_lines:
                intersects, x, y = l1.intersection_point(other)
                if intersects:
                    return True
        return False

    def intersection_point(self, other):
        if isinstance(other, Polygon):
            for l1, l2 in product(self.moving_lines, other.moving_lines):
                intersects, x, y = l1.intersection_point(l2)
                if intersects:
                    return True, x, y
        elif isinstance(other, Line):
            for l1 in self.moving_lines:
                intersects, x, y = l1.intersection_point(other)
                if intersects:
                    return True, x, y
        return False, None, None

    def point_inside(self, x, y):
        outside_point = (self.moving_polygon.left - 1, self.moving_polygon.bottom - 1)
        break_line = Line([(x, y), outside_point])
        n_broken_lines = sum(int(l.intersection_point(break_line)[0]) for l in self.moving_polygon.lines)
        return n_broken_lines % 2 == 1

    def __copy__(self):
        return self.manufacture([(l.original_x1, l.original_y1) for l in self.lines], self.x, self.y, self.rotation)


class PolygonPart(Polygon):

    def __init__(self, lines: List[Line], part_id=None):
        super().__init__(lines, part_id=part_id)
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
        points = list(chain(*[[(l.x1, l.y1) for l in p.lines] for p in polygons]))
        hull = self.convex_hull(points)
        lines = self.coords_to_lines(hull)
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
            print(len(self), len(other), self.intersects(other))
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
