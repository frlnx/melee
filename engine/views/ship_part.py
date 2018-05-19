from itertools import chain
from math import radians, cos, sin

from pyglet.gl import GL_LINES, glRotatef, glPopMatrix, glPushMatrix, glScalef
from pyglet.graphics import draw
from pyglet.text import Label

from engine.models.ship_part import ShipPartModel
from engine.views.base_view import BaseView


class ShipPartView(BaseView):

    def __init__(self, model: ShipPartModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model
        self._model.observe_material(self.update_material)

    def update_material(self):
        if self._model.material_affected:
            self.set_effect_value(self._model.material_value)

    def set_effect_value(self, effect_value):
        if self._model.material_affected:
            self._mesh.update_material(self._model.material_affected, self._model.material_mode,
                                       self._model.material_channel, effect_value)


class PartDrydockView(ShipPartView):

    def __init__(self, model: ShipPartModel, mesh=None):
        super().__init__(model, mesh)
        self._base_diffuse = (13., 13., 13., 1.)
        self._diffuse = self.to_cfloat_array(13., 13., 13., 1.)
        self._light_direction = self.to_cfloat_array(0, 10, 0, 1)


class ShipPartConfigurationView(PartDrydockView):

    def __init__(self, model: ShipPartModel, mesh=None):
        self._mode = "keyboard"
        self.font_size = 60
        half_font_size = int(self.font_size / 2)
        self.infobox = Label("", font_name='Courier New', font_size=self.font_size, y=-half_font_size)
        super().__init__(model, mesh=mesh)
        self.update()

    def set_mode(self, mode):
        self._mode = mode
        self.update()

    @property
    def mode(self):
        return self._mode or "keyboard"

    def update(self):
        super(ShipPartConfigurationView, self).update()
        if self.mode == "keyboard":
            if self._model.keyboard:
                text = self._model.keyboard
            elif self._model.mouse:
                text = "M {}".format(self._model.mouse)
            else:
                text = ""
        elif self.mode == "gamepad":
            if self._model.axis:
                text = "{}".format(self._model.axis)
            elif self._model.button:
                text = "B{}".format(self._model.button)
            else:
                text = ""
        else:
            raise AttributeError("Invalid mode")
        text = str(text)
        self.infobox.text = text
        self.infobox.x = -((self.font_size * len(text)) / 2)

    def _draw_local(self):
        super(ShipPartConfigurationView, self)._draw_local()
        glPushMatrix()
        glRotatef(-self.yaw, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
        glScalef(0.025, 0.025, 0.025)
        self.infobox.draw()
        glPopMatrix()


class ShipPartDrydockView(PartDrydockView):

    def __init__(self, model: ShipPartModel, mesh=None):
        super().__init__(model, mesh)
        step = 36
        r_step = radians(step)
        ten_radians = [radians(d) for d in range(0, 360, step)]
        circle = [(cos(d), sin(d), cos(d + r_step), sin(d + r_step)) for d in ten_radians]
        circle = [x for x in chain(*circle)]
        self.circle_v2f = ('v2f', circle)
        self.circle_n_points = int(len(circle) / 2)
        self.circle_c4B = ('c4B', [150, 200, 255, 128] * self.circle_n_points)
        self.bbox_v2f = ('v2f', list(chain(*[(l.x1, l.y1, l.x2, l.y2) for l in self._model.bounding_box.lines])))
        self.bbox_n_points = len(self._model.bounding_box.lines) * 2
        self.bbox_c4f = ('c4f', [1., 1., 1., 1.] * self.bbox_n_points)

    def _draw_local(self):
        super(PartDrydockView, self)._draw_local()
        glRotatef(90, 1, 0, 0)
        draw(self.circle_n_points, GL_LINES, self.circle_v2f, self.circle_c4B)

    def _draw_global(self):
        super(PartDrydockView, self)._draw_global()
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        draw(self.bbox_n_points, GL_LINES, self.bbox_v2f, self.bbox_c4f)

        lines = [(self._model.x, self._model.z, part.x, part.z) for part in self._model.connected_parts]
        connections_v2f = ('v2f', list(chain(*lines)))
        n_points = len(lines) * 2
        draw(n_points, GL_LINES, connections_v2f, ('c4f', [0.5, 0.7, 1.0, 1.0] * n_points))
        glPopMatrix()

    def update(self):
        super(PartDrydockView, self).update()
        self.bbox_v2f = ('v2f', list(chain(*[(l.x1, l.y1, l.x2, l.y2) for l in self._model.bounding_box.lines])))

    def set_effect_value(self, effect_value):
        super(ShipPartDrydockView, self).set_effect_value(effect_value)
        self.set_diffuse_multipliers(1., effect_value, effect_value, 1.)
        inverse_effect_value = 1 - effect_value
        self.set_ambience_multipliers(.1 + inverse_effect_value, .1, .1, 1.0)


class NewPartDrydockView(PartDrydockView):
    pass
