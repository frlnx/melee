from engine.controllers.input_interface import InputInterface
from gui.models.drag_and_drop import DragAndDropContainer


class DragAndDropController(InputInterface):

    def __init__(self, model: DragAndDropContainer):
        self._model = model

    def on_mouse_press(self, x, y, button, modifiers):
        self._model.grab_at(x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        self._model.move(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._model.drag(x, y, dx, dy)

    def on_mouse_release(self, x, y, button, modifiers):
        self._model.drop(x, y)
