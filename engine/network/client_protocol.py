from engine.network.event_protocol import EventProtocol
from engine import Engine


class ClientProtocol(EventProtocol):

    version = (1, 0, 0)

    def __init__(self, factory, engine: Engine):
        super().__init__(factory)
        self.engine = engine
        self.commands = {
            "spawn": self.spawn_model,
            "handshake": self.handshake
        }
        
    def connectionMade(self):
        super(ClientProtocol, self).connectionMade()
        self.engine.observe_new_models(self.engine_callback_new_model)

    def engine_callback_new_model(self, model):
        self.send({"command": "spawn", "model": model})

    def spawn_model(self, frame):
        self.engine.spawn(frame['model'])

    def handshake(self, frame):
        versions = frame['versions']
        assert self.version == versions['protocol']
        assert self.engine.version == versions['engine']

