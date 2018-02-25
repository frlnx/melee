#!/usr/bin/env python

from engine.network.factories import EventClientFactory
from engine.pigtwisted import install
from engine import ClientEngine
from sys import argv


def main():
    print(argv)
    engine = ClientEngine(int(argv[1]))
    install(engine)
    from twisted.internet import reactor
    factory = EventClientFactory(engine)
    reactor.connectTCP("localhost", 8000, factory)
    reactor.run()

if __name__ == '__main__':
    main()