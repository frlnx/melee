#!/usr/bin/env python

from twisted.internet import reactor
from engine.network.server_factory import BroadcastServerFactory


def main():
    factory = BroadcastServerFactory()
    reactor.listenTCP(8000, factory)
    reactor.run()

if __name__ == '__main__':
    main()