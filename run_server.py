#!/usr/bin/env python

from twisted.internet import reactor
from engine.network.server.factories import BroadcastServerFactory
from engine.network.server.update_protocol import UpdateServerProtocol
from engine import ServerEngine


def main():
    engine = ServerEngine(reactor)
    update_protocol = UpdateServerProtocol(engine)
    factory = BroadcastServerFactory(engine, update_protocol)
    reactor.listenTCP(8000, factory)
    reactor.listenUDP(8001, update_protocol)
    reactor.run(call_interval=1/60)

if __name__ == "__main__":
    main()
