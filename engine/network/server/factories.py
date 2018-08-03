from twisted.internet.protocol import ServerFactory

from engine.network.server.event_protocol import BroadcastProtocol


class BroadcastServerFactory(ServerFactory):

    protocol = BroadcastProtocol

    def __init__(self, engine, update_protocol):
        self.addresses = {}
        self.send_functions = {}
        self.engine = engine
        self.update_protocol = update_protocol

    def startedConnecting(self, arg):
        print("Started connecting {}".format(arg))

    def clientConnectionLost(self, connector, reason):
        print("Lost client")

    def buildProtocol(self, addr):
        host = addr.host
        port = addr.port
        self.update_protocol.register_address(host, 8002)
        p = self.protocol(self.engine, self.broadcast)
        self.addresses[p.uuid] = addr
        self.send_functions[p.uuid] = p.send
        return p

    def broadcast(self, frame, original_client_uuid):
        for uuid, send in self.send_functions.items():
            if uuid == original_client_uuid:
                continue
            send(frame)