import pickle

from twisted.internet.protocol import DatagramProtocol

from engine.engine import Engine


class UpdateProtocol(DatagramProtocol):

    def __init__(self, engine: Engine):
        self.engine = engine

    def update(self, _):
        data = []
        for model in self.models_to_update:
            data.append(model.data_dict)
        self.send(data)

    @property
    def models_to_update(self):
        return self.engine.models.values()

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


