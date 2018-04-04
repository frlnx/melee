import ctypes

from engine.views.base_view import BaseView
from engine.views.opengl_mesh import OpenGLWaveFrontFactory
from engine.views.factories import DynamicViewFactory
from engine.views.menus import ShipBuildMenu, BaseMenu, InputMenu, ControlConfigMenu

from pyglet.gl import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHT0, GL_POSITION, GL_LIGHTING
from pyglet.gl import GL_DIFFUSE, GL_AMBIENT
from pyglet.gl import glMatrixMode, glLoadIdentity, glEnable, gluPerspective, glLightfv, glRotatef
from pyglet.gl import glOrtho, glDisable, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
import pyglet

from random import random, randrange
from os import path, listdir

from engine.views.debris import Debris


class Window(pyglet.window.Window):
    def __init__(self, input_handler=None):
        super().__init__(width=1280, height=720)
        files = [path.join("objects", file_name) for file_name in listdir('objects') if file_name.endswith('.obj')]
        self.mesh_factory = OpenGLWaveFrontFactory(files)
        self._to_cfloat_array = ctypes.c_float * 4
        self.view_factory = DynamicViewFactory(self.mesh_factory)
        self.views = set()
        self.new_views = set()
        self.del_views = set()
        self.my_model = None
        self.my_view = None
        self.menu = None
        self._exit = False
        self.backdrop = self.mesh_factory.manufacture("backdrop")
        self._menu_left = 200
        self._menu_bottom = 600
        self._menu_main_menu()
        self._stop_func = None
        # self.spawn_sound = pyglet.media.load('plasma.mp3', streaming=False)
        self.input_handler = input_handler
        self.debris = []
        self._debris_counter = 0

        if input_handler:
            input_handler.push_handlers(self)

    def to_cfloat_array(self, *floats):
        return self._to_cfloat_array(*floats)

    def update_view_timers(self, dt):
        for view in self.views:
            view.update_view_timer(dt)
        for debris in self.debris:
            debris.update(dt)
        #self._debris_counter += dt

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            if self.menu:
                self.close_menu()
            else:
                self._menu_main_menu()
        if symbol == pyglet.window.key.F1:
            print("DEBUG")

    def _menu_main_menu(self):
        functions = [self.close_menu, self._menu_shipyard, self._menu_controls, self._menu_network, self.exit]
        self.set_menu(BaseMenu.labeled_menu_from_function_names("Main Menu",
                                                                functions, self._menu_left, self._menu_bottom))

    def _menu_shipyard(self):
        self.set_menu(ShipBuildMenu.manufacture_for_ship_model(self.my_model, self._menu_main_menu,
                                                               self._menu_left, self._menu_bottom, self.mesh_factory))

    def _menu_network(self):
        self.set_menu(InputMenu.input_menu("Network", self._menu_connect, self._menu_left, self._menu_bottom,
                                           self._menu_main_menu, 36))

    def _menu_controls(self):
        menu = ControlConfigMenu.manufacture_for_ship_model(self.my_model, self._menu_main_menu,
                                                            self._menu_left, self._menu_bottom, self.mesh_factory)
        if self.input_handler:
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
        #  self.spawn_sound.play()
        self.new_views.add(view)
        if self.my_model is None:
            self.my_model = model
            self.my_view = view
            for i in range(30):
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

    def on_draw(self):
        self.clear()
        self.set_up_perspective()
        self.my_view.align_camera()

        self.backdrop.draw()

        if self.menu:
            self.draw_menu()
        else:
            self.draw_debris()
            self.my_view.center_camera()
            self.draw_space()
            self.integrate_new_views()
            self.remove_views()

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
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.to_cfloat_array(1, 1, 1, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, self.to_cfloat_array(0, 1, 1, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.to_cfloat_array(1.0, 1.0, 1.0, 1.0))
        for view in self.views:
            if view.is_alive:
                view.draw()
            else:
                self.del_view(view)
        glDisable(GL_LIGHTING)

    def draw_menu(self):
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
