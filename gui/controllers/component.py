from engine.controllers.input_interface import InputInterface
from gui.models.component import MenuComponentModel


class MenuComponentController(InputInterface):

    def __init__(self, model: MenuComponentModel):
        super().__init__()
        self._model = model

    def in_area(self, x, y):
        return self._model.in_area(x, y)
