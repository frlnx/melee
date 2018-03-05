#!/usr/bin/env python

from engine.network.client import NetworkClient
from engine import ClientEngine
from engine.window import Window
from engine.input_handlers import Keyboard


def main():
    window = Window()
    keyboard = Keyboard(window)
    engine = ClientEngine(keyboard, window=window)
    host = '192.168.2.2'
    port = 8000
    client = NetworkClient(engine)
    #client.connect(host, port)

if __name__ == '__main__':
    main()
