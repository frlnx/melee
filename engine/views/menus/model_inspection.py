from pyglet.gl import glScalef, glTranslatef, glRotatef

from engine.models.base_model import BaseModel
from engine.physics.force import MutableDegrees, MutableOffsets
from engine.views.base_view import BaseView
from engine.views.factories import DynamicViewFactory
from .base import PerspectiveMenuComponent


class ModelInspectionMenuComponent(PerspectiveMenuComponent):

    factory = DynamicViewFactory()

    def __init__(self, left, right, bottom, top, model: BaseModel):
        super().__init__(left, right, bottom, top)
        self._view: BaseView = None
        self._position = MutableOffsets(0, 0, 0)
        self._rotation = MutableDegrees(0, 0, 0)
        self.set_model(model)

    def set_model(self, model: BaseModel):
        self._view = self.factory.manufacture(model)
        self._view.replace_position(self._position)
        self._view.replace_rotation(self._rotation)

    def draw(self):
        super(ModelInspectionMenuComponent, self).draw()
        glTranslatef(0, 0, -10)
        glRotatef(90, 1, .5, .5)
        glScalef(3., 3., 3.)

        self._view.draw()
        self._view.draw_transparent()

