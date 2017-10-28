# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from bisect import bisect

from .fingerprint import Fingerprint
from .util.atomic import AtomicInt
from .util.rwlock import ReadLock, WriteLock, ReadWriteLock

def binary_search(a, x):
    index = bisect(a, x)
    if (index and a[index - 1] == x):
        return index - 1  # right-most index of the found
    else:
        return ~index  # insertion point

class Slot(Fingerprint):
    """ Extends Fingerprint to hold an additional reference count. """

    def __init__(self, fingerprint):
        super().__init__(fingerprint)
        self.ref_count = AtomicInt(1)

    def add_ref(self):
        self.ref_count.increment()

    def remove_ref(self):
        return self.ref_count.decrement()

class Binder:
    """ Manages evnet-handler bindings. """

    class _Filter:
        def __init__(self):
            self.map = {}

        def add(type_id, fingerprint):
            if type_id in self.map:
                slots = self.map[type_id]
            else:
                slots = []
                self.map[type_id] = slots
            slot = Slot(fingerprint)
            index = binary_search(slots, slot)
            if (index >= 0):
                slots[index].add_ref()
            else:
                index = ~index
                slots.insert(index, slot)

        def get(type_id):
            return self.map[type_id] if type_id in self.map else None

        def remove(type_id, fingerprint):
            if type_id not in self.map:
                return
            slots = self.map[type_id]
            index = binary_search(slots, Slot(fingerprint))
            if index < 0:
                return
            if (slots[index].remove_ref() == 0):
                del slots[index]
            if len(slots) == 0:
                del self.map[type_id]

    def __init__(self):
        self.map = {}
        self.filter = Binder._Filter()
        self.rwlock = ReadWriteLock()

    def bind(event, handler):
        pass
