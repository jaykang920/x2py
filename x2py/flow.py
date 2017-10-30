# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from threading import local

from .binder import Binder
from .case import CaseStack
from .util.trace import Trace

def _init():
    result = local()
    result.current = None
    return result

class Flow:
    """ Represents a logically independent execution flow. """
    thread_local = _init()

    def __init__(self, name=None):
        self.name = name if name is not None else type(self).__name__
        self.cases = CaseStack()
        self.binder = Binder()

    @staticmethod
    def bind(event, handler):
        Flow.thread_local.current.subscribe(event, handler)

    @staticmethod
    def unbind(event, handler):
        Flow.thread_local.current.unsubscribe(event, handler)

    def attach(self):
        from .hub import Hub
        Hub.instance.attach(self)
        return self

    def detach(self):
        from .hub import Hub
        Hub.instance.detach(self)
        return self

    def add(self, case):
        if self.cases.add(case):
            Trace.debug("flow '{}': added case '{}'", self.name, type(case).__name__)
        return self

    def remove(self, case):
        if self.cases.remove(case):
            Trace.debug("flow '{}': removed case '{}'", self.name, type(case).__name__)
        return self

    def dispatch(self, event):
        print("dispatching {}".format(event))

        event_proxy = Flow.thread_local.event_proxy
        handler_chain = Flow.thread_local.handler_chain

        if len(handler_chain) != 0:
            handler_chain.clear()

        self.binder.build_handler_chain(event, event_proxy, handler_chain)

        for handler in handler_chain:
            try:
                handler(event)
            except BaseException as ex:
                # log
                pass

        handler_chain.clear()

    def feed(self, event):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def subscribe(self, event, handler):
        self.binder.bind(event, handler)

    def unsubscribe(self, event, handler):
        self.binder.unbind(event, handler)
