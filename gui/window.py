from pyglet.window import Window as PygletWindow

from .controllers import ComponentContainerController
from .models.container import ComponentContainerModel
from .views import OrthoViewport


class Window(PygletWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = ComponentContainerModel([], 0, self.width, 0, self.height)
        self._controller = ComponentContainerController(self._model)
        self.push_handlers(self._controller)
        self._view = OrthoViewport(self._model)

    def add_component(self, model):
        self._model.add_component(model)

    def on_draw(self):
        self.clear()
        self._view.draw()
