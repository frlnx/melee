from engine.models.ship_part import ShipPartModel
from engine.views.base_view import BaseView

from pywavefront import Wavefront


FILE_TEMPLATE = "objects/{}.obj"


class ShipPartView(BaseView):

    def __init__(self, model: ShipPartModel, mesh=None):
        super().__init__(model, mesh=mesh)
        # self._mesh = Wavefront(FILE_TEMPLATE.format(model.name))

    def _draw(self):
        self._mesh.draw()
