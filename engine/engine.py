from engine.models.base_model import BaseModel
from engine.models.factories import ShipModelFactory
from engine.controllers.factories import ControllerFactory
from engine.input_handlers import GamePad
from engine.pigtwisted import TwistedEventLoop
from engine.window import Window

import pyglet
from typing import Callable


class Engine(TwistedEventLoop):

    version = (1, 0, 0)

    def __init__(self):
        super().__init__()
        self.controllers = set()
        self.ships = set()
        self.smf = ShipModelFactory()
        self.controller_factory = ControllerFactory()
        self.has_exit = True
        self.window = Window()
        self.clock.schedule(self.update)
        self.clock.set_fps_limit(60)
        self._new_model_callbacks = set()
        self._model_rollback = list()
        self.gamepad = GamePad(0)

    def observe_new_models(self, func: Callable):
        self._new_model_callbacks.add(func)
        self._rollback_for_new_observer(func)

    def _rollback_for_new_observer(self, func):
        dead_models = []
        for model in self._model_rollback:
            if not model.is_alive:
                dead_models.append(model)
            else:
                func(model)
        for dead_model in dead_models:
            self._model_rollback.remove(dead_model)

    def _new_model_callback(self, model):
        for _new_model_observer in self._new_model_callbacks:
            _new_model_observer(model)
        self._model_rollback.append(model)

    def unobserve_new_models(self, func: Callable):
        try:
            self._new_model_callbacks.remove(func)
        except KeyError:
            pass

    def on_enter(self):
        model = self.smf.manufacture("wolf")
        self._new_model_callback(model)
        ship = self.controller_factory.manufacture(model, input_handler=self.gamepad)
        self.propagate_target(ship)
        self.window.spawn(ship._model)
        self.controllers.add(ship)
        self.ships.add(ship)

    def spawn_with_callback(self, model: BaseModel):
        self._new_model_callback(model)
        self.spawn(model)

    def spawn(self, model: BaseModel):
        controller = self.controller_factory.manufacture(model)
        self.window.spawn(model)
        self.controllers.add(controller)

    def decay(self, controller):
        self.window.del_view(controller.view)
        self.controllers.remove(controller)
        # TODO: Deregister target

    def propagate_target(self, ship):
        for c in self.controllers:
            c.register_target(ship._model)
            ship.register_target(c._model)

    def update(self, dt):
        spawns = []
        decays = []
        for controller in self.controllers:
            controller.update(dt)
            spawns += controller.spawns
            if not controller.is_alive:
                decays.append(controller)
        for decaying_controller in decays:
            self.decay(decaying_controller)
        for ship in self.ships:
            for controller in self.controllers:
                if ship != controller:
                    ship.solve_collision(controller._model)
        #for c1, c2 in combinations(self.controllers, 2):
        #    c1.solve_collision(c2._model)
        for model in spawns:
            self.spawn_with_callback(model)
