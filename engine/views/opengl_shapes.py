from math import cos, sin, radians
from itertools import chain


class OpenGLFactory(object):

    def __init__(self):
        self._polyhedron = self._render_polyhedron()

    @property
    def polyhedron(self):
        return self._polyhedron.copy()

    @staticmethod
    def _render_polyhedron():
        shape = []
        top = [0, -1, 0, 0, -1, 0]
        upper_circle = list(chain(*[(sin(radians(d)), -0.6, cos(radians(d)),
                                     sin(radians(d)), -0.6, cos(radians(d))) for d in range(0, 360, int(360 / 5))]))
        lower_circle = list(chain(*[(sin(radians(d)), 0.6, cos(radians(d)),
                                     sin(radians(d)), 0.6, cos(radians(d))) for d in range(36, 396, int(360 / 5))]))
        bottom = [0, 1, 0, 0, 1, 0]
        for i in range(5):
            i1 = i * 6
            i2 = i1 + 6
            i3 = ((i + 1) % 5) * 6
            i4 = i3 + 6
            up1 = upper_circle[i1:i2]
            up2 = upper_circle[i3:i4]
            lp1 = lower_circle[i1:i2]
            lp2 = lower_circle[i3:i4]

            shape += top
            shape += up1
            shape += up2

            shape += up1
            shape += lp1
            shape += up2

            shape += lp1
            shape += lp2
            shape += up2

            shape += lp1
            shape += bottom
            shape += lp2
        return shape
