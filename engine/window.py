import ctypes
from random import random, randrange
from typing import Callable

import pyglet
from pyglet.gl import GL_DIFFUSE, GL_AMBIENT
from pyglet.gl import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHT0, GL_POSITION, GL_LIGHTING
from pyglet.gl import glMatrixMode, glLoadIdentity, glEnable, gluPerspective, glLightfv, glRotatef, glViewport
from pyglet.gl import glOrtho, glDisable, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT

from engine.views.base_view import BaseView
from engine.views.debris import Debris
from engine.views.factories import DynamicViewFactory
from engine.views.hud import Hud
from engine.views.meshfactory import factory


class Window(pyglet.window.Window):
    # noinspection PyTypeChecker
    _to_cfloat_array: Callable = ctypes.c_float * 4

    def __init__(self, input_handler=None):
        super().__init__(width=1280, height=720)
        self.view_factory = DynamicViewFactory()
        self.hud = Hud(self.view_factory)
        self.new_views = set()
        self.del_views = set()
        self._menu = None
        self._exit = False
        self.backdrop = factory.manufacture("backdrop")
        # self.spawn_sound = pyglet.media.load('plasma.mp3', streaming=False)
        self.input_handler = input_handler
        self.debris = []
        self.on_draw = self._on_draw_menu
        self._models_by_uuid = {}
        self._views_by_uuid = {}
        self._camera_following = None
        if input_handler:
            input_handler.push_handlers(self)

    @property
    def views(self):
        return self._views_by_uuid.values()

    def to_cfloat_array(self, *floats):
        return self._to_cfloat_array(*floats)

    def update_view_timers(self, dt):
        for view in self.views:
            view.update_view_timer(dt)
        for debris in self.debris:
            debris.update(dt)

    @property
    def perspective(self):
        return float(self.width) / self.height

    def spawn(self, model):
        if model.uuid in self._models_by_uuid:
            print(f"Got {model.uuid} already!")
        self._models_by_uuid[model.uuid] = model
        view = self.view_factory.manufacture(model)
        self.hud.add_model(model)
        #  self.spawn_sound.play()
        self.new_views.add(view)
        if not self._camera_following:
            self.set_camera_on(model.uuid)

    def set_camera_on(self, uuid):
        self._camera_following = uuid
        self.debris.clear()
        for i in range(100):
            self.debris.append(Debris(randrange(-40, 40), randrange(-4, 4), randrange(-40, 40),
                                      random(), self.camera_model.movement))

    @property
    def camera_model(self):
        return self._models_by_uuid[self._camera_following]

    @property
    def camera_view(self):
        return self._views_by_uuid[self._camera_following]

    def del_view(self, view: BaseView):
        self.del_views.add(view)

    def on_resize(self, width, height):
        super(Window, self).on_resize(width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        gluPerspective(60., self.perspective, 1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        return True

    def set_menu(self, menu):
        if self._menu is not None:
            self.remove_handlers(self._menu)
            if self.input_handler:
                self.input_handler.remove_handlers(self._menu)
        self._menu = menu
        self.push_handlers(self._menu)
        self.on_draw = self._on_draw_menu

    def close_menu(self):
        self.remove_handlers(self._menu)
        if self.input_handler:
            self.input_handler.remove_handlers(self._menu)
        self._menu = None
        self.on_draw = self._on_draw_game

    def _on_draw_menu(self):
        glViewport(0, 0, self.width * 2, self.height * 2)
        self.set_up_perspective()
        self.backdrop.draw()
        self.draw_menu()

    def _on_draw_game(self):

        self.integrate_new_views()
        self.set_up_perspective()
        self.camera_view.align_camera()
        self.backdrop.draw()
        self.draw_debris()
        self.camera_view.center_camera()
        self.draw_space()
        self.remove_views()
        self.draw_hud()

    def set_up_perspective(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., self.perspective, 1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glRotatef(90, 1, 0, 0)

    def draw_debris(self):
        if len(self.debris) == 0:
            return
        lines = []
        colors = []
        for debris in self.debris:
            lines += debris.v3f
            colors += debris.c4f
        pyglet.graphics.draw(len(self.debris) * 2, pyglet.gl.GL_LINES, ('v3f', lines), ('c4f', colors))

    def draw_space(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.to_cfloat_array(0.1, 0.1, 0.1, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, self.to_cfloat_array(0, 0.3, 1, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.to_cfloat_array(3.0, 3.0, 3.0, 1.0))
        views = self.views_in_range
        for view in views:
            if view.is_alive:
                view.draw()
            else:
                self.del_view(view)
        for view in views:
            if view.is_alive:
                view.draw_transparent()
        glDisable(GL_LIGHTING)

    @property
    def views_in_range(self):
        return [view for view in self.views if view.distance_to(self.camera_view) < 400.]

    def draw_menu(self):
        self._set_up_flat_ortho_projection()
        self._menu.draw()

    def draw_hud(self):
        self._set_up_flat_ortho_projection()
        self.hud.draw()

    def _set_up_flat_ortho_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def integrate_new_views(self):
        for view in self.new_views:
            self._views_by_uuid[view.model.uuid] = view
        self.new_views.clear()

    def remove_views(self):
        for view in self.del_views:
            del self._views_by_uuid[view.model.uuid]
            del self._models_by_uuid[view.model.uuid]
        if self._camera_following not in self._views_by_uuid:
            self._camera_following = self._views_by_uuid.keys().__iter__().__next__()
        self.del_views.clear()
