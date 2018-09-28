import inspect
from collections import defaultdict
from typing import Callable


class RemoveCallbackException(Exception):
    pass


class Observer:

    def __init__(self, callback: Callable):
        self._callback = callback
        self.__eq__ = callback.__eq__
        self.__hash__ = callback.__hash__

    def __call__(self, *args, **kwargs):
        self._callback(**kwargs)


class SelfObserver(Observer):

    def __init__(self, callback, observable):
        super(SelfObserver, self).__init__(callback)
        self._observable = observable

    def __call__(self, *args, **kwargs):
        self._callback(caller=self._observable, **kwargs)


class Observable:

    def __init__(self):
        self._new_observers = defaultdict(set)
        self._observers = defaultdict(set)
        self._removed_observers = defaultdict(set)

    def _make_observer(self, callback: Callable):
        if 'caller' in inspect.signature(callback).parameters:
            return SelfObserver(callback, self)
        else:
            return Observer(callback)

    def observe(self, callback: Callable, action):
        self._new_observers[action].add(self._make_observer(callback))

    def unobserve(self, callback: Callable, action):
        self._removed_observers[action].add(self._make_observer(callback))

    def _callback(self, action, **kwargs):
        self._prune_removed_observers(action)
        self._introduce_new_observers(action)
        for callback in self._observers[action]:
            try:
                callback(**kwargs)
            except RemoveCallbackException:
                self.unobserve(callback, action)

    def remove_all_observers(self):
        self._removed_observers = self._observers

    def _introduce_new_observers(self, action):
        self._observers[action] |= self._new_observers[action]
        self._new_observers[action].clear()

    def _prune_removed_observers(self, action):
        self._observers[action] -= self._removed_observers[action]
        self._removed_observers[action].clear()


__all__ = [Observable]
