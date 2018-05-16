# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from .event_based_flow import EventBasedFlow
from ..builtin_events import *
from ..flow import Flow
from ..util.trace import Trace

class ThreadlessFlow(EventBasedFlow):
    def __init__(self, name=None):
        super(ThreadlessFlow, self).__init__(name)
        self.running = False

    def start(self):
        with self._lock:
            if self.running:
                return

            self._setup()
            self.cases.setup_with(self)

            Flow.thread_local.current = self
            Flow.thread_local.event_proxy = EventProxy()
            Flow.thread_local.handler_chain = []

            self.running = True
            self.queue.enqueue(FlowStart())

        Trace.debug("started flow '{}'", self.name)

    def stop(self):
        with self._lock:
            if not self.running:
                return

            self.queue.close(FlowStop())
            self.running = False

            Flow.thread_local.handler_chain = None
            Flow.thread_local.event_proxy = None
            Flow.thread_local.current = None

            self.cases.teardown_with(self)
            self._teardown()

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
