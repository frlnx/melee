from engine.models.ship_part import ShipPartModel
from engine.views.base_view import BaseView

from pyglet.gl import glMatrixMode, GL_TEXTURE, glPushMatrix, glTranslatef, glRotatef, glPopMatrix, GL_MODELVIEW


class ShipPartView(BaseView):

    def __init__(self, model: ShipPartModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model

    def _draw(self):
        self._mesh.draw()


class TargetIndicatorView(BaseView):

    def __init__(self, model: ShipPartModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model

    def _draw(self):
        x, y, z = self._model.texture_offset
        z = -z
        glMatrixMode(GL_TEXTURE)
        glPushMatrix()
        glTranslatef(*[-x for x in [x, z, y]])
        glRotatef(self._model.texture_rotation[1], 0, 0, 1)
        self._mesh.draw()
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
