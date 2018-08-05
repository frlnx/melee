import random
import time
from collections import defaultdict
from typing import Callable

from twisted.internet.task import LoopingCall

from engine.models.base_model import BaseModel
from engine.models.factories import ShipModelFactory, AsteroidModelFactory
from engine.physics.force import MutableOffsets, MutableForce
from engine.physics.spacial_index import SpacialIndex


class Engine(object):

    fps = 60

    version = (1, 0, 0)

    def __init__(self, event_loop):
        self._observers = defaultdict(set)
        self._event_loop = event_loop
        self.smf = ShipModelFactory()
        self.amf = AsteroidModelFactory()
        self.has_exit = True
        self.rnd = random.seed()
        self._new_model_callbacks = set()
        self._dead_model_callbacks = set()
        self.models = {}
        self._time_spent = 0
        self._scheduled_taks = {}
        self._players = {}
        self._collision_check_models = set()
        self._spacial_index = SpacialIndex()

    def observe(self, func: Callable, action: str):
        self._observers[action].add(func)

    def unobserve(self, func, action):
        self._observers[action].remove(func)

    def callback(self, action):
        for func in self._observers[action]:
            func()

    def register_player(self, callsign, ship_uuid):
        self._players[ship_uuid] = callsign
        self.callback("players")

    def deregister_player(self, ship_uuid):
        del self._players[ship_uuid]
        self.callback("players")

    @property
    def players(self):
        return [{"callsign": callsign, "ship_uuid": ship_uuid} for ship_uuid, callsign in self._players.items()]

    def schedule(self, func: Callable):
        self.schedule_interval(func, 1 / self.fps)

    def schedule_interval(self, func, interval):
        lc = LoopingCall(lambda: self._call_with_time_since(func))
        lc.start(interval)

    def _call_with_time_since(self, func: Callable):
        func_name = func.__name__
        last_time = self._scheduled_taks.get(func_name, time.time())
        now = time.time()
        dt = now - last_time
        func(dt)
        self._scheduled_taks[func_name] = now

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
        self.models = {}

    def spawn_asteroids(self, n, area=200):
        i = 0
        failed_attempts = 0
        while i <= n and failed_attempts <= n * 2:
            model = self.amf.manufacture(self.random_position(area=area))
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
        self.spawn(model)
        self._new_model_callback(model)

    def spawn(self, model: BaseModel):
        self.models[model.uuid] = model
        model.observe(lambda: self._add_to_collision_checks(model))
        bbox = model.bounding_box
        bbox.observe(lambda: self._spacial_index.reindex_spacial_position(model), "quadrants")
        self._spacial_index.init_model_into_2d_space_index(model)

    def _add_to_collision_checks(self, model: BaseModel):
        self._collision_check_models.add(model)

    def decay(self, uuid):
        model = self.models[uuid]
        model.set_alive(False)
        self.remove_model_by_uuid(uuid)
        self._spacial_index.clear_model_from_2d_space_index(model)
        if model in self._collision_check_models:
            self._collision_check_models.remove(model)

    def remove_model_by_uuid(self, uuid):
        try:
            del self.models[uuid]
        except KeyError:
            pass

    def decay_with_callback(self, model):
        self.decay(model.uuid)
        self._dead_model_callback(model)

    def update(self, dt):
        spawns = []
        decays = []
        for model in self.models.values():
            model.run(dt)
            new_spawns = model.spawns
            spawns += new_spawns
            if not model.is_alive:
                decays.append(model)
        for decaying_model in decays:
            self.decay_with_callback(decaying_model)
        self.register_collisions()
        for model in spawns:
            self.spawn_with_callback(model)

    def register_collisions(self):
        pairs = self._spacial_index.all_pairs_deduplicated(self._collision_check_models)
        for m1, m2 in pairs:
            assert isinstance(m1, BaseModel)
            assert isinstance(m2, BaseModel)
            m1_intersection_parts, m2_intersection_parts = m1.intersected_polygons(m2)
            if not m1_intersection_parts and not m2_intersection_parts:
                continue
            intersects, x, y = m1.intersection_point(m2)
            if intersects:
                m1_vector = m2.movement - m1.movement
                m2_vector = -m1_vector
                combined_mass = m1.mass + m2.mass
                m1_mass_quota = m2.mass / combined_mass
                m2_mass_quota = m1.mass / combined_mass
                m1_force = MutableForce(MutableOffsets(x, 0, y), m1_vector * m1_mass_quota)
                m2_force = MutableForce(MutableOffsets(x, 0, y), m2_vector * m2_mass_quota)
                m1.add_collision(m1_force)
                m2.add_collision(m2_force)
            if m1.destructable and m2.destructable:
                n_parts_damaged = min(len(m1_intersection_parts), len(m2_intersection_parts))
                m1_intersection_parts = m1_intersection_parts[:n_parts_damaged]
                m2_intersection_parts = m2_intersection_parts[:n_parts_damaged]
            for part in m1.parts_by_bounding_boxes(m1_intersection_parts):
                part.damage()
            for part in m2.parts_by_bounding_boxes(m2_intersection_parts):
                part.damage()
        self._collision_check_models.clear()
