# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from threading import Thread

from .event_based_flow import EventBasedFlow
from ..builtin_events import *
from ..flow import Flow
from ..util.trace import Trace

class SingleThreadFlow(EventBasedFlow):
    def __init__(self, name=None):
        super().__init__(name)
        self.thread = None

    def start(self):
        with self._lock:
            if self.thread is not None:
                return

            self.cases.setup(self)

            self.thread = Thread(target=self)
            self.thread.setName(self.name)
            self.thread.start()

            self.queue.enqueue(FlowStart())

        Trace.debug("started flow '{}'", self.name)

    def stop(self):
        with self._lock:
            if self.thread is None:
                return

            self.queue.close(FlowStop())

            self.thread.join()
            self.thread = None

            self.cases.teardown(self)

        Trace.debug("stopped flow '{}'", self.name)

    def __call__(self):
        Flow.thread_local.current = self
        Flow.thread_local.event_proxy = EventProxy()
        Flow.thread_local.handler_chain = []

        while True:
            event = self.queue.dequeue()
            if event is None:
                break
            self.dispatch(event)

        Flow.thread_local.handler_chain = None
        Flow.thread_local.event_proxy = None
        Flow.thread_local.current = None
