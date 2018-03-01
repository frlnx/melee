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
        print(">> {} UDP".format(len(datagram)))
        frame = self.deserialize(datagram)
        self.engine.update_model(frame)

    @staticmethod
    def serialize(d: dict):
        ser = pickle.dumps(d, protocol=-1)
        return ser

    @staticmethod
    def deserialize(m: bytes):
        return pickle.loads(m)


class UpdateServerProtocol(UpdateProtocol):

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.addresses = []
        self.engine.clock.schedule_interval(self.update, interval=1)

    def register_address(self, ip, port):
        self.addresses.append((ip, port))

    def unregister_address(self, ip, port):
        self.addresses.remove((ip, port))

    def send(self, data):
        self.broadcast(data)

    def broadcast(self, data):
        ser = self.serialize(data)
        print("<< {} UDP".format(len(ser)))
        for address in self.addresses:
            self.transport.write(ser, address)


class UpdateClientProtocol(UpdateProtocol):

    def __init__(self, engine, host, port):
        super().__init__(engine)
        self.host = host
        self.port = port

    def startProtocol(self):
        self.transport.connect(self.host, self.port)

    def start(self):
        self.engine.clock.schedule_interval(self.update, interval=1)
        self.engine.my_model.observe(self.client_movement)

    def client_movement(self):
        self.send([self.engine.my_model.data_dict])

    def send(self, data):
        ser = self.serialize(data)
        self.transport.write(ser)
