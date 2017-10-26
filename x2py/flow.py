# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

class Flow:
    """ Represents a logically independent execution flow. """

    def __init__(self, name=None):
        self.name = name if name is not None else type(self).__name__

    def attach(self):
        from .hub import Hub
        Hub.instance.attach(self)
        return self

    def detach(self):
        from .hub import Hub
        Hub.instance.detach(self)
        return self

    def dispatch(self, event):
        print("dispatching {}".format(event))

    def feed(self, event):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()
