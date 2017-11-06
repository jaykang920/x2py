# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from .event import Event

class EventFactory:
    map = {}

    @staticmethod
    def create(type_id):
        factory_method = EventFactory.map.get(type_id)
        if (factory_method is None):
            return None
        return factory_method()

    @staticmethod
    def register(type_id, factory_method):
        EventFactory.map[type_id] = factory_method