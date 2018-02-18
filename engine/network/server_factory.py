from twisted.internet.protocol import ServerFactory

from engine import Engine
from engine.network.event_protocol import EventProtocol

class EventServerFactory(ServerFactory):

    protocol = EventProtocol

    def __init__(self, engine: Engine):
        self.engine = engine
        self.clients = set()

    def buildProtocol(self, addr):
        return self.protocol(self, self.engine)
