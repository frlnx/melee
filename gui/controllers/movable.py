from gui.models.movable import MovableMixin
from .component import MenuComponentController


class DragControllerMixin(MenuComponentController):

    _model: MovableMixin

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super(DragControllerMixin, self).on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        if self._model.in_area(x - dx, y - dy) and self.mouse.LEFT & buttons:
            self._model.move(dx, dy)
