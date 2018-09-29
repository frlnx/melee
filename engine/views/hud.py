from engine.models import ShipModel
from engine.views.menus.model_inspection import ModelInspectionMenuComponent



class Hud(ModelInspectionMenuComponent):

    def __init__(self, left, right, bottom, top, model: ShipModel):
        super().__init__(left, right, bottom, top, model.target)
        model.observe(self._set_model, "target")

    def _set_model(self, target):
        self.set_model(model=target)
