from math import *

from .base_model import BaseModel


class AsteroidModel(BaseModel):

    destructable = False

    @property
    def mass(self):
        return 100000000

    def intersected_polygons(self, other: "BaseModel"):
        own_intersections, other_intersections = self.bounding_box.intersected_polygons(other.bounding_box)
        delta_movement = self.movement - other.movement
        r = delta_movement.direction.yaw_radian

        def order_by_direction(part):
            x, y = part.centroid()
            return x * sin(r) + y * cos(r)
        if self.destructable:
            own_intersections = sorted(own_intersections, key=order_by_direction)
        if other.destructable:
            other_intersections = sorted(other_intersections, key=order_by_direction)
            other_intersections.reverse()
        return own_intersections, other_intersections
