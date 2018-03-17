from engine.network.factories import EventClientFactory
from engine.network.update_protocol import UpdateClientProtocol
from engine.pigtwisted import install
from engine import ClientEngine


class NetworkClient(object):

    def __init__(self, engine: ClientEngine):
        install(engine)
        from twisted.internet import reactor
        self.engine = engine
        self.engine.bind_connect(self.connect)
        self.reactor = reactor
        self.engine.bind_stop(self.reactor.stop)
        self.reactor.run(call_interval=1/60)

    def connect(self, host, port=8000):
        update_protocol = UpdateClientProtocol(self.engine, host, port+1)
        factory = EventClientFactory(self.engine, update_protocol)
        self.reactor.connectTCP(host, port, factory)
        self.reactor.listenUDP(port+2, update_protocol)
