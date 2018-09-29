from pyglet.gl import glScalef, glTranslatef, glRotatef, glLoadIdentity
from pyglet.text import Label

from engine.models.base_model import BaseModel
from engine.physics.force import MutableDegrees, MutableOffsets
from engine.views.base_view import BaseView
from engine.views.factories import DynamicViewFactory
from .base import PerspectiveOrthoOverlayComponent


class ModelInspectionMenuComponent(PerspectiveOrthoOverlayComponent):

    factory = DynamicViewFactory()

    def __init__(self, left, right, bottom, top, model: BaseModel):
        super().__init__(left, right, bottom, top)
        self._model = None
        self._view: BaseView = None
        self._position = MutableOffsets(0, 0, 0)
        self._rotation = MutableDegrees(0, 0, 0)
        padding = 20
        font_size = 12
        x = left + padding
        y = top - (font_size + padding)
        self._info_label = Label("N/A", font_name='Courier New', font_size=font_size, x=x, y=y, multiline=True,
                                 width=self.width - padding * 2)
        self.set_model(model)

    def set_model(self, model: BaseModel):
        if self._model == model:
            return
        self._unobserve_model_info_changes()
        self._model = model
        self._view = self.factory.manufacture(model)
        self._view.replace_position(self._position)
        self._view.replace_rotation(self._rotation)
        self._observe_model_info_changes()
        self._update_info_text()

    def _update_info_text(self):
        self._info_label.text = self._build_info_text()

    def _build_info_text(self):
        text = ""
        fields = ['name', 'full_torque', 'degrees_off_center_of_mass', 'generation_level', 'fuel_stored', 'working',
                  'max_power_output']
        for field in fields:
            try:
                data = getattr(self._model, field)
                if isinstance(data, float):
                    data = str(round(data, 2))
                elif isinstance(data, bool):
                    data = data and "Yes" or "No"
                text += f"\n{field.capitalize().replace('_', ' ')}: " + data.capitalize()
            except AttributeError:
                pass
        return text

    def _observe_model_info_changes(self):
        self._model.observe(self._update_info_text, "move")
        self._model.observe(self._update_info_text, "working")

    def _unobserve_model_info_changes(self):
        if self._model:
            self._model.unobserve(self._update_info_text, "move")
            self._model.unobserve(self._update_info_text, "working")

    def _draw_perspective(self):
        super(ModelInspectionMenuComponent, self)._draw_perspective()
        glTranslatef(0, 0, -10)
        glRotatef(90, 1, .5, .5)
        glScalef(3., 3., 3.)

        self._view.draw()
        self._view.draw_transparent()

    def _draw_ortho(self):
        glLoadIdentity()
        self._info_label.draw()


