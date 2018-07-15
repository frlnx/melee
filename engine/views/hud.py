from typing import Set, List

from pyglet.gl import *
from pyglet.text import Label

from engine.models import BaseModel


class Hud(object):

    def __init__(self):
        self._models: Set[BaseModel] = set()
        self.texts: List[Label] = list()

    def add_model(self, model):
        self._models.add(model)
        self.texts.append(Label(f'{model.uuid.hex[:6]} {model.name}', font_name="Courier New"))

    def draw(self):
        for i, text in enumerate(self.texts):
            glTranslatef(0, 30, 0)
            text.draw()
