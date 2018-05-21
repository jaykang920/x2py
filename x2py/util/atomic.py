# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from threading import Lock

class AtomicInt(object):
    def __init__(self, value=0):
        self._value = value
        self._lock = Lock()

    def decrement(self):
        with self._lock:
            self._value -= 1
            return self._value

    def increment(self):
        with self._lock:
            self._value += 1
            return self._value

    @property
    def value(self):
        with self._lock:
            return self._value

    @value.setter
    def value(self, val):
        with self._lock:
            self._value = val
