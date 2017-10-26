# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from .event_based_flow import EventBasedFlow
from ..builtin_events import *
from ..util.trace import Trace

class ThreadlessFlow(EventBasedFlow):
    def __init__(self, name=None):
        super().__init__(name)
        self.running = False

    def start(self):
        with self._lock:
            if self.running:
                return
            self.running = True
            self.queue.enqueue(FlowStart())

        Trace.debug("started flow '{}'", self.name)

    def stop(self):
        with self._lock:
            if not self.running:
                return
            self.queue.close(FlowStop())
            self.running = False

        Trace.debug("stopped flow '{}'", self.name)

    def dispatch(self):
        event = self.queue.dequeue()
        if event is None:
            return
        self.dispatch(event)

    def try_dispatch(self):
        event = self.queue.try_dequeue()
        if event is not None:
            self.dispatch(event)
        return event

    def try_dispatch_all(self):
        n = 0
        while True:
            event = self.queue.try_dequeue()
            if event is None:
                break
            self.dispatch(event)
            n += 1
        return n
