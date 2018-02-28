from engine.network.event_protocol import EventProtocol
from engine.engine import Engine


class ClientProtocol(EventProtocol):

    version = (1, 0, 0)

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.engine = engine
        self.commands.update({
            "spawn": self.spawn_model,
        })
        
    def connectionMade(self):
        super(ClientProtocol, self).connectionMade()
        self.engine.observe_new_models(self.engine_callback_new_model)
        self.engine.clock.schedule_interval(self.initiate_ping, interval=10)
        for model in self.engine.models.values():
            self.send_spawn_model(model)

    def engine_callback_new_model(self, model):
        self.send_spawn_model(model)

    def spawn_model(self, frame):
        self.engine.spawn(frame['model'])

    def handshake(self, frame):
        versions = frame['versions']
        assert self.version == versions['protocol']
