# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from threading import Thread

from x2py.builtin_events import *
from x2py.flow import Flow
from x2py.flows.event_based_flow import EventBasedFlow
from x2py.util.trace import Trace

class SingleThreadFlow(EventBasedFlow):
    def __init__(self, name=None):
        super(SingleThreadFlow, self).__init__(name)
        self.thread = None

    def start(self):
        with self._lock:
            if self.thread is not None:
                return

            self._setup()
            self.cases.setup_with(self)

            self.thread = Thread(target=self)
            self.thread.setName(self.name)
            self.thread.start()

            self.queue.enqueue(FlowStart())

    def stop(self):
        with self._lock:
            if self.thread is None:
                return

            self.queue.close(FlowStop())

            self.thread.join()
            self.thread = None

            self.cases.teardown_with(self)
            self._teardown()

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

