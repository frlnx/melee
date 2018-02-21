from twisted.internet.protocol import ServerFactory

from engine import Engine
from engine.network.client_protocol import ClientProtocol
from engine.network.broadcast_protocol import BroadcastProtocol


class EventClientFactory(ServerFactory):

    protocol = ClientProtocol

    def __init__(self, engine: Engine):
        self.engine = engine

    def startedConnecting(self, arg):
        print("Started connecting {}".format(arg))

    def clientConnectionLost(self):
        print("Lost client")

    def clientConnectionFailed(self, reason):
        print("Failed to connect! {}".format(reason))

    def buildProtocol(self, addr):
        return self.protocol(self, self.engine)


class BroadcastServerFactory(ServerFactory):

    protocol = BroadcastProtocol

    def __init__(self):
        self.clients = set()

    def startedConnecting(self, arg):
        print("Started connecting {}".format(arg))

    def clientConnectionLost(self):
        print("Lost client")

    def buildProtocol(self, addr):
        p = self.protocol(self)
        return p

    def broadcast(self, origin_client, frame):
        for client in self.clients:
            if client == origin_client:
                continue
            client.message(frame)
