from twisted.internet.protocol import ServerFactory

from engine.engine import Engine
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

    def __init__(self, engine):
        self.clients = set()
        self.engine = engine

    def startedConnecting(self, arg):
        print("Started connecting {}".format(arg))

    def clientConnectionLost(self, *args):
        print("Lost client", *args)

    def buildProtocol(self, addr):
        return self.protocol(self, self.engine)

    def broadcast(self, frame, original_client_uuid):
        print("Broadcasting!")
        for client in self.clients:
            if client.uuid == original_client_uuid:
                continue
            client.send(frame)
