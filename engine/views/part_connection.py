from engine.models.part_connection import PartConnectionModel, ShieldConnectionModel
from .base_view import BaseView


class PartConnectionView(BaseView):

    model: PartConnectionModel
    bbox_color = (255, 255, 255, 255)

    def __init__(self, model: PartConnectionModel, mesh=None):
        super().__init__(model, mesh=mesh)

    def draw(self):
        super(PartConnectionView, self).draw()

    def draw_transparent(self):
        super(PartConnectionView, self).draw_transparent()


class ShieldConnectionView(PartConnectionView):

    model: ShieldConnectionModel
    bbox_color = (192, 192, 255, 255)
