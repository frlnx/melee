from engine.models.ship_part import ShipPartModel
from engine.views.base_view import BaseView


class ShipPartView(BaseView):

    def __init__(self, model: ShipPartModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model
        self._model.observe_material(self.update_material)

    def _draw(self):
        self._mesh.draw()

    def update_material(self):
        if self._model.material_affected:
            self._mesh.update_material(self._model.material_affected, self._model.material_mode,
                                       self._model.material_channel, self._model.material_value)
