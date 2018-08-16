from collections import defaultdict
from functools import reduce
from itertools import product, chain
from math import radians, atan2, degrees, floor, ceil
from typing import List, Iterator, Set
from uuid import uuid4

from engine.physics.line import Line


class BasePolygon(object):

    def __init__(self, lines: List[Line], part_id=None):
        if len(lines) == 0:
            raise AttributeError("Need at least one point")
        self.part_id = part_id or uuid4().hex
        self._lines = lines
        self.rotation = 0
        self.x = 0
        self.y = 0
        self._left = self._right = self._top = self._bottom = None
        self._moving_left = self._moving_right = self._moving_top = self._moving_bottom = None
        self._moving_points = [(l.x1, l.y1) for l in self.lines]
        self._moving_polygon = None
        self._observers = defaultdict(set)
        self._quadrants = set()

    def observe(self, func, action):
        self._observers[action].add(func)

    def unobserve(self, func, action):
        try:
            self._observers[action].remove(func)
        except KeyError:
            pass

    def callback(self, action):
        for callback in self._observers[action]:
            callback()

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

    @classmethod
    def manufacture_open(cls, coords, x=0, y=0, rotation=0):
        lines = cls.coords_to_lines(coords)
        lines.pop(0)
        polygon = cls(lines)
        polygon.set_position_rotation(x, y, rotation)
        polygon.clear_movement()
        return polygon

    @property
    def lines(self) -> List[Line]:
        return self._lines

    @property
    def moving_polygon(self) -> "Polygon":
        if self._moving_polygon:
            return self._moving_polygon
        point_string = self.convex_hull(self._moving_points)
        self._moving_polygon = Polygon.manufacture(coords=point_string)
        return self._moving_polygon

    @property
    def moving_lines(self):
        return self.moving_polygon.lines

    @classmethod
    def convex_hull(cls, points) -> List[tuple]:
        points = list(set(points))
        if len(points) <= 3:
            return points
        y_es = [p[1] for p in points]
        smallest_y = min(y_es)
        smallest_y_index = y_es.index(smallest_y)
        starting_point = points[smallest_y_index]
        point_string = []
        last_angle = 0
        min_angle_point = starting_point
        while min_angle_point not in point_string:
            point_string.append(min_angle_point)
            last_point = point_string[-1]
            eval_points = list(points)
            eval_points.remove(last_point)
            angles = cls.get_angles_for_points_from_point(last_point, eval_points)
            delta_angles = [cls.delta_angle(a, last_angle) % 360 for a in angles]
            min_angle = min(delta_angles)
            min_angle_point = eval_points[delta_angles.index(min_angle)]
            last_angle += min_angle
        hull = point_string[point_string.index(min_angle_point):]
        hull.reverse()
        return hull

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

    def set_position_rotation(self, x, y, yaw_degrees):
        self.x = x
        self.y = y
        self.rotation = yaw_degrees
        self._moving_points.clear()
        for line in self.lines:
            self._moving_points.append((line.x1, line.y1))
            if line.set_position_rotation(x, y, radians(yaw_degrees)):
                self._moving_points.append((line.x1, line.y1))
        self._left = self._right = self._top = self._bottom = None
        self._moving_left = self._moving_right = self._moving_top = self._moving_bottom = None
        self._moving_polygon = None

    def clear_movement(self):
        self._moving_points = [(l.x1, l.y1) for l in self.lines]
        self._moving_left = self._moving_right = self._moving_top = self._moving_bottom = None
        self._moving_polygon = None

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
        self._moving_left = self._moving_left or min(x for x, y in self._moving_points)
        return self._moving_left

    @property
    def moving_right(self):
        self._moving_right = self._moving_right or max(x for x, y in self._moving_points)
        return self._moving_right

    @property
    def moving_top(self):
        self._moving_top = self._moving_top or max(y for x, y in self._moving_points)
        return self._moving_top

    @property
    def moving_bottom(self):
        self._moving_bottom = self._moving_bottom or min(y for x, y in self._moving_points)
        return self._moving_bottom

    @property
    def quadrants(self) -> set:
        self._quadrants = self._quadrants or set(product(
            range(int(floor(self.moving_left / 30)), int(ceil(self.moving_right / 30))),
            range(int(floor(self.moving_bottom / 30)), int(ceil(self.moving_top / 30)))
        ))
        return self._quadrants

    def reset_quadrants(self):
        self._quadrants = set()
        self.callback("quadrants")

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

    def intersects(self, other):
        if not self.movement_box_intersects(other):
            return False
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
        if not self.movement_box_intersects(other):
            return False, None, None
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

    def intersected_polygons(self, other: "Polygon"):
        intersections = set()

        #if len(other) == 0 or not self.intersects(other) and not other.point_inside(*self.centroid()):
        #    return set(), intersections

        for p in other:
            if self.intersects(p):
                intersections.add(p)
        return set(), intersections

    def __iter__(self) -> Iterator["Polygon"]:
        return [self].__iter__()

    def __len__(self):
        return 1


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


class ConvexHull(Polygon):

    def point_inside(self, x, y):
        return all(line.on_left_side(x, y) for line in self.moving_lines)


class MultiPolygon(ConvexHull):

    def __init__(self, polygons: Set[PolygonPart]):
        points = list(chain(*[[(l.x1, l.y1) for l in p.lines] for p in polygons]))
        hull = self.convex_hull(points)
        lines = self.coords_to_lines(hull)
        super().__init__(lines)
        self._polygons = polygons
        self._part_id_index = {p.part_id: p for p in self._polygons}

    def clear_movement(self):
        super(MultiPolygon, self).clear_movement()
        for p in self:
            p.clear_movement()

    def remove_polygons(self, uuids):
        self._remove_polygons({self._part_id_index[uuid] for uuid in uuids})

    def _remove_polygons(self, polygons):
        if not polygons & self._polygons:
            return
        self._polygons -= polygons
        self.rebuild_hull()

    def rebuild_hull(self):
        x, y, rotation = self.x, self.y, self.rotation
        self.set_position_rotation(0, 0, 0)
        points = list(chain(*[[(l.x1, l.y1) for l in p.lines] for p in self._polygons]))
        hull = self.convex_hull(points)
        lines = self.coords_to_lines(hull)
        #self.freeze()
        self._lines = lines
        self.set_position_rotation(x, y, rotation)

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
        polygon = MultiPolygon({PolygonPart(lines)})
        polygon.set_position_rotation(x, y, rotation)
        polygon.clear_movement()
        return polygon

    def set_position_rotation(self, x, y, yaw_degrees):
        super(MultiPolygon, self).set_position_rotation(x, y, yaw_degrees)
        for polygon in self._polygons:
            polygon.set_position_rotation(x, y, yaw_degrees)
        self.reset_quadrants()
