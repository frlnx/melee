from engine.models.base_model import BaseModel
from engine.input_handlers import GamePad, Keyboard
from engine.window import Window
from engine.engine import Engine


class ClientEngine(Engine):

    version = (1, 0, 0)

    def __init__(self, input_handler=None, window=None):
        super().__init__()

        self.my_model = self.smf.manufacture("wolf", position=self.random_position())
        self.models[self.my_model.uuid] = self.my_model

        if window is None:
            self.window = Window()
        else:
            self.window = window
        self.window.spawn(self.my_model)
        self.window.connect = self.connect
        if input_handler is not None:
            self.gamepad = input_handler
        else:
            self.gamepad = Keyboard(self.window)

        self.window.push_handlers(self)
        self.window._stop_func = self.stop
        self.window._start_local_func = self.start_local
        self._stop_func = None
        self.connect_func = lambda x: None

    def start_local(self):
        self.spawn_self()

        m2 = self.smf.manufacture("wolf", position=self.random_position())
        self._new_model_callback(m2)
        self.spawn(m2)

        self.spawn_asteroids(10)

    def spawn_self(self):
        self.my_controller = self.controller_factory.manufacture(self.my_model, input_handler=self.gamepad)
        self._controllers[self.my_model.uuid] = self.my_controller
        self.propagate_target(self.my_model)
        self._new_model_callback(self.my_model)

    def on_window_close(self):
        self.stop()

    def stop(self):
        self._stop_func()

    def bind_stop(self, func):
        self._stop_func = func

    def bind_connect(self, connect_func):
        self.connect_func = connect_func

    def connect(self, *args, **kwargs):
        self.spawn_self()
        self.connect_func(*args, **kwargs)
        self.solve_collisions = self._client_solve_collisions

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

    def _client_solve_collisions(self):
        for other_model in self.models.values():
            if other_model == self.my_model:
                continue
            self.my_controller.solve_collision(other_model)
