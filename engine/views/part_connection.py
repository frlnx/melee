from engine.models.part_connection import PartConnectionModel, ShieldConnectionModel
from .base_view import BaseView


class PartConnectionView(BaseView):

    model: PartConnectionModel
    bbox_color = (255, 255, 255, 255)

    def __init__(self, model: PartConnectionModel, mesh=None):
        super().__init__(model, mesh=mesh)

    def draw(self):
        if self.is_alive:
            super(PartConnectionView, self).draw()

    def draw_transparent(self):
        if self.is_alive:
            super(PartConnectionView, self).draw_transparent()

    def _draw_local(self):
        super(PartConnectionView, self)._draw_local()
        #self._draw_bbox(self.model.bounding_box, color=self.bbox_color)


class ShieldConnectionView(PartConnectionView):

    model: ShieldConnectionModel
    bbox_color = (192, 192, 255, 255)
