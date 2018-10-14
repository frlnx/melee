from gui.controllers.component import MenuComponentController
from gui.models.scroller import ScrollerModelMixin


class ScrollController(MenuComponentController):

    _model: ScrollerModelMixin

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.mouse.RIGHT & buttons:
            self._model.scroll_by(dx, dy)
