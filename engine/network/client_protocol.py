from engine.network.event_protocol import EventProtocol


class ClientProtocol(EventProtocol):

    version = (1, 0, 0)

    def connectionMade(self):
        super(ClientProtocol, self).connectionMade()
        self.engine.observe_new_models(self.engine_callback_new_model)
        self.engine.observe_dead_models(self.engine_callback_decay_model)
        self.engine.schedule_interval(self.initiate_ping, interval=10)

    def engine_callback_new_model(self, model):
        self.send_spawn_model(model)

    def engine_callback_decay_model(self, model):
        self.send_decay_model(model)
