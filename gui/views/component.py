from typing import Set

from pyglet.text import Label

from gui.models.component import MenuComponentModel
from gui.views.drawables.drawable import Drawable


class ComponentView:

    _model: MenuComponentModel

    def __init__(self, model: MenuComponentModel):
        self._model = model

    def drawables(self) -> Set[Drawable]:
        raise NotImplementedError()

    def texts(self) -> Set[Label]:
        raise NotImplementedError()
