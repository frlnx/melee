from engine.network.event_protocol import EventProtocol


class BroadcastProtocol(EventProtocol):

    def __init__(self, factory):
        super().__init__(factory)
        commands = {
            "spawn": self.factory.broadcast
        }
        self.commands.update(commands)

    def connectionMade(self):
        print("Got new client!")
        self.factory.clients.add(self)

    def connectionLost(self, reason):
        print("Lost a client!")
        self.factory.clients.remove(self)
