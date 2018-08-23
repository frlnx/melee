from itertools import chain
from math import hypot, ceil

from pyglet.graphics import draw, GL_QUADS
from pyglet.graphics import glRotatef, glTranslated

from engine.models.ship import ShipModel
from engine.views.base_view import BaseView


class ShipView(BaseView):
    def __init__(self, model: ShipModel, mesh=None):
        super().__init__(model, mesh=mesh)
        self._draw = self._draw_sub_views
        self._draw_transparent = self._draw_transparent_sub_views
        self._sub_views = set()
        self._sub_view_indexed = {}
        self._model: ShipModel = model
        self.fuel_gage_v3f: list = None
        self.rebuild_callback()
        model.observe(self.rebuild_callback, "rebuild")

    def get_sub_view(self, uuid):
        return self._sub_view_indexed[uuid]

    def has_sub_view_for(self, uuid):
        return uuid in self._sub_view_indexed

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
        super(ShipView, self)._draw_local()

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
        pass

    def center_camera(self):
        glTranslated(*-self.position)

    def add_sub_view(self, sub_view):
        self._sub_views.add(sub_view)
        sub_view.model.observe_with_self(self.remove_sub_view_for_model, "alive")
        self._sub_view_indexed[sub_view.model.uuid] = sub_view

    def remove_sub_view(self, sub_view):
        try:
            self._sub_views.remove(sub_view)
        except KeyError:
            pass

    def remove_sub_view_for_model(self, removed: "ShipPartModel"):
        sub_view = self._sub_view_indexed[removed.uuid]
        self.remove_sub_view(sub_view)

    def _draw_sub_views(self):
        for subview in self._sub_views:
            subview.draw()

    def _draw_transparent_sub_views(self):
        for subview in self._sub_views:
            subview.draw_transparent()

    def clear_sub_views(self):
        self._sub_views.clear()

    def update_view_timer(self, dt):
        super(ShipView, self).update_view_timer(dt)
        for sub_view in self._sub_views:
            sub_view.update_view_timer(dt)
