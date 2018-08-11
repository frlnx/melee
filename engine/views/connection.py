from .base_view import BaseView
from engine.models.part_connection import PartConnectionModel
from pyglet.gl import glRotatef


class ConnectionView(BaseView):

    model: PartConnectionModel

    def __init__(self, model: PartConnectionModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._draw = self._draw_stuff

    def _draw_stuff(self):
        #glRotatef(90, 1, 0, 0)
        self._draw_bbox(self.model._ship_parts[0].bounding_box, color=(255, 255, 0, 255))
        self._draw_bbox(self.model.bounding_box)
