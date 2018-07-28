from engine.network.event_protocol import EventProtocol


class BroadcastProtocol(EventProtocol):

    def __init__(self, engine, broadcast_func):
        super().__init__(engine)
        self.username = None
        self.broadcast_func = broadcast_func
        self.own_model = None
        self.commands.update(
            {
                "login": self.login,
                "register_own_ship": self.register_own_ship
            }
        )

    def spawn_model(self, frame):
        super(BroadcastProtocol, self).spawn_model(frame)
        self.broadcast(frame)

    def broadcast(self, frame):
        self.broadcast_func(frame, self.uuid)

    def connectionMade(self):
        pass

    def login(self, frame):
        if not self.username:
            self.username = frame['username']

    def register_own_ship(self, frame):
        self.send_player_list()
        self.own_model = frame['model']
        self.engine.register_player(self.username, self.own_model.uuid)
        self.spawn_model(frame)
        self.send_spawn_all_models()
        self.send_enter()

    def send_spawn_all_models(self):
        for model in self.engine.models.values():
            self.send_spawn_model(model)

    def send_player_list(self):
        self.send({"command": "update_player_list", "players": self.engine.players})

    def send_enter(self):
        self.send({"command": "enter"})
