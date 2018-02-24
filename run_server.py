#!/usr/bin/env python

from engine.network.server_factory import BroadcastServerFactory
from engine.pigtwisted import install
from engine import ServerEngine


def main():
    engine = ServerEngine()
    install(engine)
    from twisted.internet import reactor
    factory = BroadcastServerFactory(engine)
    reactor.listenTCP(8000, factory)
    reactor.run()

if __name__ == "__main__":
    main()
