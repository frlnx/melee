from twisted.internet.protocol import Protocol, connectionDone
import pickle
from datetime import datetime
from uuid import uuid4


class EventProtocol(Protocol):

    version = (1, 0, 0)

    def __init__(self, factory, engine):
        self.factory = factory
        self.engine = engine
        self.commands = {
            "handshake": self.handshake,
            "ping": self.ping,
            "pong": self.pong
        }
        self.uuid = uuid4()

    def connectionMade(self):
        self.send({"command": "handshake", "versions": {"protocol": self.version}})
        self.initiate_ping(None)

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
        self.commands.get(frame['command'], self.print_frame)(frame)

    def print_frame(self, frame):
        print("Can't handle", frame)

    def initiate_ping(self, _):
        self.send({"command": "ping", "ts": datetime.now().timestamp()})

    def handshake(self, frame):
        versions = frame['versions']
        assert self.version == versions['protocol']

    def ping(self, frame):
        self.send({"command": "pong", "ts": frame['ts']})

    def pong(self, frame):
        print(datetime.now().timestamp() - frame['ts'], "latency")
