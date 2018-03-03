from engine.network.factories import BroadcastServerFactory
from engine.network.update_protocol import UpdateServerProtocol
from engine.pigtwisted import install
from engine import ServerEngine


class NetworkServer(object):

    def __init__(self, engine: ServerEngine):
        self.engine = engine
        install(engine)
        from twisted.internet import reactor
        self.reactor = reactor

    def listen(self, port=8000):
        update_protocol = UpdateServerProtocol(self.engine)
        factory = BroadcastServerFactory(self.engine, update_protocol)
        self.reactor.listenTCP(port, factory)
        self.reactor.listenUDP(port+1, update_protocol)
        self.reactor.run(call_interval=1/60)
