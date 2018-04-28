from engine.models.factories import ProjectileModelSpawnFunctionFactory
from engine.controllers.ship import ShipController
from engine.controllers.ship_part import ShipPartController
from engine.controllers.base_controller import BaseController
from engine.models.ship import ShipModel
from engine.models.ship_part import ShipPartModel
from engine.models.projectiles import PlasmaModel
from engine.models.asteroid import AsteroidModel
from engine.input_handlers import InputHandler


class ControllerFactory(object):

    def __init__(self):
        self.dummy_input_handler = InputHandler()
        self.model_controller_map = {
            ShipModel: ShipControllerFactory().manufacture,
            ShipPartModel: ShipPartControllerFactory().manufacture,
            PlasmaModel: BaseFactory().manufacture,
            AsteroidModel: BaseFactory().manufacture,
        }

    def manufacture(self, model, input_handler=None):
        if not input_handler:
            input_handler = self.dummy_input_handler
        factory_func = self.model_controller_map[model.__class__]
        return factory_func(model, input_handler)


class BaseFactory(object):

    def __init__(self, controller_class=BaseController):
        self.controller_class = controller_class

    def manufacture(self, model, input_handler):
        controller = self.controller_class(model, input_handler)
        return controller


class ShipPartControllerFactory(object):

    def manufacture(self, model, gamepad, spawn_func=lambda: False) -> ShipPartController:
        controller = ShipPartController(model, gamepad, spawn_func)
        return controller


class ShipControllerFactory(object):

    def __init__(self, sub_controller_factory_class=ShipPartControllerFactory):
        self.sub_controller_factory = sub_controller_factory_class()
        self.projectile_model_spawn_func_factory = ProjectileModelSpawnFunctionFactory()

    def manufacture(self, model, gamepad):
        controller = ShipController(model, gamepad)
        for sub_model in model.parts:
            if sub_model.name == "plasma gun":
                spawn_func = self.projectile_model_spawn_func_factory.manufacture("plasma", model, sub_model)
            else:
                spawn_func = self._no_spawn
            sub_controller = self.sub_controller_factory.manufacture(sub_model, gamepad, spawn_func)
            controller.add_sub_controller(sub_controller)
        return controller

    def _no_spawn(self):
        pass
