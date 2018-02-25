from engine.network.event_protocol import EventProtocol


class BroadcastProtocol(EventProtocol):

    def __init__(self, factory, engine):
        super().__init__(factory, engine)
        self.engine = engine
        commands = {
            "spawn": self.broadcast
        }
        self.commands.update(commands)

    def connectionMade(self):
        print("Got new client!")
        self.factory.clients.add(self)
        self.send({"command": "handshake", "versions": {"protocol": self.version}})

    def connectionLost(self, reason):
        print("Lost a client!")
        self.factory.clients.remove(self)

    def spawn_model(self, frame):
        self.engine.spawn(frame['model'])
        self.broadcast(frame)

    def broadcast(self, frame):
        self.factory.broadcast(frame, self.uuid)
