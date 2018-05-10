from math import cos, sin, radians

from engine.models.ship_part import ShipPartModel
from engine.physics.polygon import Polygon


class ShieldArcModel(ShipPartModel):

    def __init__(self, generated_from: ShipPartModel):
        first_quad_z = generated_from.position.z - 4
        second_quad_z = generated_from.position.z + 4
        x = generated_from.position.x
        coords = []
        for degrees in range(0, 90, 10):
            radi = radians(degrees)
            coords.append((cos(radi) * 4 + x, sin(radi) * 4 + first_quad_z))
        for degrees in range(0, 90, 10):
            radi = radians(degrees)
            coords.append((sin(radi) * 4 + x, -cos(radi) * 4 + second_quad_z))
        bounding_box = Polygon.manufacture(coords, x=x, y=generated_from.position.z)
        generated_from.observe(self.update)
        super().__init__("Shield Arc", generated_from.position, generated_from.rotation,
                         generated_from.movement, generated_from.spin, bounding_box)
