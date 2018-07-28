from engine.client import ClientEngine
from engine.network.client.update_protocol import UpdateClientProtocol
from engine.network.factories import EventClientFactory
from engine.pigtwisted import install


class NetworkClient(object):

    def __init__(self, engine: ClientEngine):
        event_loop = engine._event_loop
        install(event_loop)
        from twisted.internet import reactor
        self.connection = None
        self.listener = None
        self.engine = engine
        self.engine.bind_connect(self.connect)
        self.reactor = reactor
        self.engine.bind_stop(self.reactor.stop)
        self.reactor.run(call_interval=1/60)

    def connect(self, host, port=8000):
        update_protocol = UpdateClientProtocol(self.engine, host, port+1)
        factory = EventClientFactory(self.engine, update_protocol)
        self.connection = self.reactor.connectTCP(host, port, factory)
        self.listener = self.reactor.listenUDP(port + 2, update_protocol)

    def disconnect(self):
        self.connection.disconnect()
        self.listener.stopListening()
        print("Disconnected")
