from twisted.internet.protocol import connectionDone
from twisted.protocols.basic import Int32StringReceiver
import pickle
from datetime import datetime
from uuid import uuid4


class EventProtocol(Int32StringReceiver):

    version = (1, 0, 0)

    def __init__(self, engine):
        self.engine = engine
        self.username = None
        self._latency = 0
        self.commands = {
            "handshake": self.handshake,
            "register_own_ship": self.register_own_ship,
            "ping": self.ping,
            "pong": self.pong,
            "spawn": self.spawn_model,
            "decay": self.decay_model
        }
        self.uuid = uuid4()

    def get_latency(self):
        return self._latency

    def connectionMade(self):
        self.send({"command": "handshake", "versions": {"protocol": self.version}})
        self.initiate_ping(None)

    @staticmethod
    def serialize(d: dict) -> bytes:
        ser = pickle.dumps(d, protocol=-1)
        return ser

    @staticmethod
    def deserialize(m: bytes) -> dict:
        return pickle.loads(m)

    def send(self, frame: dict):
        ser = self.serialize(frame)
        print("<< {} {}".format(len(ser), frame))
        self.sendString(ser)

    def send_spawn_model(self, model):
        self.send({"command": "spawn", "model": model})

    def send_decay_model(self, model):
        self.send({"command": "decay", "model_uuid": model.uuid})

    def spawn_model(self, frame):
        self.engine.spawn(frame['model'])

    def decay_model(self, frame):
        self.engine.decay(frame['model_uuid'])

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
