# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

import inspect
import sys
import types

from x2py.event import Event
from x2py.util.trace import Trace

class EventFactory(object):
    """Manages a map of retrievable event type identifiers and their factory
        methods."""

    class _EventFactory(object):
        def __init__(self):
            self._map = {}

        def create(self, type_id):
            factory_method = self._map.get(type_id)
            if (factory_method is None):
                Trace.warn("unknown event type id {}", type_id)
                return None
            return factory_method()

        def register(self, type_id, factory_method):
            if type_id == 0:  # ignore the root event
                return
            existing = self._map.get(type_id)
            if existing:
                if existing != factory_method:
                    raise ValueError("event type id {} conflicted".format(type_id))
                return
            self._map[type_id] = factory_method

        def register_type(self, t):
            EventFactory.register(t.tag.type_id, t)

        def register_module(self, module, base_class=Event):
            predicate = lambda t: inspect.isclass(t) and issubclass(t, base_class)
            members = inspect.getmembers(module, predicate)
            for name, t in members:
                EventFactory.register_type(t)

        def register_package(self, module, base_class=Event):
            EventFactory.register_module(module, base_class)
            for name in dir(module):
                attr = getattr(module, name)
                if type(attr) == types.ModuleType:
                    EventFactory.register_package(attr, base_class)

    instance = _EventFactory()

    def __init__(self):
        raise AssertionError()

    @staticmethod
    def new():
        return EventFactory._EventFactory()

    @staticmethod
    def create(type_id):
        return EventFactory.instance.create(type_id)

    @staticmethod
    def register(type_id, factory_method):
        EventFactory.instance.register(type_id, factory_method)

    @staticmethod
    def register_type(t):
        EventFactory.instance.register_type(t)

    @staticmethod
    def register_module(module, base_class=Event):
        EventFactory.instance.register_module(module, base_class)

    @staticmethod
    def register_package(module, base_class=Event):
        EventFactory.instance.register_package(module, base_class)
