from gui.models.button import ButtonModel
from .component import MenuComponentController


class ButtonController(MenuComponentController):

    def __init__(self, model: ButtonModel):
        super().__init__(model)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.in_area(x, y):
            self._model.func()

    def on_mouse_motion(self, x, y, dx, dy):
        print(x, y)
        self._model.highlight(self.in_area(x, y))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._model.highlight(self.in_area(x, y))
