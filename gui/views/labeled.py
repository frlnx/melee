from pyglet.text import Label

from gui.models.component import MenuComponentModel


class LabeledMixin:

    ALIGN_LEFT = 'left'
    ANCHOR_X_LEFT = 'left'
    ANCHOR_Y_BASELINE = 'baseline'
    font_size = 24
    align = ALIGN_LEFT
    anchor_x = ANCHOR_X_LEFT
    anchor_y = ANCHOR_Y_BASELINE

    _model: MenuComponentModel

    def __init__(self, model):
        label = Label("button", x=model.center_x, y=model.center_y,
                      align=self.align, anchor_x=self.anchor_x, anchor_y=self.anchor_y)
        self._texts = [label]
        model.observe(self.update_text_position, "move")

    def update_text_position(self):
        for text in self._texts:
            text.x = self._model.center_x
            text.y = self._model.center_y
