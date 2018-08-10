from engine.engine import Engine


class ServerEngine(Engine):

    def __init__(self, event_loop):
        super().__init__(event_loop)
        self.on_enter()

    def on_enter(self):
        self.spawn_asteroids(20, area=2000)
