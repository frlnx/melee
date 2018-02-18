from engine.models.base_model import BaseModel
from engine.controllers.factories import ShipControllerFactory, BaseFactory
from engine.controllers.projectiles import ProjectileController
from engine.views.factories import DummyViewFactory
from engine.input_handlers import GamePad

import pyglet

class Engine(pyglet.app.EventLoop):

    def __init__(self):
        super().__init__()
        self.controllers = set()
        self.ships = set()
        self.bf = BaseFactory(ProjectileController)
        self.sf = ShipControllerFactory()
        self.has_exit = True
        pyglet.clock.schedule(self.update)
        pyglet.clock.set_fps_limit(60)

    def on_enter(self):
        self.spawn_ship("dolph", [10, 0, 2], GamePad(0))
        self.spawn_ship("dolph", [0, 0, 20], GamePad(0))
        self.spawn_ship("dolph", [-10, 0, -2], GamePad(0))

    def spawn_ship(self, name, location, input_device=None):
        ship = self.sf.manufacture(name, input_device)
        self.propagate_target(ship)
        ship.move_to(location)
        self.spawn(ship)
        self.ships.add(ship)

    def spawn_model(self, model: BaseModel):


    def spawn(self, controller):
        self.window.add_view(controller.view)
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
            spawns += [self.bf.manufacture(model, controller._gamepad) for model in controller.spawns]
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
        for spawned_controller in spawns:
            self.spawn(spawned_controller)
