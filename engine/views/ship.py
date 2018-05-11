from math import atan2, degrees, hypot
from itertools import chain

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView

from pyglet.graphics import glRotatef, glTranslated
from pyglet.graphics import draw, GL_LINES


class ShipView(BaseView):
    def __init__(self, model: ShipModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model
        self.v3f = ('v3f', [-10, -10, -10, 10, -10, -10, 10, -10, 10, -10, -10, 10])

    def align_camera(self):
        self.angle_camera_to_target()
        super().align_camera()

    def angle_camera_to_target(self):
        tx, ty, tz = self._model.target_pos
        x, y, z = self._model.position

        distance = hypot(tx - x, tz - z)
        distance = min(max(distance, 50), 200)

        glTranslated(0, -distance, 0)

        pitch = sorted([-75, -degrees(atan2(z - tz, distance / 2)) / 2, 0])[1]
        yaw = sorted([-10, degrees(atan2(x - tx, distance / 2)) / 2, 10])[1]
        #roll = sorted([-50, degrees(atan2(x - tx, distance / 2)) / 2, 50])[1]
        glRotatef(-45, 1, 0, 0)
        glRotatef(yaw, 0, 1, 0)
        #glRotatef(roll, 0, 0, 1)

    def _draw_local(self):
        draw(4, GL_LINES, self.v3f, ('c4f', [1., 1., 1., 1.] * 4))

    def _draw_global(self):
        lines  = self._model.bounding_box.lines
        v3f = [(line.x1, -10.0, line.y1, line.x2, -10.0, line.y2) for line in lines]
        v3f = list(chain(*v3f))
        n_points = int(len(v3f) / 3)
        v3f = ('v3f', v3f)
        c4B = ('c4B', (255, 255, 255, 255) * n_points)
        draw(n_points, GL_LINES, v3f, c4B)

    def center_camera(self):
        glTranslated(*-self._model.position)
