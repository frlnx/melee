import ctypes
import pickle
from random import random, randrange
from typing import Callable

import pyglet
from pyglet.gl import GL_DIFFUSE, GL_AMBIENT
from pyglet.gl import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHT0, GL_POSITION, GL_LIGHTING
from pyglet.gl import glMatrixMode, glLoadIdentity, glEnable, gluPerspective, glLightfv, glRotatef
from pyglet.gl import glOrtho, glDisable, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT

from engine.views.base_view import BaseView
from engine.views.debris import Debris
from engine.views.factories import DynamicViewFactory
from engine.views.hud import Hud


class Window(pyglet.window.Window):
    _to_cfloat_array: Callable = ctypes.c_float * 4

    def __init__(self, input_handler=None):
        super().__init__(width=1280, height=720)
        with open('meshfactory.pkl', 'rb') as f:
            self.mesh_factory = pickle.load(f)
        self.hud = Hud()
        self.view_factory = DynamicViewFactory(self.mesh_factory)
        self.views = set()
        self.new_views = set()
        self.del_views = set()
        self.my_model = None
        self.my_view = None
        self._menu = None
        self._exit = False
        self.backdrop = self.mesh_factory.manufacture("backdrop")
        # self.spawn_sound = pyglet.media.load('plasma.mp3', streaming=False)
        self.input_handler = input_handler
        self.debris = []
        self.on_draw = self._on_draw_menu

        if input_handler:
            input_handler.push_handlers(self)

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
        view = self.view_factory.manufacture(model)
        self.hud.add_model(model)
        #  self.spawn_sound.play()
        self.new_views.add(view)
        if self.my_model is None:
            self.my_model = model
            self.my_view = view
            for i in range(100):
                self.debris.append(Debris(randrange(-40, 40), randrange(-4, 4), randrange(-40, 40),
                                          random(), model.movement))

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

    def on_draw(self):
        pass

    def _on_draw_menu(self):
        self.set_up_perspective()
        self.backdrop.draw()
        self.draw_menu()

    def _on_draw_game(self):
        self.set_up_perspective()
        self.my_view.align_camera()
        self.backdrop.draw()
        self.draw_debris()
        self.my_view.center_camera()
        self.draw_space()
        self.integrate_new_views()
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
        for view in self.views:
            if view.is_alive:
                view.draw()
            else:
                self.del_view(view)
        for view in self.views:
            if view.is_alive:
                view.draw_transparent()
        glDisable(GL_LIGHTING)

    def draw_menu(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self._menu.draw()

    def draw_hud(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.hud.draw()

    def integrate_new_views(self):
        self.views.update(self.new_views)
        self.new_views.clear()

    def remove_views(self):
        self.views = self.views - self.del_views
        self.del_views.clear()
