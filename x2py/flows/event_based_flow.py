# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from threading import Lock

from ..event import Event
from ..event_queue import EventQueue
from ..flow import Flow

class EventBasedFlow(Flow):
    """ Abstract base class for event-based (waiting) execution flows. """

    def __init__(self, name=None):
        super().__init__(name)
        self.queue = EventQueue()
        self._lock = Lock()

    def feed(self, event):
        if (event is None or not isinstance(event, Event)):
            raise TypeError()
        self.queue.enqueue(event)