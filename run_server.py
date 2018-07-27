#!/usr/bin/env python

from engine.network.server.factories import BroadcastServerFactory
from engine.network.server.update_protocol import UpdateServerProtocol
from engine.pigtwisted import install
from engine import ServerEngine


def main():
    engine = ServerEngine()
    install(engine)
    from twisted.internet import reactor
    update_protocol = UpdateServerProtocol(engine)
    factory = BroadcastServerFactory(engine, update_protocol)
    reactor.listenTCP(8000, factory)
    reactor.listenUDP(8001, update_protocol)
    reactor.run(call_interval=1/60)

if __name__ == "__main__":
    main()
