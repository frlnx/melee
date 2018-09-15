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
        self.own_model: ShipModel = None
        self.target_model: ShipModel = None
        self.target_view: ShipHudView = None
        self._default_text = Label("Unknown", font_name="Courier New")

    def set_target_model(self, model: BaseModel):
        self.target_model = model
        self.target_view = self._views[model]

    def add_model(self, model: BaseModel):
        self._models.add(model)
        self.texts[model] = Label(f'{model.uuid.hex[:6]} {model.name}', font_name="Courier New")
        model.observe(lambda: self.remove_model(model) if not model.is_alive else None, "alive")
        if isinstance(model, ShipModel):
            self._views[model] = self._view_factory.manufacture(model, view_class=ShipHudView)
            if not self.own_model:
                self.own_model = model
                self.own_model.observe(lambda: self.set_target_model(self.own_model.target), "target")
            if not self.target_model:
                self.set_target_model(model)

    def remove_model(self, model):
        try:
            del self.texts[model]
        except KeyError:
            pass

    def draw(self):
        glPushMatrix()
        label = self.texts.get(self.target_model, self._default_text)
        glTranslatef(1200, 400, 0)
        label.draw()
        glPopMatrix()
        glPushMatrix()
        glScalef(10, 10, 10)
        glRotatef(90, 1, 0, 0)
        glTranslatef(120, -10, -30)
        self.target_view.draw()
        glPopMatrix()

    def _draw(self):
        glPushMatrix()
        for i, text in enumerate(self.texts.values()):
            glTranslatef(0, 30, 0)
            text.draw()
        glPopMatrix()
        glPushMatrix()
        glScalef(10, 10, 10)
        glRotatef(90, 1, 0, 0)
        glTranslatef(120, -10, -30)
        for i, view in enumerate(self._views.values()):
            glTranslatef(0, 0, -10)
            view.draw()
        glPopMatrix()
