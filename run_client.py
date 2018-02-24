#!/usr/bin/env python

from engine.network.server_factory import EventClientFactory
from engine.pigtwisted import install
from engine import ClientEngine


def main():
    engine = ClientEngine()
    install(engine)
    from twisted.internet import reactor
    factory = EventClientFactory(engine)
    reactor.connectTCP("localhost", 8000, factory)
    reactor.run()

if __name__ == '__main__':
    main()