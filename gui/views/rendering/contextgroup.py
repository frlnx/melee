from typing import Set

from .context import Context


class ContextGroup:

    def __init__(self, contexts: Set[Context]):
        super().__init__()
        self._contexts = contexts
        self.cost = sum(map(lambda x: x.cost, self._contexts))

    def activate(self):
        for context in self._contexts:
            context.__enter__()

    def deactivate(self):
        for context in self._contexts:
            context.__exit__()

    def __enter__(self):
        self.activate()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deactivate()

    def __eq__(self, other: "ContextGroup"):
        if not isinstance(other, self.__class__):
            return False
        return self._contexts == other._contexts

    def __hash__(self):
        return self._contexts.__hash__()

    def context_change_cost(self, other: "ContextGroup"):
        cost = sum(map(lambda x: x.cost, other._contexts - self._contexts))
        return cost
