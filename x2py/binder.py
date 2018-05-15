# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from bisect import bisect

from .event import Event, EventProxy
from .fingerprint import Fingerprint
from .util.atomic import AtomicInt
from .util.rwlock import ReadLock, WriteLock, ReadWriteLock

def binary_search(a, x):
    index = bisect(a, x)
    if index and (a[index - 1] == x):
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

class Binder(object):
    """ Manages evnet-handler bindings. """

    class _Filter(object):
        def __init__(self):
            self.map = {}

        def add(self, type_id, fingerprint):
            slots = self.map.get(type_id)
            if slots is None:
                slots = []
                self.map[type_id] = slots
            slot = Slot(fingerprint)
            index = binary_search(slots, slot)
            if index >= 0:
                slots[index].add_ref()
            else:
                index = ~index
                slots.insert(index, slot)

        def get(self, type_id):
            return self.map.get(type_id)

        def remove(self, type_id, fingerprint):
            slots = self.map.get(type_id)
            if slots is None:
                return
            index = binary_search(slots, Slot(fingerprint))
            if index < 0:
                return
            if slots[index].remove_ref() == 0:
                del slots[index]
            if len(slots) == 0:
                del self.map[type_id]

    def __init__(self):
        self.map = {}  # event => list of handlers
        self.filter = Binder._Filter()
        self.rwlock = ReadWriteLock()

    def bind(self, event, handler):
        with self.rwlock.wlock():
            handlers = self.map.get(event)
            if handlers is None:
                handlers = []
                self.map[event] = handlers

            token = (event, handler)
            if handler not in handlers:
                handlers.append(handler)
                self.filter.add(event.type_id(), event.fingerprint)

                if hasattr(handler, '__self__'):
                    from .event_sink import EventSink
                    target = handler.__self__
                    if isinstance(target, EventSink):
                        target._add_binding(token)
            return token

    def _unbind_(self, event, handler):
        handlers = self.map.get(event)
        if handler is None:
            return
        if handler not in handlers:
            return
        handlers.remove(handler)
        if len(handlers) == 0:
            del self.map[event]
        self.filter.remove(event.type_id(), event.fingerprint)

    def _unbind(self, event, handler):
        with self.rwlock.wlock():
            self._unbind_(event, handler)

    def unbind(self, event, handler):
        with self.rwlock.wlock():
            self._unbind_(event, handler)

            if hasattr(handler, '__self__'):
                from .event_sink import EventSink
                target = handler.__self__
                if isinstance(target, EventSink):
                    target._remove_binding((event, handler))

    def build_handler_chain(self, event, event_proxy, handler_chain):
        event_proxy.event = event
        tag = event.type_tag()
        fingerprint = event.fingerprint
        with self.rwlock.rlock():
            while tag is not None:
                type_id = tag.type_id
                event_proxy.type_id = type_id
                slots = self.filter.get(type_id)
                if slots is not None:
                    for slot in slots:
                        if fingerprint.equivalent(slot):
                            event_proxy.fingerprint = slot

                            handlers = self.map.get(event_proxy)
                            if handlers is not None:
                                handler_chain += handlers
                tag = tag.base

