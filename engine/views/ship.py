from math import atan2, degrees
from itertools import chain

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView

from pyglet.graphics import glRotatef, glTranslated
from pyglet.graphics import draw, GL_LINES


class ShipView(BaseView):
    def __init__(self, model: ShipModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model

    def align_camera(self):
        super().align_camera()
        self.angle_camera_to_target()

    def angle_camera_to_target(self):
        tx, ty, tz = self._model.target_pos
        x, y, z = self._model.position

        pitch = sorted([-20, -degrees(atan2(z - tz, 23)) / 2, 30])[1]
        roll = sorted([-20, degrees(atan2(x - tx, 23)) / 2, 20])[1]
        glRotatef(pitch, 1, 0, 0)
        glRotatef(roll, 0, 0, 1)

    def draw(self):
        super(ShipView, self).draw()
        lines  = self._model.bounding_box.lines
        v3f = [(line.x1, -10.0, line.y1, line.x2, -10.0, line.y2) for line in lines]
        v3f = list(chain(*v3f))
        n_points = int(len(v3f) / 3)
        v3f = ('v3f', v3f)
        c4B = ('c4B', (255, 255, 255, 255) * n_points)
        draw(n_points, GL_LINES, v3f, c4B)

    def center_camera(self):
        x, y, z = self._model.position
        glTranslated(-x, -y - 23, -z)
