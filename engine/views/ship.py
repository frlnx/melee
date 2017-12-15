from typing import Set
from math import atan2

from engine.models.ship import ShipModel
from engine.views.ship_part import ShipPartView
from engine.views.base_view import BaseView

from pyglet.graphics import glTranslatef, glRotatef, glPushMatrix, glPopMatrix, GLfloat, glGetFloatv, \
    GL_MODELVIEW_MATRIX, glMultMatrixf, glLoadIdentity, glTranslated

class ShipView(BaseView):
    def __init__(self, model: ShipModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model

    def center_camera(self):
        tx, ty, tz = self._model.target_pos
        glRotatef(-self._model.yaw, 0, 1, 0)
        x, y, z = self._model.position
        pitch = atan2(-23, tz - z)
        roll = atan2(-23, tx - x)
        glRotatef(pitch, 1, 0, 0)
        glRotatef(roll, 0, 0, 1)
        glTranslated(-x, -y - 23, -z)
