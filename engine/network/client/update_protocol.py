from engine.client import ClientEngine
from engine.network.update_protocol import UpdateProtocol


class UpdateClientProtocol(UpdateProtocol):

    def __init__(self, engine: ClientEngine, host, port):
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

    @property
    def models_to_update(self):
        return [self.engine.my_model]
