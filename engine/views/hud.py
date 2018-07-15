from typing import Set, Dict

from pyglet.gl import *
from pyglet.text import Label

from engine.models import BaseModel


class Hud(object):

    def __init__(self):
        self._models: Set[BaseModel] = set()
        self.texts: Dict[BaseModel, Label] = dict()

    def add_model(self, model: BaseModel):
        self._models.add(model)
        self.texts[model] = Label(f'{model.uuid.hex[:6]} {model.name}', font_name="Courier New")
        model.observe(lambda: self.remove_model(model) if not model.is_alive else None, "alive")

    def remove_model(self, model):
        try:
            del self.texts[model]
        except KeyError:
            pass

    def draw(self):
        for i, text in enumerate(self.texts.values()):
            glTranslatef(0, 30, 0)
            text.draw()
