from engine.views.factories import ShipViewFactory
from engine.models.factories import ShipModelFactory
from engine.controllers.ship import ShipController

class ShipControllerFactory(object):

    def __init__(self):
        self.view_factory = ShipViewFactory()
        self.model_factory = ShipModelFactory()

    def manufacture(self, name, gamepad):
        model = self.model_factory.manufacture(name)
        view = self.view_factory.manufacture(model)
        controller = ShipController(model, view, gamepad)
        return controller