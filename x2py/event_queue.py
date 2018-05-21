# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from collections import deque
from threading import Condition, Lock

from x2py.event import Event

class EventQueue(object):
    """ The blocking event queue implementation. """

    def __init__(self):
        self._deque = deque()
        self._closed = False
        self._lock = Lock()
        self._cond = Condition(self._lock)

    def close(self, final_event=None):
        with self._cond:
            if final_event is not None:
                self._deque.append(final_event)
            self._closed = True
            self._cond.notify_all()

    def dequeue(self):
        with self._cond:
            while len(self._deque) == 0:
                if self._closed:
                    return None
                self._cond.wait()
            return self._deque.popleft()

    def enqueue(self, event):
        with self._cond:
            if self._closed:
                return
            self._deque.append(event)
            if len(self._deque) == 1:
                self._cond.notify()

    def try_dequeue(self):
        with self._lock:
            if self._closed:
                return None
            return self._deque.popleft() if len(self._deque) != 0 else None
