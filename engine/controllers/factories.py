from engine.views.factories import ViewFactory, DummyViewFactory
from engine.views.ship import ShipView
from engine.views.base_view import BaseView
from engine.views.ship_part import ShipPartView, TargetIndicatorView
from engine.models.factories import ShipModelFactory, ShipPartModelFactory, ProjectileModelSpawnFunctionFactory
from engine.controllers.ship import ShipController
from engine.controllers.ship_part import ShipPartController
from engine.controllers.base_controller import BaseController
from engine.controllers.projectiles import ProjectileController
from engine.models.ship import ShipModel
from engine.models.ship_part import ShipPartModel
from engine.models.projectiles import PlasmaModel
from engine.input_handlers import InputHandler


class ControllerFactory(object):

    def __init__(self):
        self.dummy_view_factory = DummyViewFactory()
        self.dummy_input_handler = InputHandler()
        self.model_controller_map = {
            ShipModel: ShipController,
            ShipPartModel: ShipPartController,
            PlasmaModel: ProjectileController
        }

    def manufacture(self, model, input_handler=None):
        if not input_handler:
            input_handler = self.dummy_input_handler
        view = self.dummy_view_factory.manufacture(model)
        controller_class = self.model_controller_map.get(model.__class__, BaseController)
        return controller_class(model, view, input_handler)


class BaseFactory(object):

    def __init__(self, controller_class=BaseController, view_factory_class=ViewFactory):
        self.controller_class = controller_class
        self.view_factory = view_factory_class(BaseView)

    def manufacture(self, model, input_handler):
        view = self.view_factory.manufacture(model)
        controller = self.controller_class(model, view, input_handler)
        return controller


class ShipPartControllerFactory(object):

    def __init__(self, view_factory_class=ViewFactory):
        self.view_factory = view_factory_class(ShipPartView)
        self.target_indicator_view_factory = view_factory_class(TargetIndicatorView)
        self.model_factory = ShipPartModelFactory()

    def manufacture(self, model, gamepad, spawn_func=lambda: False) -> ShipPartController:
        if model.target_indicator:
            view = self.target_indicator_view_factory.manufacture(model)
        else:
            view = self.view_factory.manufacture(model)
        controller = ShipPartController(model, view, gamepad, spawn_func)
        return controller

class DummyShipPartControllerFactory(ShipPartControllerFactory):

    def __init__(self):
        super().__init__(view_factory_class=DummyViewFactory)


class ShipControllerFactory(object):

    def __init__(self, view_factory_class=ViewFactory, sub_controller_factory_class=ShipPartControllerFactory):
        self.view_factory = view_factory_class(ShipView)
        self.model_factory = ShipModelFactory()
        self.sub_controller_factory = sub_controller_factory_class()
        self.projectile_model_spawn_func_factory = ProjectileModelSpawnFunctionFactory()

    def manufacture(self, name, gamepad):
        model = self.model_factory.manufacture(name)
        view = self.view_factory.manufacture(model)
        controller = ShipController(model, view, gamepad)
        for sub_model in model.parts:
            if sub_model.name == "plasma gun":
                spawn_func = self.projectile_model_spawn_func_factory.manufacture("plasma", model, sub_model)
            else:
                spawn_func = self._no_spawn
            sub_controller = self.sub_controller_factory.manufacture(sub_model, gamepad, spawn_func)
            controller.add_sub_controller(sub_controller)
            view.add_sub_view(sub_controller.view)
        return controller

    def _no_spawn(self):
        pass


class DummyViewShipControllerFactory(ShipControllerFactory):

    def __init__(self):
        super().__init__(view_factory_class=DummyViewFactory,
                         sub_controller_factory_class=DummyShipPartControllerFactory)

