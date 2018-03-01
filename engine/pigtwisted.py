from queue import Queue, Empty
from functools import partial
import pyglet

from twisted.python import log
from twisted.internet import _threadedselect


class TwistedEventLoop(pyglet.app.base.EventLoop):

    def register_twisted_queue(self, queue, interval):
        f = partial(self._make_twisted_calls, queue)
        self.clock.schedule_interval_soft(f, interval)

    @staticmethod
    def _make_twisted_calls(queue: Queue, _):
        try:
            f = queue.get(block=False)
        except Empty:
            pass
        else:
            f()


class PygletReactor(_threadedselect.ThreadedSelectReactor):

    max_fps = 120

    def __init__(self, event_loop):
        super().__init__()
        self._postQueue = Queue()
        self._twistedQueue = Queue()
        self.pyglet_event_loop = event_loop
        self._stopping = False

    def stop(self):
        if self._stopping:
            return
        self._stopping = True
        _threadedselect.ThreadedSelectReactor.stop(self)

    def _run_in_main_thread(self, f):
        """Schedule Twisted calls within the Pyglet event loop."""
        if hasattr(self, "pyglet_event_loop"):
            # Add the function to a queue which is called as part
            # of the Pyglet event loop (see EventLoop above)
            self._twistedQueue.put(f)
        else:
            # If Pyglet has stopped, add the events to a queue which
            # is processed prior to shutting Twisted down.
            self._postQueue.put(f)

    def _stop_pyglet(self):
        """Stop the pyglet event loop."""

        if hasattr(self, "pygletEventLoop"):
            self.pyglet_event_loop.exit()

    def run(self, call_interval=1 / 10., installSignalHandlers=True):
        call_interval = max((1 / self.max_fps), call_interval)
        self.pyglet_event_loop.register_twisted_queue(self._twistedQueue, call_interval)

        self.interleave(self._run_in_main_thread, installSignalHandlers=installSignalHandlers)

        self.addSystemEventTrigger("after", "shutdown", self._stop_pyglet)
        self.addSystemEventTrigger("after", "shutdown", lambda: self._postQueue.put(None))

        self.pyglet_event_loop.run()
        self.graceful_shutdown()

    def graceful_shutdown(self):
        # Now that the event loop has finished, remove
        # it so that further Twisted events are added to
        # the shutdown queue, and are dealt with below.
        del self.pyglet_event_loop
        last_twisted_event = None
        if not self._stopping:
            # The Pyglet event loop is no longer running, so we monitor the
            # queue containing Twisted events until all events are dealt with.
            self.stop()
            while 1:
                try:
                    f = self._postQueue.get(timeout=0.01)
                except Empty:
                    continue
                else:
                    if f is last_twisted_event:
                        break
                    try:
                        f()
                    except:
                        log.err()


def install(event_loop):
    reactor = PygletReactor(event_loop=event_loop)
    from twisted.internet.main import installReactor
    installReactor(reactor)
    return reactor
