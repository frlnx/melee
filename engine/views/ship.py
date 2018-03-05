from math import atan2, degrees

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView

from pyglet.graphics import glRotatef, glTranslated


class ShipView(BaseView):
    def __init__(self, model: ShipModel, mesh=None):
        self._part_spacing = 0
        self._offset = [0, 0, 0]
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

    @property
    def position(self):
        return [a + b for a, b in zip(self._model.position, self._offset)]

    @property
    def pitch(self):
        return self._model.pitch

    @property
    def yaw(self):
        return self._model.yaw

    @property
    def roll(self):
        return self._model.roll

    def center_camera(self):
        x, y, z = self._model.position
        glTranslated(-x, -y - 23, -z)

    def reset_offset(self):
        self._offset = [0, 0, 0]

    def reset_part_spacing(self):
        self._part_spacing = 0

    def offset(self, x, y, z):
        self._offset = [x, y, z]

    def part_spacing(self, distance):
        self._part_spacing = distance