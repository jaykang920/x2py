# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from .cell import MetaProperty, Cell
from .util.hash import hash_update

class Event(Cell):
    """ Common base class for all events. """

    class Tag(Cell.Tag):
        def __init__(self, base, type_name, props, type_id):
            super().__init__(base, type_name, props)
            self.type_id = type_id

    tag = Tag(None, 'Event', [
            MetaProperty('_Handle', MetaProperty.INT32)
        ], 0)

    def __init__(self, length=0):
        super().__init__(len(Event.tag.props) + length)
        base = Event.tag.offset
        self.values[base + 0] = 0

    @property
    def _handle(self):
        return self.values[Event.tag.offset + 0]
    @_handle.setter
    def _handle(self, value):
        self._set_property(Event.tag.offset + 0, value,
            Event.tag.props[0].type_index)

    def desc(self):
        prop_descs = []
        tag = self.type_tag()
        self._desc(tag, prop_descs)
        result = ', '.join(prop_descs)
        result = "{} {} {{ {} }}".format(tag.type_name, tag.type_id, result)
        return result

    def in_response_of(self, request):
        self._handle = request._handle
        return self

    def post(self):
        """ Posts up this event to the hub. """
        from .hub import Hub
        Hub.post(self)

    def type_id(self):
        return Event.tag.type_id

    def type_tag(self):
        return Event.tag

    def hash_code_for(self, fingerprint, type_id):
        value = self.hash_code(fingerprint)
        value = hash_update(value, -1)  # delimiter for type id
        value = hash_update(value, type_id)
        return value

    def __hash__(self):
        return self.hash_code_for(self.fingerprint, self.type_id())

class EventProxy:
    """ Supports dictionary search by equivalence. """

    def __init__(self):
        self.event = None
        self.fingerprint = None
        self.type_id = 0

    def equals(self, other):
        return self.event.equivalent(other)

    def __hash__(self):
        return self.event.hash_code_for(self.fingerprint, self.type_id)
