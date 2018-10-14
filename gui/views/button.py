from gui.models.button import ButtonModel
from .component import ComponentView
from .drawables.box import Box
from .labeled import LabeledMixin


class ButtonView(ComponentView, LabeledMixin):

    def __init__(self, model: ButtonModel):
        ComponentView.__init__(self, model)
        self._model = model
        self._regular_color = (.7, .7, .7)
        self._highlight_color = (1., 1., 1.)
        self._border = Box(model.left, model.right, model.bottom, model.top, color=self._regular_color)
        self._drawables = [self._border]
        LabeledMixin.__init__(self, model)
        self._model.observe(self._highlight_callback, "highlight")

    def drawables(self):
        return self._drawables

    def texts(self):
        return self._texts

    def _highlight_callback(self, state):
        if state:
            self.highlight()
        else:
            self.unhighlight()

    def highlight(self):
        self._border.set_color(self._highlight_color)

    def unhighlight(self):
        self._border.set_color(self._regular_color)
