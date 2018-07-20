# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from threading import Lock

from x2py.case import Case
from x2py.event_factory import EventFactory

class Link(Case):
    """Common abstract base class for link cases."""

    names = set()
    _lock = Lock()

    def __init__(self, name):
        super(Link, self).__init__()
        self.event_factory = EventFactory.new()
        self.buffer_transform = None
        with Link._lock:
            if name in Link.names:
                raise ValueError("link name '{}' is already in use".format(name))
            self._name = name
            Link.names.add(name)

    @property
    def name(self):
        return self._name

    def cleanup(self):
        if self.buffer_transform is not None:
            self.buffer_transform.cleanup()
            self.buffer_transform = None

        with Link._lock:
            if self.name in Link.names:
                Link.names.remove(self.name)

    def close(self):
        self.cleanup()

    def create_event(self, type_id):
        # Try link-local event factory first.
        result = self.event_factory.create(type_id)
        if result:
            return result
        # If not fount, try the global event factory.
        return EventFactory.create(type_id)

    def send(self, event):
        raise NotImplementedError()

    def _teardown(self):
        self.close()
        super(Link, self)._teardown()
