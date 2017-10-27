# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from threading import Lock

class AtomicInt(object):
    def __init__(self, value=0):
        self._value = value
        self._lock = Lock()

    def decrement(self):
        with self._lock:
            self.value -= 1
            return self.value

    def increment(self):
        with self._lock:
            self.value += 1
            return self.value

    def get(self):
        with self._lock:
            return self._value

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, value):
        with self._lock:
            self._value = value
