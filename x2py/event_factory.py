# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

import inspect
import sys
import types

from x2py.event import Event
from x2py.util.trace import Trace

class EventFactory(object):
    _map = {}

    @staticmethod
    def create(type_id):
        factory_method = EventFactory._map.get(type_id)
        if (factory_method is None):
            Trace.warn("unknown event type id {}", type_id)
            return None
        return factory_method()

    @staticmethod
    def register(type_id, factory_method):
        if type_id == 0:  # ignore the root event
            return
        existing = EventFactory._map.get(type_id)
        if existing:
            if existing != factory_method:
                raise ValueError("event type id {} conflicted".format(type_id))
            return
        EventFactory._map[type_id] = factory_method

    @staticmethod
    def register_type(t):
        EventFactory.register(t.tag.type_id, t)

    @staticmethod
    def register_module(module, base_class=Event):
        predicate = lambda t: inspect.isclass(t) and issubclass(t, base_class)
        members = inspect.getmembers(module, predicate)
        for name, t in members:
            EventFactory.register_type(t)

    @staticmethod
    def register_package(module, base_class=Event):
        EventFactory.register_module(module, base_class)
        for name in dir(module):
            attr = getattr(module, name)
            if type(attr) == types.ModuleType:
                EventFactory.register_package(attr, base_class)
