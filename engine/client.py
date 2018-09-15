from typing import Callable

import pyglet

from engine.controllers.factories import ControllerFactory
from engine.engine import Engine
from engine.input_handlers import Keyboard
from engine.models import BaseModel
from engine.views.menus import ShipBuildMenu, BaseMenu, InputMenu, ControlConfigMenu
from engine.window import Window


class ClientEngine(Engine):
    version = (1, 0, 0)

    def __init__(self, event_loop: "TwistedEventLoop", input_handler=None, window: Window = None):
        super().__init__(event_loop)
        self.my_model = self.smf.manufacture("ship", position=self.random_position())
        self.models[self.my_model.uuid] = self.my_model
        self.controller_factory = ControllerFactory()
        self.my_controller = None

        if window is None:
            self.window: Window = Window(input_handler=input_handler)
        else:
            self.window: Window = window
        self.window.connect = self.connect
        if input_handler is not None:
            self.input_handler = input_handler
        else:
            self.input_handler = Keyboard(self.window)

        self.window.push_handlers(self)
        self._stop_func = lambda: print("nothing bound to stop")
        self.connect_func = lambda x, y: print("nothing bound to connect")

        self._menu_left = 200
        self._menu_bottom = 600
        self._main_menu_functions = [self._menu_start_local, self._menu_shipyard, self._menu_controls,
                                     self._menu_network, self.exit]
        self.callsign = None
        self._menu_login()
        self._event_loop.clock.set_fps_limit(self.fps)

    def schedule(self, func: Callable):
        self._event_loop.clock.schedule(func)

    def schedule_interval(self, func, interval):
        self._event_loop.clock.schedule_interval(func, interval)

    def exit(self):
        self._event_loop.exit()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            if self.window._menu and self.callsign:
                self.window.close_menu()
            else:
                if self.callsign:
                    self._menu_main_menu()
                else:
                    self._menu_login()

    def _menu_login(self):
        login_menu = InputMenu.input_menu("Log in", self._menu_start, self._menu_left, self._menu_bottom,
                                          self._menu_exit, 36)
        self.window.set_menu(login_menu)

    def _menu_start(self, callsign: ''):
        self.callsign = callsign
        self.my_model.set_ship_id(callsign)
        self._menu_main_menu()

    def _menu_main_menu(self):
        self.window.set_menu(BaseMenu.labeled_menu_from_function_names("Main Menu", self._main_menu_functions,
                                                                       self._menu_left, self._menu_bottom))

    def _menu_start_local(self):
        self.start_local()
        self._main_menu_functions = [self.window.close_menu, self._menu_shipyard, self._menu_controls,
                                     self._menu_network, self._menu_exit]
        self.window.close_menu()

    def _menu_shipyard(self):
        self.window.set_menu(ShipBuildMenu.manufacture_for_ship_model(self.my_model, self._menu_main_menu,
                                                                      0, self._menu_bottom,
                                                                      self.window.view_factory))

    def _menu_network(self):
        self.window.set_menu(InputMenu.input_menu("Network", self._menu_connect, self._menu_left, self._menu_bottom,
                                                  self._menu_main_menu, 36))

    def _menu_controls(self):
        menu = ControlConfigMenu.manufacture_for_ship_model(self.my_model, self._menu_main_menu,
                                                            0, self._menu_bottom,
                                                            self.window.view_factory)
        if self.input_handler:
            self.input_handler.push_handlers(menu)
        self.window.set_menu(menu)

    def _menu_exit(self):
        self.window.close()
        self._stop_func()

    def _menu_connect(self, host="127.0.0.1", port=8000):
        self.connect(host, port)

    def connect(self, host, port):
        self.connect_func(host, port)

    def start_network(self):
        self._main_menu_functions = [self.window.close_menu, self._menu_shipyard, self._menu_controls,
                                     self._menu_network, self._menu_exit]
        self.spawn_self()
        self.window.close_menu()

    def start_local(self):
        self.spawn_self()

        m2 = self.smf.manufacture("ship", position=self.random_position(), spin=(0, 90, 0))
        self._new_model_callback(m2)
        self.spawn(m2)

        self.spawn_asteroids(200, area=2000)
        self.schedule(self.update)

    def spawn_self(self):
        self.my_controller = self.controller_factory.manufacture(self.my_model, input_handler=self.input_handler)
        self.spawn(self.my_model)
        self.window.set_camera_on(self.my_model.uuid)

    def respawn(self):
        self.my_model.set_parts(self.smf.manufacture("ship").parts)

    def bind_stop(self, func):
        self._stop_func = func

    def bind_connect(self, connect_func):
        self.connect_func = connect_func

    def spawn(self, model: BaseModel):
        super(ClientEngine, self).spawn(model)
        self.window.spawn(model)
        if model.mass > 3:
            self.propagate_target(model)

    def decay(self, uuid):
        model = self.models[uuid]
        self.my_model.remove_target(model)
        super(ClientEngine, self).decay(uuid)

    def propagate_target(self, ship: BaseModel):
        self.my_model.add_target(ship)

    def update(self, dt):
        self.my_controller.update(dt)
        super(ClientEngine, self).update(dt)
        self.window.update_view_timers(dt)
