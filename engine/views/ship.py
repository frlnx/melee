from itertools import chain
from math import hypot, ceil

from pyglet.graphics import draw, GL_QUADS
from pyglet.graphics import glRotatef, glTranslated

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView


class ShipView(BaseView):
    def __init__(self, model: ShipModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._model = model
        self.fuel_gage_v3f: list = None
        self.rebuild_callback()
        model.observe(self.rebuild_callback, "rebuild")

    def rebuild_callback(self):
        coords = []
        _box_coords = [(-0.1, -10., -0.1), (0.1, -10., -0.1), (0.1, -10., 0.1), (-0.1, -10., 0.1)]
        for i in range(10):
            coords += [(x + (i - 5) * 0.3, y, z) for x, y, z in _box_coords]
        self.fuel_gage_v3f = list(chain(*coords))

    def align_camera(self):
        tx, ty, tz = self._model.target.position
        x, y, z = self._model.position

        distance = hypot(tx - x, tz - z)
        distance = min(max(distance, 50), 200)

        glTranslated(0, -distance, distance / 3)
        glRotatef(-45, 1, 0, 0)
        super().align_camera()

    def _draw_local(self):
        self._draw_fuel_gauge()

    def _draw_fuel_gauge(self):
        n_filled_boxes = int(ceil(self._model.fuel_percentage * 10))
        n_unfilled_boxes = 10 - n_filled_boxes
        green_color_box = [0., 1., .3, 1.] * 4
        red_color_box = [1., .3, .3, 1.] * 4
        n_boxes_to_draw = 10
        n_points_to_use = n_boxes_to_draw * 4
        n_coords = n_points_to_use * 3
        draw(n_points_to_use, GL_QUADS, ('v3f', self.fuel_gage_v3f[:n_coords]),
             ('c4f', green_color_box * n_filled_boxes + red_color_box * n_unfilled_boxes))

    def _draw_global(self):
        self._draw_bbox(self._model.bounding_box)
        for bbox in self._model.bounding_box._polygons:
            self._draw_bbox(bbox, color=(255, 55, 25, 255))
        for q in self._model.bounding_box.quadrants:
            self._draw_quadrant(*q)

    def center_camera(self):
        glTranslated(*-self.position)
