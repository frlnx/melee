from math import radians, cos, sin
from itertools import chain



from pyglet.graphics import draw
from pyglet.gl import GL_LINES, GL_LIGHT0, GL_POSITION, \
    glLightfv

from engine.models.ship_part import ShipPartModel
from engine.views.base_view import BaseView


class ShipPartView(BaseView):

    def __init__(self, model: ShipPartModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model
        self._model.observe_material(self.update_material)

    def update_material(self):
        if self._model.material_affected:
            self._mesh.update_material(self._model.material_affected, self._model.material_mode,
                                       self._model.material_channel, self._model.material_value)


class ShipPartDrydockView(ShipPartView):

    def __init__(self, model: ShipPartModel, mesh=None):
        super().__init__(model, mesh)
        self._light_color = self.to_cfloat_array(13., 13., 13., 1.)
        self._light_direction = self.to_cfloat_array(0, 1, -1, 0)
        step = 36
        r_step = radians(step)
        ten_radians = [radians(d) for d in range(0, 360, step)]
        circle = [(cos(d), sin(d), cos(d + r_step), sin(d + r_step)) for d in ten_radians]
        self.circle = [x for x in chain(*circle)]
        self.v2f = ('v2f', self.circle)
        self.n_points = int(len(self.circle) / 2)
        self.c4B = ('c4B', [150, 200, 255, 128] * self.n_points)
        self.c4B_highlight = ('c4B', [0, 0, 255, 255] * self.n_points)

    def _draw_local(self):
        draw(self.n_points, GL_LINES, self.v2f, self.c4B)

    def _light_on(self):
        super(ShipPartDrydockView, self)._light_on()
        glLightfv(GL_LIGHT0, GL_POSITION, self._light_direction)
