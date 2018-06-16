from engine.models.base_model import BaseModel
from engine.models.ship import ShipModel
from engine.models.factories import ShipModelFactory, AsteroidModelFactory
from engine.controllers.factories import ControllerFactory
from engine.pigtwisted import TwistedEventLoop
from engine.input_handlers import InputHandler
from engine.physics.force import MutableOffsets, MutableDegrees, Offsets, MutableForce

from collections import defaultdict
import random
from typing import Callable, ValuesView
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
        self.input_handler = InputHandler()
        self._new_model_callbacks = set()
        self._dead_model_callbacks = set()
        self._controllers = dict()
        self.ships = set()
        self.models = {}
        self._time_spent = 0

    @property
    def controllers(self) -> ValuesView["engine.controllers.BaseController"]:
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
        i = 0
        failed_attempts = 0
        while i <= n and failed_attempts <= n * 2:
            model = self.amf.manufacture(self.random_position(area=200))
            retry = False
            for other_model in self.models.values():
                if model.bounding_box.bounding_box_intersects(other_model.bounding_box):
                    retry = True
                    break
            if retry:
                failed_attempts += 1
                continue
            else:
                i += 1
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
        controller = self.controller_factory.manufacture(model, input_handler=self.input_handler)
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

    def _update(self, dt):
        goal_time = self._time_spent + dt
        while self._time_spent < goal_time:
            first_collision_time, colliding_pairs = self._find_first_collision(dt)
            self._update(first_collision_time)
            for m1, m2 in colliding_pairs:
                self._controllers[m1.uuid].solve_collision(m2)
            self._time_spent += first_collision_time
            dt -= first_collision_time
            dt = max(dt, 0.001)

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

    def _find_first_collision(self, dt):
        collision_timings = defaultdict(list)
        for m1, m2 in combinations(self.models.values(), 2):
            momentum_delta = m1.movement - m2.movement
            time = m1.bounding_box.intersection_time(m2.bounding_box, momentum_delta, dt)
            if time < dt:
                dt = time
                collision_timings[time].append((m1, m2))
        return dt, collision_timings[dt]

    def collision_timings(self, dt):
        collision_timings = defaultdict(list)
        for m1, m2 in combinations(self.models.values(), 2):
            momentum_delta = m1.movement - m2.movement
            time = m1.bounding_box.intersection_time(m2.bounding_box, momentum_delta, dt)
            if time < dt:
                collision_timings[time].append((m1, m2))
        return collision_timings

    def solve_collisions(self):
        for c1, c2 in combinations(self.controllers, 2):
            c1.solve_collision(c2._model)
            c2.solve_collision(c1._model)

    def register_collisions(self):
        for m1, m2 in combinations(self.models.values(), 2):
            assert isinstance(m1, BaseModel)
            assert isinstance(m2, BaseModel)
            intersects, x, y = m1.intersection_point(m2)
            if intersects:
                m1_vector = m1.interception_vector(m2.position, m2.movement)
                m2_vector = -m1_vector
                m1_mass_quota = m2.mass / m1.mass
                m2_mass_quota = m1.mass / m2.mass
                m1_force = MutableForce(MutableOffsets(x, 0, y), m1_vector * m1_mass_quota)
                m2_force = MutableForce(MutableOffsets(x, 0, y), m2_vector * m2_mass_quota)
                m1.add_collision()