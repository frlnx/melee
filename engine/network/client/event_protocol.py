from engine.network.event_protocol import EventProtocol
from engine.client import ClientEngine


class ClientProtocol(EventProtocol):

    version = (1, 0, 0)

    def __init__(self, engine: ClientEngine):
        super().__init__(engine)
        self.engine = engine
        self._server_info = {}
        self.commands.update(
            {
                "server_info": self.server_info,
                "update_player_list": self.update_player_list,
                "enter": self.enter
            }
        )

    def connectionMade(self):
        super(ClientProtocol, self).connectionMade()
        self.engine.observe_new_models(self.engine_callback_new_model)
        self.engine.observe_dead_models(self.engine_callback_decay_model)
        self.engine.schedule_interval(self.initiate_ping, interval=10)
        self.send_login(self.engine.callsign)
        self.register_own_ship(self.engine.my_model)

    def engine_callback_new_model(self, model):
        self.send_spawn_model(model)

    def engine_callback_decay_model(self, model):
        self.send_decay_model(model)

    def send_login(self, username):
        self.send({"command": "login", "username": username})

    def register_own_ship(self, model):
        self.send({"command": "register_own_ship", "model": model})

    def server_info(self, frame):
        self._server_info = frame['server_info']

    def update_player_list(self, frame):
        for player in frame['players']:
            callsign = player['callsign']
            ship_uuid = player['ship_uuid']
            self.engine.register_player(callsign, ship_uuid)

    def enter(self, frame):
        self.engine.start_network()
