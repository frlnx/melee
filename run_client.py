#!/usr/bin/env python

from engine.client import ClientEngine
from engine.input_handlers import Keyboard, GamePad
from engine.network.client import NetworkClient
from engine.window import Window
from engine.pigtwisted import TwistedEventLoop

def main():
    try:
        gamepad = GamePad(0)
        print("Gamepad found!")
    except:
        gamepad = None
        print("No gamepad found!")
    window = Window(input_handler=gamepad)
    gamepad = gamepad or Keyboard(window)
    event_loop = TwistedEventLoop()
    engine = ClientEngine(event_loop=event_loop, input_handler=gamepad, window=window)
    NetworkClient(engine)

if __name__ == '__main__':
    main()
