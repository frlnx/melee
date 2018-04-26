from engine.models.base_model import BaseModel
from engine.models.ship import ShipModel
from engine.models.factories import ShipModelFactory, AsteroidModelFactory
from engine.controllers.factories import ControllerFactory
from engine.pigtwisted import TwistedEventLoop
from engine.input_handlers import InputHandler

import random
from typing import Callable, Iterable
from itertools import combinations


class Engine(TwistedEventLoop):

    version = (1, 0, 0)

    def __init__(self):
        super().__init__()
        self.smf = ShipModelFactory()
        self.amf = AsteroidModelFactory()
        self.controller_factory = ControllerFactory()
        self.has_exit = True
        self.clock.schedule(self.update)
        self.clock.set_fps_limit(60)
        self.rnd = random.seed()
        self.gamepad = InputHandler()
        self._new_model_callbacks = set()
        self._dead_model_callbacks = set()
        self._controllers = dict()
        self.ships = set()
        self.models = {}

    @property
    def controllers(self) -> Iterable["engine.controllers.BaseController"]:
        return self._controllers.values()

    def controller_by_uuid(self, uuid) -> "engine.controllers.BaseController":
        return self._controllers[uuid]

    def update_model(self, frames):
        for frame in frames:
            try:
                self.models[frame['uuid']].set_data(frame)
            except KeyError:
                pass

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

    def observe_dead_models(self, func: Callable):
        self._dead_model_callbacks.add(func)

    def _dead_model_callback(self, model):
        for _dead_model_observer in self._dead_model_callbacks:
            _dead_model_observer(model)

    def unobserve_dead_models(self, func: Callable):
        try:
            self._dead_model_callbacks.remove(func)
        except KeyError:
            pass

    def stop_game(self):
        self._new_model_callbacks = set()
        self._dead_model_callbacks = set()
        self._controllers = dict()
        self.ships = set()
        self.models = {}

    def spawn_asteroids(self, n):
        for i in range(n):
            model = self.amf.manufacture(self.random_position(area=200))
            self.spawn(model)

    @staticmethod
    def random_position(area=20):
        x = random.randint(-area, area)
        y = 0
        z = random.randint(-area, area)
        return x, y, z

    def spawn_with_callback(self, model: BaseModel):
        self._new_model_callback(model)
        self.models[model.uuid] = model
        controller = self.controller_factory.manufacture(model, input_handler=self.gamepad)
        self._controllers[model.uuid] = controller
        if isinstance(model, ShipModel):
            self.spawn_ship(controller)

    def spawn(self, model: BaseModel):
        print("Spawning from network", model.uuid)
        controller = self.controller_factory.manufacture(model)
        self.models[model.uuid] = model
        self._controllers[model.uuid] = controller
        if isinstance(model, ShipModel):
            self.spawn_ship(controller)

    def spawn_ship(self, controller):
        self.ships.add(controller)

    def decay(self, uuid):
        print("Decay from network", uuid)
        model = self.models[uuid]
        model.set_alive(False)
        self.remove_controller_by_uuid(uuid)

    def remove_controller_by_uuid(self, uuid):
        try:
            del self._controllers[uuid]
        except KeyError:
            pass

    def decay_with_callback(self, controller):
        self.decay(controller._model.uuid)
        self._dead_model_callback(controller._model)
        print("Informing network of decay", controller._model.uuid)

    def update(self, dt):
        spawns = []
        decays = []
        for controller in self.controllers:
            controller.update(dt)
            spawns += controller.spawns
            if not controller.is_alive:
                decays.append(controller)
        for decaying_controller in decays:
            self.decay_with_callback(decaying_controller)
        self.solve_collisions()
        for model in spawns:
            self.spawn_with_callback(model)

    def solve_collisions(self):
        for c1, c2 in combinations(self.controllers, 2):
            c1.solve_collision(c2._model)
            c2.solve_collision(c1._model)
