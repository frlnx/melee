from typing import Set, Dict

from pyglet.gl import *
from pyglet.text import Label

from engine.models import *
from engine.views.base_view import BaseView
from engine.views.factories import DynamicViewFactory
from engine.views.ship import ShipView


class ShipHudView(ShipView):

    @property
    def yaw(self):
        return 0

    @property
    def position(self):
        return 0, 0, 0

    @staticmethod
    def _draw_bbox(*args, **kwargs):
        pass

class Hud(object):

    def __init__(self, view_factory: DynamicViewFactory):
        self._view_factory = view_factory
        self._models: Set[BaseModel] = set()
        self.texts: Dict[BaseModel, Label] = dict()
        self._views: Dict[BaseModel, BaseView] = dict()

    def add_model(self, model: BaseModel):
        self._models.add(model)
        self.texts[model] = Label(f'{model.uuid.hex[:6]} {model.name}', font_name="Courier New")
        model.observe(lambda: self.remove_model(model) if not model.is_alive else None, "alive")
        if isinstance(model, ShipModel):
            self._views[model] = self._view_factory.manufacture(model, view_class=ShipHudView)

    def remove_model(self, model):
        try:
            del self.texts[model]
        except KeyError:
            pass

    def draw(self):
        for i, text in enumerate(self.texts.values()):
            glTranslatef(0, 30, 0)
            text.draw()
        glScalef(10, 10, 10)
        glRotatef(90, 1, 0, 0)
        glTranslatef(10, -10, -10)
        for i, view in enumerate(self._views.values()):
            glTranslatef(0, 10, 0)
            view.draw()
