from engine.controllers.factories import ShipControllerFactory
from engine.input_handlers import InputHandler


factory = ShipControllerFactory()
dummy_input = InputHandler()

class _TestShipController(object):

    def setup(self):
        self.target = factory.manufacture("ship", dummy_input)

    def test_move_to(self):
        self.target._model.set_position(100, 0, 0)
        for line in self.target._model.bounding_box.lines:
            assert line.x == 100
