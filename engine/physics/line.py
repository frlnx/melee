from typing import List, Tuple
from math import *


class Point(object):

    def __init__(self, x: float, y: float):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.origo_x = 0
        self.origo_y = 0
        self.rotation = 0

    @property
    def radii(self):
        return atan2(-self.x, self.y)

    def set_position_rotation(self, x, y, radii):
        cos_val = cos(radii)
        sin_val = sin(radii)
        self.x = x + self.original_x * cos_val - self.original_y * sin_val
        self.y = y + self.original_x * sin_val + self.original_y * cos_val
        self.rotation = radii
        self.x, self.y = x, y


class BaseLine(object):

    def __init__(self, coords: List[Tuple[float, float]]):
        (self.original_x1, self.original_y1), (self.original_x2, self.original_y2) = coords
        self.x1, self.y1, self.x2, self.y2 = self.original_x1, self.original_y1, self.original_x2, self.original_y2
        self.x = 0
        self.y = 0
        self.rotation = 0
        self.right = max(self.x1, self.x2)
        self.left = min(self.x1, self.x2)
        self.top = max(self.y1, self.y2)
        self.bottom = min(self.y1, self.y2)

    def set_position_rotation(self, x, y, radii):
        cos_val = cos(radii)
        sin_val = sin(radii)
        self.x1 = x + self.original_x1 * cos_val - self.original_y1 * sin_val
        self.y1 = y + self.original_x1 * sin_val + self.original_y1 * cos_val
        self.x2 = x + self.original_x2 * cos_val - self.original_y2 * sin_val
        self.y2 = y + self.original_x2 * sin_val + self.original_y2 * cos_val
        self.rotation = radii
        self.x, self.y = x, y
        self.right = max(self.x1, self.x2)
        self.left = min(self.x1, self.x2)
        self.top = max(self.y1, self.y2)
        self.bottom = min(self.y1, self.y2)

    @property
    def radii(self):
        return atan2(-self.dx, self.dy)

    @property
    def dx(self):
        return self.x1 - self.x2

    @property
    def dy(self):
        return self.y1 - self.y2

    def freeze(self):
        self.original_x1 = self.x1
        self.original_y1 = self.y1
        self.original_x2 = self.x2
        self.original_y2 = self.y2
        self.x, self.y = 0, 0
        self.rotation = 0

    def rotate(self, radii):
        self.set_position_rotation(self.x, self.y, radii + self.rotation)

    def translate(self, x, y):
        self.x += x
        self.x1 += x
        self.x2 += x
        self.left += x
        self.right += x
        self.y += y
        self.y1 += y
        self.y2 += y
        self.top += y
        self.bottom += y

    def __repr__(self):
        return "{} {} - {} {}".format(self.x1, self.y1, self.x2, self.y2)


class Line(BaseLine):

    def bounding_box_intersects(self, other: BaseLine):
        if self.right < other.left:
            return False
        if self.left > other.right:
            return False
        if self.top < other.bottom:
            return False
        if self.bottom > other.top:
            return False
        return True

    def intersection_point(self, other: 'Line'):
        original_other_radii = other.radii
        other.rotate(-original_other_radii)
        self.rotate(-original_other_radii)
        dx = self.x1 - other.x1
        if round(self.x1, 8) == round(self.x2, 8):
            intersects = other.x1 == self.x1
            point_x = self.x1
            point_y = (min(self.top, other.top) + max(self.bottom, other.bottom)) / 2
        else:
            k = (self.y1 - self.y2) / (self.x1 - self.x2)
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
