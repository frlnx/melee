from twisted.internet.protocol import connectionDone
from twisted.protocols.basic import Int32StringReceiver
import pickle
from datetime import datetime
from uuid import uuid4


class EventProtocol(Int32StringReceiver):

    version = (1, 0, 0)

    def __init__(self, engine):
        self.engine = engine
        self._latency = 0
        self.commands = {
            "handshake": self.handshake,
            "ping": self.ping,
            "pong": self.pong,
            "spawn": self.spawn_model
        }
        self.uuid = uuid4()
        self.known_models = set()
        self.controlled_model = None

    def get_latency(self):
        return self._latency

    def connectionMade(self):
        self.send({"command": "handshake", "versions": {"protocol": self.version}})
        self.initiate_ping(None)
        for c in self.engine.controllers:
            self.send_spawn_model(c._model)

    @staticmethod
    def serialize(d: dict):
        ser = pickle.dumps(d, protocol=-1)
        return ser

    @staticmethod
    def deserialize(m: bytes):
        return pickle.loads(m)

    def send(self, frame: dict):
        ser = self.serialize(frame)
        print("<< {} {}".format(len(ser), frame))
        self.sendString(ser)

    def send_spawn_model(self, model):
        if model not in self.known_models:
            self.send({"command": "spawn", "model": model})

    def spawn_model(self, frame):
        if self.controlled_model is None:
            self.controlled_model = frame['model']
        self.known_models.add(frame['model'])
        self.engine.spawn(frame['model'])

    def connectionLost(self, reason=connectionDone):
        pass

    def stringReceived(self, data):
        frame = self.deserialize(data)
        print(">> {} {}".format(len(data), frame))
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
        latency = datetime.now().timestamp() - frame['ts']
        self._latency = latency
        print(latency, "latency")
