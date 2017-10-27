# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from threading import local

from .binder import Binder
from .case import CaseStack

class Flow:
    """ Represents a logically independent execution flow. """
    thraed_local = local()

    def __init__(self, name=None):
        self.name = name if name is not None else type(self).__name__
        self.cases = CaseStack()
        self.binder = Binder()

    def attach(self):
        from .hub import Hub
        Hub.instance.attach(self)
        return self

    def detach(self):
        from .hub import Hub
        Hub.instance.detach(self)
        return self

    def add(self, case):
        if cases.add(case):
            Trace.debug("flow '{}': added case '{}'", self.name, type(case).__name__)
        return self

    def remove(self, case):
        if cases.remove(case):
            Trace.debug("flow '{}': removed case '{}'", self.name, type(case).__name__)
        return self

    def dispatch(self, event):
        print("dispatching {}".format(event))

    def feed(self, event):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()
