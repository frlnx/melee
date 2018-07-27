from twisted.internet.protocol import ClientFactory

from engine.engine import Engine
from engine.network.client_protocol import ClientProtocol


class EventClientFactory(ClientFactory):

    protocol = ClientProtocol

    def __init__(self, engine: Engine, update_protocol):
        self.engine = engine
        self.update_protocol = update_protocol

    def startedConnecting(self, arg):
        print("Started connecting {}".format(arg))

    def clientConnectionLost(self, connector, reason):
        print("Lost client")

    def clientConnectionFailed(self, connector, reason):
        print("Failed to connect! {}".format(reason))

    def buildProtocol(self, addr):
        p =  self.protocol(self.engine)
        self.update_protocol.start()
        return p


