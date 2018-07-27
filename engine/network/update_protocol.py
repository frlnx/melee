from twisted.internet.protocol import DatagramProtocol
from engine.engine import Engine
import pickle


class UpdateProtocol(DatagramProtocol):

    def __init__(self, engine: Engine):
        self.engine = engine

    def update(self, _):
        data = []
        for model in self.engine.models.values():
            data.append(model.data_dict)
        self.send(data)

    def datagramReceived(self, datagram, addr):
        frame = self.deserialize(datagram)
        self.engine.update_model(frame)

    @staticmethod
    def serialize(d: dict):
        ser = pickle.dumps(d, protocol=-1)
        return ser

    @staticmethod
    def deserialize(m: bytes):
        return pickle.loads(m)


class UpdateClientProtocol(UpdateProtocol):

    def __init__(self, engine, host, port):
        super().__init__(engine)
        self.host = host
        self.port = port

    def startProtocol(self):
        self.transport.connect(self.host, self.port)

    def start(self):
        self.engine.my_model.observe(self.client_movement)

    def client_movement(self):
        self.send([self.engine.my_model.data_dict])

    def send(self, data):
        ser = self.serialize(data)
        self.transport.write(ser)
