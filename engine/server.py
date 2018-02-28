from engine.engine import Engine
from collections import defaultdict


class ServerEngine(Engine):

    def __init__(self):
        super().__init__()
        self.models_per_client = defaultdict(set)
        self.client_controlled_model = dict()
