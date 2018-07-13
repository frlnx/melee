import random
from itertools import combinations
from typing import Callable, ValuesView

from engine.controllers.factories import ControllerFactory
from engine.input_handlers import InputHandler
from engine.models.base_model import BaseModel
from engine.models.factories import ShipModelFactory, AsteroidModelFactory
from engine.models.ship import ShipModel
from engine.physics.force import MutableOffsets, MutableForce
from engine.pigtwisted import TwistedEventLoop


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
        controller = self.controller_factory.manufacture(model)
        self.models[model.uuid] = model
        self._controllers[model.uuid] = controller
        if isinstance(model, ShipModel):
            self.spawn_ship(controller)

    def spawn_ship(self, controller):
        self.ships.add(controller)

    def decay(self, uuid):
        model = self.models[uuid]
        model.set_alive(False)
        self.remove_controller_by_uuid(uuid)
        self.remove_model_by_uuid(uuid)

    def remove_controller_by_uuid(self, uuid):
        try:
            del self._controllers[uuid]
        except KeyError:
            pass

    def remove_model_by_uuid(self, uuid):
        try:
            del self.models[uuid]
        except KeyError:
            pass

    def decay_with_callback(self, controller):
        self.decay(controller._model.uuid)
        self._dead_model_callback(controller._model)

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
        self.register_collisions()
        for model in spawns:
            self.spawn_with_callback(model)

    def register_collisions(self):
        for m1, m2 in combinations(self.models.values(), 2):
            assert isinstance(m1, BaseModel)
            assert isinstance(m2, BaseModel)
            m1_intersection_parts, m2_intersection_parts = m1.bounding_box.intersected_polygons(m2.bounding_box)
            if not m1_intersection_parts and not m2_intersection_parts:
                continue
            intersects, x, y = m1.intersection_point(m2)
            if intersects:
                m1_vector = m2.movement - m1.movement
                m2_vector = -m1_vector
                m1_mass_quota = m2.mass / m1.mass
                m2_mass_quota = m1.mass / m2.mass
                m1_force = MutableForce(MutableOffsets(x, 0, y), m1_vector * m1_mass_quota)
                m2_force = MutableForce(MutableOffsets(x, 0, y), m2_vector * m2_mass_quota)
                m1.add_collision(m1_force)
                m2.add_collision(m2_force)
            for part in m1.parts_by_bounding_boxes(m1_intersection_parts):
                part.damage()
            for part in m2.parts_by_bounding_boxes(m2_intersection_parts):
                part.damage()
