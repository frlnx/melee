from twisted.internet.protocol import Protocol, connectionDone
from engine import Engine
import pickle


class EventProtocol(Protocol):

    version = 1

    def __init__(self, factory, engine: Engine):
        self.factory = factory
        self.engine = engine
        self.commands = {
            "spawn": self.spawn_model
        }

    def connectionMade(self):
        self.transport.write("protocol version {} server version {}".format(self.version, self.engine.version))

    def connectionLost(self, reason=connectionDone):
        pass

    def dataReceived(self, data):
        frame = pickle.loads(data)
        self.commands.get(frame['command'], print("Can't handle: {}").format)(frame)

    def spawn_model(self, frame):
        self.engine.spawn_model(frame['model'])

    def register_new_player(self, frame):
        pass
        #self.engine.register_
