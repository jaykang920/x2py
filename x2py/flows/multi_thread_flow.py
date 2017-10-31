# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from threading import Thread

from .event_based_flow import EventBasedFlow
from ..builtin_events import *
from ..event import EventProxy
from ..flow import Flow
from ..util.trace import Trace

class MultiThreadFlow(EventBasedFlow):
    def __init__(self, name=None, num_threads=2):
        super().__init__(name)
        self.threads = []
        self.num_threads = num_threads

    def start(self):
        with self._lock:
            if len(self.threads) != 0:
                return

            self._setup()
            self.cases.setup_with(self)

            for i in range(self.num_threads):
                thread = Thread(target=self)
                thread.setName("{} {}".format(self.name, i + 1))
                thread.start()
                self.threads.append(thread)

            self.queue.enqueue(FlowStart())

        Trace.debug("started flow '{}'", self.name)

    def stop(self):
        with self._lock:
            if len(self.threads) == 0:
                return

            self.queue.close(FlowStop())

            for thread in self.threads:
                thread.join()
            self.threads.clear()

            self.cases.teardown_with(self)
            self._teardown()

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

