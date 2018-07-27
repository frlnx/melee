import pyglet

from engine.engine import Engine
from engine.input_handlers import Keyboard
from engine.models.base_model import BaseModel
from engine.views.menus import ShipBuildMenu, BaseMenu, InputMenu, ControlConfigMenu
from engine.window import Window


class ClientEngine(Engine):
    version = (1, 0, 0)

    def __init__(self, event_loop: "TwistedEventLoop", input_handler=None, window: Window = None):
        super().__init__(event_loop)
        self.my_model = self.smf.manufacture("ship", position=self.random_position())
        self.models[self.my_model.uuid] = self.my_model
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

    def exit(self):
        print("EXIT")

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
        self.spawn_self()
        self.connect_func(host, port)
        self.solve_collisions = self._client_solve_collisions

    def start_local(self):
        self.spawn_self()
        self.window.spawn(self.my_model)

        m2 = self.smf.manufacture("ship", position=self.random_position())
        self._new_model_callback(m2)
        self.spawn(m2)

        self.spawn_asteroids(10)

    def spawn_self(self):
        self.my_controller = self.controller_factory.manufacture(self.my_model, input_handler=self.input_handler)
        self._controllers[self.my_model.uuid] = self.my_controller
        self.propagate_target(self.my_model)
        self._new_model_callback(self.my_model)

    def bind_stop(self, func):
        self._stop_func = func

    def bind_connect(self, connect_func):
        self.connect_func = connect_func

    def spawn(self, model: BaseModel):
        super(ClientEngine, self).spawn(model)
        self.window.spawn(model)

    def spawn_ship(self, controller):
        super(ClientEngine, self).spawn_ship(controller)
        self.propagate_target(controller._model)

    def spawn_with_callback(self, model: BaseModel):
        super(ClientEngine, self).spawn_with_callback(model)
        self.window.spawn(model)

    def decay(self, uuid):
        model = self.models[uuid]
        self.my_controller.deregister_target(model)
        super(ClientEngine, self).decay(uuid)

    def propagate_target(self, ship: BaseModel):
        self.my_controller.register_target(ship)

    def update(self, dt):
        super(ClientEngine, self).update(dt)
        self.window.update_view_timers(dt)
