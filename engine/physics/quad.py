from math import cos, sin, radians
from engine.physics.line import Line

class BaseBox(object):

    def __init__(self, left, right, bottom, top):
        assert top > bottom
        assert left < right
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom


class Box(BaseBox):

    def intersects(self, other: BaseBox):
        if self.right < other.left:
            return False
        if self.left > other.right:
            return False
        if self.top < other.bottom:
            return False
        if self.bottom > other.top:
            return False
        return True

    def union(self, other: BaseBox) -> BaseBox:
        pass


class BaseQuad(object):

    def __init__(self, coords: list, rotation=0, x=0, z=0):
        self._original_coords = coords
        self._coords = list(coords)
        self._rotation = 0
        self._x = 0
        self._z = 0
        self._x_es = []
        self._z_es = []
        self.set_position_rotation(x, z, rotation)

    def set_position_rotation(self, tx, tz, degrees):
        self._rotation = degrees
        self._x = tx
        self._z = tz
        r = radians(degrees)
        sin_r = sin(r)
        cos_r = cos(r)
        self._coords.clear()
        self._x_es.clear()
        self._z_es.clear()
        for original_x, original_z in self._original_coords:
            x = original_x * cos_r - original_z * sin_r + tx
            z = original_x * sin_r + original_z * cos_r + tz
            self._coords.append((x, z))
            self._z_es.append(z)
            self._x_es.append(x)
        self._min_x, _, __, self._max_x = sorted(self._x_es)
        self._min_z, _, __, self._max_z = sorted(self._z_es)

    def outer_bounds_after_rotation(self, degrees) -> Box:
        r = radians(degrees)
        sin_r = sin(r)
        cos_r = cos(r)
        x_es = []
        z_es = []
        for original_x, original_z in self._coords:
            x = original_x * cos_r - original_z * sin_r
            z = original_x * sin_r + original_z * cos_r
            z_es.append(z)
            x_es.append(x)
        min_x, _, __, max_x = sorted(x_es)
        min_z, _, __, max_z = sorted(z_es)
        return Box(min_x, max_x, min_z, max_z)

    @property
    def to_json(self):
        return {"coords": self._original_coords, "rotation": self._rotation, "x": self._x, "z": self._z}

    @property
    def outer_bounding_box(self):
        return Box(self.left, self.right, self.bottom, self.top)

    @property
    def left(self):
        return self._min_x

    @property
    def right(self):
        return self._max_x

    @property
    def top(self):
        return self._max_z

    @property
    def bottom(self):
        return self._min_z


class Quad(BaseQuad):

    def __add__(self, other: BaseQuad):
        left = min(self.left, other.left)
        right = max(self.right, other.right)
        bottom = min(self.bottom, other.bottom)
        top = max(self.top, other.top)
        coords = [(left, bottom), (right, bottom), (right, top), (left, top)]
        return Quad(coords)

    def __repr__(self):
        return ", ".join([str(x) for x in [self.left, self.right, self.bottom, self.top]])
