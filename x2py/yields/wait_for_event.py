# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from datetime import timedelta

from x2py.builtin_events import TimeoutEvent
from x2py.config import Config
from x2py.flow import Flow
from x2py.flows.time_flow import TimeFlow
from x2py.util.trace import Trace
from x2py.yields.wait_handle_pool import WaitHandlePool

class WaitForEvent(object):
    def __init__(self, coroutine, e, seconds=Config.Coroutine.default_timeout):
        self.coroutine = coroutine
        self.handler_token = Flow.bind(e, self.on_event)
        self.timerout_token = None
        self.timer_token = None
        if seconds > 0:
            timeout_event = TimeoutEvent().setattrs(key=self)
            self.timeout_token = Flow.bind(timeout_event, self.on_timeout)
            self.timer_token = TimeFlow.get().reserve(timeout_event, timedelta(seconds=seconds))

    def on_event(self, e):
        Flow.unbind_with(self.handler_token)

        if self.timer_token:
            TimeFlow.get().cancel(self.timer_token)
            Flow.unbind_with(self.timeout_token)

        wait_handle = self.handler_token[0]._wait_handle
        if wait_handle:
            WaitHandlePool.release(wait_handle)

        coroutine.result = e
        coroutine.next()

    def on_timeout(self, e):
        Flow.unbind_with(self.handler_token)
        Flow.unbind_with(self.timeout_token)

        wait_handle = self.handler_token[0]._wait_handle
        if wait_handle:
            WaitHandlePool.release(wait_handle)

        Trace.error("WaitForEvent timeout for {}".format(self.handler_token[0]))

        self.coroutine.result = None
        self.coroutine.next()

class WaitForResponse(WaitForEvent):
    def __init__(self, coroutine, req, e, seconds=Config.Coroutine.default_timeout):
        wait_handle = WaitHandlePool.acquire()
        req._wait_handle = wait_handle
        e._wait_handle = wait_handle

        super(WaitForResponse, self).__init__(coroutine, e, seconds)

        req.post()
