from engine.models.base_model import BaseModel
from engine.models.ship import ShipModel
from engine.models.factories import ShipModelFactory
from engine.controllers.factories import ControllerFactory
from engine.pigtwisted import TwistedEventLoop
from engine.input_handlers import InputHandler

import random
from typing import Callable


class Engine(TwistedEventLoop):

    version = (1, 0, 0)

    def __init__(self):
        super().__init__()
        self.local_controllers = set()
        self.remote_controllers = set()
        self.ships = set()
        self.smf = ShipModelFactory()
        self.controller_factory = ControllerFactory()
        self.has_exit = True
        self.clock.schedule(self.update)
        self.clock.set_fps_limit(60)
        self._new_model_callbacks = set()
        self.rnd = random.seed()
        self.gamepad = InputHandler()
        self.models = {}

    def update_model(self, frames):
        for frame in frames:
            self.models[frame['uuid']].set_data(frame)

    @property
    def controllers(self):
        return self.local_controllers | self.remote_controllers

    def observe_new_models(self, func: Callable):
        self._new_model_callbacks.add(func)

    def _new_model_callback(self, model):
        for _new_model_observer in self._new_model_callbacks:
            _new_model_observer(model)

    def unobserve_new_models(self, func: Callable):
        try:
            self._new_model_callbacks.remove(func)
        except KeyError:
            pass

    def on_enter(self):
        model = self.smf.manufacture("wolf", position=self.random_position())
        self._new_model_callback(model)
        self.models[model.uuid] = model
        ship = self.controller_factory.manufacture(model, input_handler=self.gamepad)
        self.propagate_target(ship)
        self.local_controllers.add(ship)
        self.ships.add(ship)

    @staticmethod
    def random_position():
        x = random.randint(-10, 10)
        y = 0
        z = random.randint(-10, 10)
        return x, y, z

    def spawn_with_callback(self, model: BaseModel):
        self._new_model_callback(model)
        self.models[model.uuid] = model
        controller = self.controller_factory.manufacture(model, input_handler=self.gamepad)
        self.local_controllers.add(controller)
        if isinstance(model, ShipModel):
            self.spawn_ship(controller)

    def spawn(self, model: BaseModel):
        controller = self.controller_factory.manufacture(model)
        self.models[model.uuid] = model
        self.remote_controllers.add(controller)
        if isinstance(model, ShipModel):
            self.spawn_ship(controller)

    def spawn_ship(self, controller):
        self.propagate_target(controller)
        self.ships.add(controller)

    def decay(self, controller):
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
