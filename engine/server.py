from engine.engine import Engine


class ServerEngine(Engine):

    def on_enter(self):
        self.spawn_asteroids(200, area=2000)
