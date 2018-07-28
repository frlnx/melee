from engine.network.server.event_protocol import BroadcastProtocol
from engine.network.client.event_protocol import ClientProtocol
from io import BytesIO


class MockEngine(object):

    def __init__(self, models, spawn_func):
        self.models = models
        self.spawn_func = spawn_func
        self.clock = object()
        setattr(self.clock, 'schedule_interval', self.schedule_interval)

    def schedule_interval(self, *args):
        pass

    def observe_new_models(self, func):
        pass


class _TestBroadcastProtocol(object):

    def setup(self):
        self.models = {"foo": "bar"}
        self.mock_engine = MockEngine(self.models, self.spawn_func)
        self.server = BroadcastProtocol(self.mock_engine, self.broadcast)
        self.target = BytesIO()
        self.server.transport = self.target
        self.broadcasted_data = {}

    def broadcast(self, data):
        self.broadcasted_data = data

    def spawn_func(self, model):
        self.models[model.uuid] = model

    def test_connect(self):
        self.server.connectionMade()
        self.target.seek(0)
        assert b'spawn' in self.target.read()


class _TestClientProtocol(object):

    def setup(self):
        self.models = {"foo": "bar"}
        self.mock_engine = MockEngine(self.models, self.spawn_func)
        self.server = ClientProtocol(self.mock_engine)
        self.target = BytesIO()
        self.server.transport = self.target

    def spawn_func(self, model):
        self.models[model.uuid] = model

    def test_connect(self):
        self.server.connectionMade()
        self.target.seek(0)
        assert b'spawn' in self.target.read()