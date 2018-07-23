# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

import time
from threading import Lock, Thread

from x2py.event import Event
from x2py.event_queue import EventQueue
from x2py.flow import Flow
from x2py.util.atomic import AtomicInt
from x2py.util.trace import Trace

class Time(object):
    """Utility class to handle time information within a frame-based flow."""

    def __init__(self):
        pass

    def init(self):
        self.start_clock = Time.clock()
        self.last_clock = self.start_clock
        self.current_clock = self.last_clock
        self.delta_clock = 0.0

    def before_update(self):
        self.current_clock = Time.clock()
        self.delta_clock = self.current_clock - self.last_clock

    def after_update(self):
        self.last_clock = self.current_clock

    @staticmethod
    def clock():
        return time.clock()

class FrameBasedFlow(Flow):
    """Abstract base class for frame-based (looping) execution flows."""

    def __init__(self, name=None, with_queue=False):
        super(FrameBasedFlow, self).__init__(name)
        self.queue = None
        if with_queue:
            self.queue = EventQueue()
        self._lock = Lock()
        self.should_stop = AtomicInt()
        self.thread = None

        # Default resolution is 15.625ms (64 frame/sec)
        self.resolution = 0.015625

        self.time = Time()

    def feed(self, event):
        if self.queue is None:
            return
        if event is None or not isinstance(event, Event):
            raise TypeError()
        self.queue.enqueue(event)

    def start(self):
        with self._lock:
            if self.thread is not None:
                return

            self._setup()
            self.cases.setup_with(self)

            self.thread = Thread(target=self)
            if self.name is not None:
                self.thread.setName(self.name)
            self.thread.start()

            if self.queue is not None:
                self.queue.enqueue(FlowStart())

    def stop(self):
        with self._lock:
            if self.thread is None:
                return

            self.should_stop.value = 1
            if self.queue is not None:
                self.queue.close(FlowStop())

            self.thread.join()
            self.thread = None

            self.cases.teardown_with(self)
            self._teardown()

    def __call__(self):
        Flow.thread_local.current = self
        if self.queue is not None:
            Flow.thread_local.event_proxy = EventProxy()
            Flow.thread_local.handler_chain = []

        self._begin()

        while self.should_stop.value == 0:
            self._update()

            if self.queue is not None:
                while (Time.clock() - self.time.current_clock) < self.resolution:
                    event = self.queue.try_dequeue()
                    if event is not None:
                        self.dispatch(event)
                        if event.type_id() == BuiltinEventType.FLOW_STOP:
                            self.should_stop.value = 1
                            break
                    else:
                        if self.should_stop.value != 0:
                            break
                        else:
                            time.sleep(0.001)
                            continue
            else:
                clock_delta = Time.clock() - self.time.current_clock
                if clock_delta < self.resolution:
                    delay = self.resolution - clock_delta
                else:
                    delay = 0.0
                time.sleep(delay)

        self.end()

        if self.queue is not None:
            Flow.thread_local.handler_chain = None
            Flow.thread_local.event_proxy = None
        Flow.thread_local.current = None

    def _begin(self):
        self.time.init()
        self.begin()

    def _update(self):
        self.time.before_update()
        self.update()
        self.time.after_update()

    def begin(self):
        pass

    def end(self):
        pass

    def update(self):
        raise NotImplementedError()
