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

    def spawn_model(self, frame):
        super(BroadcastProtocol, self).spawn_model(frame)
        self.broadcast(frame)

    def broadcast(self, frame):
        self.broadcast_func(frame, self.uuid)
