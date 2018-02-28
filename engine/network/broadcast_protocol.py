from engine.network.event_protocol import EventProtocol


class BroadcastProtocol(EventProtocol):

    def __init__(self, engine, broadcast_func):
        super().__init__(engine)
        self.engine = engine
        commands = {
            "spawn": self.broadcast
        }
        self.commands.update(commands)
        self.broadcast_func = broadcast_func
        self.known_models = set()
        self.controlled_model = None

    def spawn_model(self, frame):
        super(BroadcastProtocol, self).spawn_model(frame)
        if self.controlled_model is None:
            self.controlled_model = frame['model']
        self.known_models.add(frame['model'])
        self.broadcast(frame)

    def broadcast(self, frame):
        self.broadcast_func(frame, self.uuid)
