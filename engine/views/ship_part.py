from engine.models.ship_part import ShipPartModel
from engine.views.base_view import BaseView


class ShipPartView(BaseView):

    def __init__(self, model: ShipPartModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model

    def _draw(self):
        if self._model.target_indicator:
            x, y, z = self._model.texture_offset
            self._mesh.materials['Grid'].texture.set_position_rotation([x, z, y], self._model.texture_rotation)
        self._mesh.draw()
