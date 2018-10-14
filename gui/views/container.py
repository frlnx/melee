from typing import Set

from pyglet.graphics import Batch
from pyglet.text import Label

from gui.models.component import MenuComponentModel
from gui.models.container import ComponentContainerModel
from gui.views.drawables import Drawable
from .component import ComponentView
from .placeholder import Placeholder


class ContainerView(ComponentView):

    def __init__(self, model: ComponentContainerModel):
        self._batch = Batch()
        self._views = []
        for component in model.components:
            self.add_component(component)
        self._drawables = set()
        self._texts = set()
        model.observe(self.add_component, model.SIGNAL_ADD_COMPONENT)

    def add_component(self, component: MenuComponentModel):
        from gui import views
        if component.view_class:
            view_class = getattr(views, component.view_class)
        else:
            view_class = Placeholder
        view = view_class(component)
        self._views.append(view)
        for drawable in view.drawables():
            self.add_drawable(drawable)
        for text in view.texts():
            self.add_text(text)

    def drawables(self) -> Set[Drawable]:
        return self._drawables

    def texts(self) -> Set[Label]:
        return self._texts

    def add_drawable(self, drawable: Drawable):
        self._drawables.add(drawable)

    def add_text(self, text):
        self._texts.add(text)
