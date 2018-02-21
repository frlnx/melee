from twisted.internet.protocol import Protocol, connectionDone
import pickle


class EventProtocol(Protocol):

    version = (1, 0, 0)

    def __init__(self, factory):
        self.factory = factory
        self.commands = {
            "handshake": self.handshake
        }

    def connectionMade(self):
        self.send({"command": "handshake", "versions": {"protocol": self.version}})

    @staticmethod
    def serialize(d: dict):
        return pickle.dumps(d, protocol=-1)

    @staticmethod
    def deserialize(m: object):
        return pickle.loads(m)

    def send(self, frame: dict):
        print(">> {}".format(frame))
        ser = self.serialize(frame)
        self.transport.write(ser)

    def connectionLost(self, reason=connectionDone):
        pass

    def dataReceived(self, data):
        frame = self.deserialize(data)
        print("<< {}".format(frame))
        self.commands.get(frame['command'], self.print_frame)(self, frame)

    @staticmethod
    def print_frame(self, frame):
        print("Can't handle", frame)

    @staticmethod
    def handshake(self, frame):
        versions = frame['versions']
        assert self.version == versions['protocol']

