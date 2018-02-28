#!/usr/bin/env python

from engine.network.factories import EventClientFactory
from engine.network.update_protocol import UpdateClientProtocol
from engine.pigtwisted import install
from engine import ClientEngine
from sys import argv


def main():
    print(argv)
    try:
        controller_id = int(argv[1])
    except IndexError:
        controller_id = -1
    engine = ClientEngine(controller_id)
    install(engine)
    from twisted.internet import reactor
    host = '127.0.0.1'
    tcp_port = 8000
    udp_port = 8001
    update_protocol = UpdateClientProtocol(engine, host, 8001)
    factory = EventClientFactory(engine, update_protocol)
    reactor.connectTCP(host, tcp_port, factory)
    reactor.listenUDP(8002, update_protocol)
    reactor.run()

if __name__ == '__main__':
    main()