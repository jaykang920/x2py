# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

import sys
import traceback

from threading import local

from x2py.binder import Binder
from x2py.builtin_events import *
from x2py.case import Case, CaseStack
from x2py.util.trace import Trace

def _init():
    result = local()
    result.current = None
    return result

class Flow(object):
    """ Represents a logically independent execution flow. """
    thread_local = _init()

    def __init__(self, name=None):
        self.name = name if name is not None else type(self).__name__
        self.cases = CaseStack()
        self.binder = Binder()

    @staticmethod
    def bind(event, handler):
        return Flow.thread_local.current.subscribe(event, handler)

    @staticmethod
    def unbind(event, handler):
        Flow.thread_local.current.unsubscribe(event, handler)

    def attach(self):
        from x2py.hub import Hub
        Hub.instance.attach(self)
        return self

    def detach(self):
        from x2py.hub import Hub
        Hub.instance.detach(self)
        return self

    def add(self, case):
        if case is None or not isinstance(case, Case):
            raise TypeError()
        if self.cases.add(case):
            Trace.debug("flow '{}': added case '{}'", self.name, type(case).__name__)
        return self

    def remove(self, case):
        if case is None or not isinstance(case, Case):
            raise TypeError()
        if self.cases.remove(case):
            Trace.debug("flow '{}': removed case '{}'", self.name, type(case).__name__)
        return self

    def dispatch(self, event):
        event_proxy = Flow.thread_local.event_proxy
        handler_chain = Flow.thread_local.handler_chain

        if len(handler_chain) != 0:
            del handler_chain[:]

        self.binder.build_handler_chain(event, event_proxy, handler_chain)

        for handler in handler_chain:
            try:
                handler(event)
            except Exception as ex:
                Trace.error("flow: dispatch {}".format(ex))
                traceback.print_exc(file=sys.stderr)

        del handler_chain[:]

    def feed(self, event):
        raise NotImplementedError()

    def on_start(self, event):
        pass

    def on_stop(self, event):
        pass

    def _setup(self):
        """ Called internally when this flow starts up. """

        self.subscribe(FlowStart(), self.on_start)
        self.subscribe(FlowStop(), self.on_stop)

        self.setup()

    def setup(self):
        """ Overridden by subclasses to build a flow startup handler chain. """
        pass

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def _teardown(self):
        """ Called internally when this flow shuts down. """
        self.teardown()

        self.subscribe(FlowStop(), self.on_stop)
        self.subscribe(FlowStart(), self.on_start)

    def teardown(self):
        """ Overridden by subclasses to build a flow shutdown handler chain. """
        pass

    def subscribe(self, event, handler):
        return self.binder.bind(event, handler)

    def _unsubscribe(self, event, handler):
        self.binder._unbind(event, handler)

    def unsubscribe(self, event, handler):
        self.binder.unbind(event, handler)
