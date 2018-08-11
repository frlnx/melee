from engine.models.part_connection import PartConnectionModel
from .base_view import BaseView
from pyglet.gl import GL_LINES, glRotatef, glPopMatrix, glPushMatrix, glScalef
from pyglet.graphics import draw
from itertools import chain


class ConnectionView(BaseView):

    model: PartConnectionModel

    def __init__(self, model: PartConnectionModel, mesh=None):
        super().__init__(model, mesh=mesh)

    def _draw_local(self):
        super(ConnectionView, self)._draw_local()
        self._draw_bbox(self.model.bounding_box, color=(40, 70, 200, 255))
