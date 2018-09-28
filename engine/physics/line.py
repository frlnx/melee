from math import *
from typing import List, Tuple

from engine.models.observable import Observable


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


class BaseLine(Observable):

    def __init__(self, coords: List[Tuple[float, float]]):
        Observable.__init__(self)
        (self.original_x1, self.original_y1), (self.original_x2, self.original_y2) = coords
        self.x1, self.y1, self.x2, self.y2 = self.original_x1, self.original_y1, self.original_x2, self.original_y2
        self.x = 0
        self.y = 0
        self.rotation = 0
        self.length = hypot(self.dx, self.dy)
        self.right = max(self.x1, self.x2)
        self.left = min(self.x1, self.x2)
        self.top = max(self.y1, self.y2)
        self.bottom = min(self.y1, self.y2)

    def set_points(self, start, end):
        x1, y1 = start
        x2, y2 = end
        self.original_x1, self.original_y1, self.original_x2, self.original_y2 = x1, y1, x2, y2
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.length = hypot(self.dx, self.dy)
        self.right = max(self.x1, self.x2)
        self.left = min(self.x1, self.x2)
        self.top = max(self.y1, self.y2)
        self.bottom = min(self.y1, self.y2)
        self._callback("move")

    def set_position_rotation(self, x, y, radii):
        if self.x == x and self.y == y and self.rotation == radii:
            return False
        cos_val = cos(radii)
        sin_val = sin(radii)
        self.x1 = x + self.original_x1 * cos_val - self.original_y1 * sin_val
        self.y1 = y + self.original_x1 * sin_val + self.original_y1 * cos_val
        self.x2 = x + self.original_x2 * cos_val - self.original_y2 * sin_val
        self.y2 = y + self.original_x2 * sin_val + self.original_y2 * cos_val
        self.rotation = radii
        self.x, self.y = x, y
        self.length = hypot(self.dx, self.dy)
        self.right = max(self.x1, self.x2)
        self.left = min(self.x1, self.x2)
        self.top = max(self.y1, self.y2)
        self.bottom = min(self.y1, self.y2)
        self._callback("move")
        return True

    @property
    def centroid(self):
        return self.x1 - self.dx / 2, self.y1 - self.dy / 2

    @property
    def radii(self):
        return atan2(-self.dx, self.dy)

    @property
    def degrees(self):
        return degrees(self.radii)

    @property
    def dx(self):
        return self.x1 - self.x2

    @property
    def dy(self):
        return self.y1 - self.y2

    @property
    def dxa(self):
        return self.x2 - self.x1

    @property
    def dya(self):
        return self.y2 - self.y1

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
        self._callback("move")

    def __repr__(self):
        return f"{round(self.x1, 1)},{round(self.y1, 1)} " \
               f"-({round(self.degrees, 1)}/{round(self.length, 1)})- " \
               f"{round(self.x2, 1)},{round(self.y2, 1)}"


class Line(BaseLine):

    precision = 9

    def flip(self):
        self.x1, self.y1, self.x2, self.y2 = self.x2, self.y2, self.x1, self.y1
        self.original_x1, self.original_y1, self.original_x2, self.original_y2 = \
            self.original_x2, self.original_y2, self.original_x1, self.original_y1

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

    def intersection_point(self, other):

        if not self.bounding_box_intersects(other):
            return False, float('nan'), float('nan')

        common_denominator = self._common_denominator_with(other)

        if self.parallel_to(other):
            return False, float('nan'), float('nan')

        k_x = other.dxa * (self.y1 - other.y1) - other.dya * (self.x1 - other.x1)
        k_y = self.dxa * (self.y1 - other.y1) - self.dya * (self.x1 - other.x1)

        k_x /= common_denominator
        k_y /= common_denominator

        k_x_upper, k_x_lower = round(k_x, self.precision), round(k_x - 1, self.precision)
        k_y_upper, k_y_lower = round(k_y, self.precision), round(k_y - 1, self.precision)

        if k_x_lower <= 0 <= k_x_upper and k_y_lower <= 0 <= k_y_upper:
            intersection_x = self.x1 + k_x * self.dxa
            intersection_y = self.y1 + k_x * self.dya
            return True, intersection_x, intersection_y
        return False, float('nan'), float('nan')

    def _common_denominator_with(self, other: "Line"):
        return self.dx * other.dy - other.dx * self.dy

    def parallel_to(self, other: "Line"):
        return round(self._common_denominator_with(other), self.precision) == 0

    def on_right_side(self, x, y):
        return self.sign_of_sidedness(x, y) > 0

    def on_left_side(self, x, y):
        return self.sign_of_sidedness(x, y) < 0

    def sign_of_sidedness(self, x, y):
        position = (self.x2 - self.x1) * (y - self.y1) - (self.y2 - self.y1) * (x - self.x1)
        return position

    def delta_radii_to(self, other: "Line"):
        return (self.radii - other.radii + pi) % (pi * 2) - pi

    def copy(self):
        return self.__class__([(self.x1, self.y1), (self.x2, self.y2)])
