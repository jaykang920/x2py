# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from threading import Lock

from .case import Case

class Link(Case):
    names = set()
    _lock = Lock()

    def __init__(self, name):
        super().__init__()
        # buffer transform
        with Link._lock:
            if name in Link.names:
                raise ValueError("link name '{}' is already in use".format(name))
            self._name = name
            Link.names.add(name)

    @property
    def name(self):
        return self._name

    def cleanup(self):
        # buffer transform
        with Link._lock:
            if self.name in Link.names:
                Link.names.remove(self.name)

    def close(self):
        self.cleanup()

    def send(self, event):
        raise NotImplementedError()

    def _teardown(self):
        self.close()
        super()._teardown()