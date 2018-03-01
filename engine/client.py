from engine.models.base_model import BaseModel
from engine.input_handlers import GamePad, Keyboard
from engine.window import Window
from engine.engine import Engine


class ClientEngine(Engine):

    version = (1, 0, 0)

    def __init__(self, gamepad_id=0):
        super().__init__()
        self.window = Window()
        try:
            self.gamepad = GamePad(gamepad_id)
        except:
            self.gamepad = Keyboard(self.window)
        self.my_model = self.smf.manufacture("wolf", position=self.random_position())

    def on_enter(self):
        model = self.my_model
        self.models[model.uuid] = model
        self._new_model_callback(model)
        ship = self.controller_factory.manufacture(model, input_handler=self.gamepad)
        self.propagate_target(ship)
        self.window.spawn(ship._model)
        self.local_controllers.add(ship)
        self.ships.add(ship)

    def spawn(self, model: BaseModel):
        super(ClientEngine, self).spawn(model)
        self.window.spawn(model)

    def spawn_with_callback(self, model: BaseModel):
        super(ClientEngine, self).spawn_with_callback(model)
        self.window.spawn(model)

    def decay(self, controller):
        self.window.del_view(controller.view)
        self.remote_controllers.remove(controller)
        self.local_controllers.remove(controller)
        # TODO: Deregister target
