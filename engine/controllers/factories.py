from engine.views.factories import ViewFactory
from engine.models.factories import ShipModelFactory, ShipPartModelFactory
from engine.controllers.ship import ShipController
from engine.controllers.ship_part import ShipPartController

class ShipControllerFactory(object):

    def __init__(self):
        self.view_factory = ViewFactory()
        self.model_factory = ShipModelFactory()
        self.sub_controller_factory = ShipPartControllerFactory()

    def manufacture(self, name, gamepad):
        model = self.model_factory.manufacture(name)
        view = self.view_factory.manufacture(model)
        controller = ShipController(model, view, gamepad)
        for sub_model in model.parts:
            sub_controller = self.sub_controller_factory.manufacture(sub_model, gamepad)
            controller.add_sub_controller(sub_controller)
            view.add_sub_view(sub_controller.view)
        return controller


class ShipPartControllerFactory(object):

    def __init__(self):
        self.view_factory = ViewFactory()
        self.model_factory = ShipPartModelFactory()

    def manufacture(self, model, gamepad) -> ShipPartController:
        view = self.view_factory.manufacture(model)
        controller = ShipPartController(model, view, gamepad)
        return controller