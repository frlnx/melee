from math import atan2, degrees

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView

from pyglet.graphics import glRotatef, glTranslated


class ShipView(BaseView):
    def __init__(self, model: ShipModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model

    def center_camera(self):
        glRotatef(-self._model.yaw, 0, 1, 0)
        tx, ty, tz = self._model.target_pos
        x, y, z = self._model.position

        pitch = sorted([-10, -degrees(atan2(z - tz, 23)) / 2, 20])[1]
        roll = sorted([-10, degrees(atan2(x - tx, 23)) / 2, 10])[1]

        glRotatef(pitch, 1, 0, 0)
        glRotatef(roll, 0, 0, 1)
        glTranslated(-x, -y - 23, -z)
