#class _TestShipController(object):
#    factory = ShipControllerFactory()
#    dummy_input = InputHandler()
#    def setup(self):
#        self.target = self.factory.manufacture("ship", self.dummy_input)
#
#    def test_move_to(self):
#        self.target._model.set_position(100, 0, 0)
#        for line in self.target._model.bounding_box.lines:
#            assert line.x == 100
