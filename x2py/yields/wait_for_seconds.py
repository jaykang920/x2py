# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from datetime import timedelta

from x2py.builtin_events import TimeoutEvent
from x2py.flow import Flow
from x2py.flows.time_flow import TimeFlow

class WaitForSeconds(object):
    def __init__(self, coroutine, seconds):
        self.coroutine = coroutine
        e = TimeoutEvent().setattrs(key=self)
        self.token = Flow.bind(e, self.on_timeout)
        TimeFlow.get().reserve(e, timedelta(seconds=seconds))

    def on_timeout(self, e):
        Flow.unbind_with(self.token)
        self.coroutine.result = e
        self.coroutine.next()

class WaitForNothing(object):
    def __init__(self, coroutine, result):
        self.coroutine = coroutine
        self.result = result
        e = TimeoutEvent().setattrs(key=self)
        self.token = Flow.bind(e, self.on_event)
        e.post()

    def on_event(self, e):
        Flow.unbind_with(self.token)
        self.coroutine.result = self.result
        self.coroutine.next()
