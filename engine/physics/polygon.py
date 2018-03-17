from typing import List
from math import radians
from itertools import product
import shapely.geometry
import shapely.affinity

from engine.physics.line import Line


class BasePolygon(object):

    def __init__(self, lines: List[Line], shape: shapely.geometry.Polygon):
        self._lines = lines
        self._shape = shape
        self.rotation = 0
        self.x = 0
        self.y = 0

    @staticmethod
    def manufacture(coords, x=0, y=0, rotation=0):
        last_coord = coords[0]
        lines = [Line([coords[-1], coords[0]])]
        for coord in coords[1:]:
            lines.append(Line([last_coord, coord]))
            last_coord = coord
        if len(coords) < 3:
            shape = shapely.geometry.Point(coords[0]).buffer(0.1)
        else:
            shape = shapely.geometry.Polygon(coords)
        assert shape.is_valid
        polygon = Polygon(lines, shape)
        polygon.set_position_rotation(x, y, rotation)
        polygon.freeze()
        return polygon

    @property
    def lines(self) -> List[Line]:
        return self._lines

    def set_position_rotation(self, x, y, yaw_degrees):
        for line in self.lines:
            line.set_position_rotation(x, y, radians(yaw_degrees))
        self._shape = shapely.affinity.translate(self._shape, x - self.x, 0, y - self.y)
        self._shape = shapely.affinity.rotate(self._shape, -yaw_degrees - self.rotation)

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

    def intersection_point(self, other: BasePolygon):
        inter = self._shape.intersection(other._shape)
        if inter is None:
            return False, None, None
        if isinstance(inter, shapely.geometry.GeometryCollection):
            if len(inter) == 0:
                return False, None, None
        return True, inter.centroid.x, inter.centroid.y


    def __iadd__(self, other):
        self._lines += [Line([(line.x1, line.y1), (line.x2, line.y2)]) for line in other.lines]
        self._shape = self._shape.union(other._shape)
        return self
