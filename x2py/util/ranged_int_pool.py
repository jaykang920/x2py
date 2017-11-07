# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from array import array
from threading import Lock

class RangedIntPool:
    def __init__(self, min_value, max_value, advancing=False):
        self._min_value = min_value
        self._max_value = max_value
        self._advancing = advancing
        self._offset = 0
        self._blocks = array('L', [0] * (((max_value - min_value) >> 5) + 1))
        self._lock = Lock()

    def acquire(self):
        with self._lock:
            index = self._offset
            length = self._max_value - self._min_value + 1
            i = 0
            while i < length:
                if (index >= length):
                    index = 0
                if not self._get(index):
                    self._set(index, True)
                    if self._advancing:
                        self._offset = index + 1
                        if (self._offset >= length):
                            self._offset = 0
                    return self._min_value + index
                i += 1
                index += 1
            raise ResourceWarning()

    def claim(self, value):
        if value < self._min_value or self._max_value < value:
            raise ValueError()
        index = value - self._min_value
        with self._lock:
            if (self._get(index)):
                return False
            self._set(index, True)
        return True

    def release(self, value):
        if value < self._min_value or self._max_value < value:
            raise ValueError()
        index = value - self._min_value
        with self._lock:
            self._set(index, False)

    def _get(self, index):
        return ((self._blocks[index >> 5] & (1 << (index & 0x1f))) != 0)

    def _set(self, index, flag):
        if flag:
            self._blocks[index >> 5] |= (1 << (index & 0x1f))
        else:
            self._blocks[index >> 5] &= ~(1 << (index & 0x1f))
