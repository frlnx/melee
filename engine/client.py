from engine.models.base_model import BaseModel
from engine.input_handlers import GamePad, Keyboard
from engine.window import Window
from engine.engine import Engine


class ClientEngine(Engine):

    version = (1, 0, 0)

    def __init__(self, input_handler=None, window=None):
        super().__init__()
        if window is None:
            self.window = Window()
        else:
            self.window = window
        self.window.spawn(self.my_model)
        if input_handler is not None:
            self.gamepad = input_handler
        else:
            self.gamepad = Keyboard(self.window)
        self.window.push_handlers(self)
        self.window._stop_func = self.stop
        self._stop_func = None
        self.clock.schedule_interval(self.window.update_view_timers, 0.033)

    def on_window_close(self):
        self.stop()

    def stop(self):
        self._stop_func()

    def bind_stop(self, func):
        self._stop_func = func

    def bind_connect(self, connect_func):
        self.window.connect = connect_func

    def spawn(self, model: BaseModel):
        super(ClientEngine, self).spawn(model)
        self.window.spawn(model)

    def spawn_with_callback(self, model: BaseModel):
        super(ClientEngine, self).spawn_with_callback(model)
        self.window.spawn(model)

    def decay(self, controller):
        self.window.del_view(controller.view)
        self.controllers.remove(controller)
        # TODO: Deregister target
