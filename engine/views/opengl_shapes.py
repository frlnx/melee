from itertools import chain
from math import cos, sin, radians


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

    @classmethod
    def _render_pipe(cls, axis='x', circle_start=0, circle_stop=360, circle_n_points=8, start=-1, stop=1):
        circle = cls._render_circle(axis, circle_start, circle_stop, circle_n_points, axial_coordinate=start)
        circle += cls._render_circle(axis, circle_start, circle_stop, circle_n_points, axial_coordinate=stop)
        return circle

    @staticmethod
    def _render_circle(axis='x', start=0, stop=360, n_points=8, axial_coordinate=0):
        step = int((stop - start) / n_points)
        circle = [[cos(radians(d)), sin(radians(d))] for d in range(start, stop, step)]
        coordinate_order = 'xyz'
        return list(chain(
            *[(axial_coordinate if axis == co else coords.pop() for co in coordinate_order) for coords in circle]))


shape_factory = OpenGLFactory()
