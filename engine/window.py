import ctypes

from engine.views.base_view import BaseView
from engine.views.opengl_mesh import OpenGLWaveFrontFactory
from engine.views.factories import DynamicViewFactory
from engine.views.menus import ShipBuildMenu, BaseMenu, InputMenu, ControlConfigMenu

from pyglet.gl import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHT0, GL_POSITION, GL_LIGHTING
from pyglet.gl import GL_DIFFUSE, GLfloat, GL_AMBIENT
from pyglet.gl import glMatrixMode, glLoadIdentity, glEnable, gluPerspective, glLightfv, glRotatef
from pyglet.gl import glOrtho, glDisable, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
from pywavefront import Wavefront
import pyglet

from math import hypot
from collections import namedtuple
from random import random, randrange
from os import path, listdir

Debris  = namedtuple("Debris", ['x', 'y', 'z', 'i'])


class Window(pyglet.window.Window):
    def __init__(self, input_handler=None):
        super().__init__(width=1280, height=720)
        files = [path.join("objects", file_name) for file_name in listdir('objects') if file_name.endswith('.obj')]
        self.mesh_factory = OpenGLWaveFrontFactory(files)
        self.lightfv = ctypes.c_float * 4
        self.view_factory = DynamicViewFactory(self.mesh_factory)
        self.views = set()
        self.new_views = set()
        self.del_views = set()
        self.center = None
        self.menu = None
        self._exit = False
        self.backdrop = Wavefront("objects/backdrop.obj")
        self._menu_main_menu()
        self._stop_func = None
        # self.spawn_sound = pyglet.media.load('plasma.mp3', streaming=False)
        self.input_handler = input_handler
        self.debris = []
        for i in range(30):
            self.debris.append(Debris(randrange(-40, 40),
                                      randrange(-4, 4),
                                      randrange(-40, 40),
                                      random()))
        self._debris_counter = 0
        if input_handler:
            input_handler.push_handlers(self)

    def update_view_timers(self, dt):
        for view in self.views:
            view.update_view_timer(dt)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            if self.menu:
                self.close_menu()
            else:
                self._menu_main_menu()
        if symbol == pyglet.window.key.F1:
            print("DEBUG")

    def _menu_main_menu(self):
        self.set_menu(BaseMenu.labeled_menu_from_function_names("Main Menu",
                            [
                                self.close_menu,
                                self._menu_shipyard,
                                self._menu_controls,
                                self._menu_network,
                                self.exit
                            ], 200, 600))

    def _menu_shipyard(self):
        self.set_menu(ShipBuildMenu.manufacture_for_ship_model(self.center._model, self._menu_main_menu,
                                                               200, 600, self.mesh_factory))

    def _menu_network(self):
        self.set_menu(InputMenu.input_menu("Network", self._menu_connect, 200, 600, self._menu_main_menu, 36))

    def _menu_controls(self):
        menu = ControlConfigMenu.manufacture_for_ship_model(self.center._model, self._menu_main_menu, 200, 600,
                                                            self.mesh_factory)
        self.input_handler.push_handlers(menu)
        self.set_menu(menu)

    def exit(self):
        self.close()
        self._stop_func()

    def _menu_connect(self, host="127.0.0.1", port=8000):
        self.connect(host, port)

    def connect(self, host, port):
        print("connect not bound yet")

    def set_menu(self, menu):
        if self.menu is not None:
            self.remove_handlers(self.menu)
            if self.input_handler:
                self.input_handler.remove_handlers(self.menu)
        self.menu = menu
        self.push_handlers(self.menu)

    def close_menu(self):
        self.remove_handlers(self.menu)
        if self.input_handler:
            self.input_handler.remove_handlers(self.menu)
        self.menu = None

    @property
    def perspective(self):
        return float(self.width) / self.height

    def spawn(self, model):
        view = self.view_factory.manufacture(model)
        # self.spawn_sound.play()
        self.new_views.add(view)
        if self.center is None:
            self.center = view

    def del_view(self, view: BaseView):
        self.del_views.add(view)

    def center_camera_on(self, view: BaseView):
        self.center = view

    def on_resize(self, width, height):
        super(Window, self).on_resize(width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        gluPerspective(60., self.perspective, 1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        return True

    def on_draw(self):
        self.clear()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., self.perspective, 1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glRotatef(90, 1, 0, 0)
        self.center.align_camera()

        self.backdrop.draw()

        self.center.center_camera()

        x_offset, y_offset, z_offset = -self.center._model.movement
        lines = []
        colors = []
        self._debris_counter += self.center._model.movement.distance / 1000
        for debris in self.debris:
            i = (debris.i + self._debris_counter) % 1
            x = self.center._model.position.x + debris.x
            x1 = (x + x_offset * 2 * (i - 0.05)) - x_offset
            x2 = (x + x_offset * 2 * i) - x_offset
            y = -10 + debris.y
            z = self.center._model.position.z + debris.z
            z1 = (z + z_offset * 2 * (i - 0.05)) - z_offset
            z2 = (z + z_offset * 2 * i) - z_offset
            lines += [x1, y, z1, x2, y, z2]
            distance = hypot(x2 - self.center._model.position.x, z2 - self.center._model.position.z)
            color = 255 / (distance ** 2 + 1)
            colors += [0, 0, 0, 0, color, color, color, color]

        pyglet.graphics.draw(len(self.debris) * 2, pyglet.gl.GL_LINES, ('v3f', lines), ('c4f', colors))

        if not self.menu:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat * 4)(1, 1, 1, 1.0))
            glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat * 4)(0, 1, 1, 0))
            glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0, 1.0))
            for view in self.views:
                view.draw()
            glDisable(GL_LIGHTING)

        self.integrate_new_views()
        self.remove_views()
        if self.menu:
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(0, self.width, 0, self.height, -1., 1000.)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            self.menu.draw()

    def integrate_new_views(self):
        self.views.update(self.new_views)
        self.new_views.clear()

    def remove_views(self):
        self.views = self.views - self.del_views
        self.del_views.clear()
