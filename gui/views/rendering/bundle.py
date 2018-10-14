from typing import Set

from pyglet.graphics import Group

from .context import Context


class Bundle(Group):

    def __init__(self, contexts: Set[Context]):
        super().__init__()
        self._contexts = contexts
        self.cost = sum(map(lambda x: x.cost, self._contexts))

    def set_state(self):
        for context in self._contexts:
            context.__enter__()

    def unset_state(self):
        for context in self._contexts:
            context.__exit__()

    def __enter__(self):
        self.set_state()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unset_state()

    def __eq__(self, other: "Bundle"):
        if not isinstance(other, self.__class__):
            return False
        return self._contexts == other._contexts

    def __hash__(self):
        return self._contexts.__hash__()

    def context_change_cost(self, other: "Bundle"):
        cost = sum(map(lambda x: x.cost, other._contexts - self._contexts))
        return cost
