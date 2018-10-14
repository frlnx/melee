from gui.models.component import MenuComponentModel
from .component import ComponentView
from .drawables.box import Box
from .labeled import LabeledMixin


class Placeholder(ComponentView, LabeledMixin):

    def __init__(self, model: MenuComponentModel):
        self._model = model
        self._regular_color = (.7, .7, .7)
        self._border = Box(model.left, model.right, model.bottom, model.top, color=self._regular_color)
        self._drawables = [self._border]
        LabeledMixin.__init__(self, model)
        self._model.observe(self.movement_callback, "move")

    def movement_callback(self):
        self._border.update_boundaries(self._model.left, self._model.right, self._model.bottom, self._model.top)

    def drawables(self):
        return self._drawables

    def texts(self):
        return self._texts
