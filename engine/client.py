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
        self.models[self.my_model.uuid] = self.my_model

    def on_enter(self):
        super(ClientEngine, self).on_enter()
        self.window.spawn(self.my_model)

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
