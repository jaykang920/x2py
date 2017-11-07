# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from .cell import Cell
from .util.hash import hash_update

class Event(Cell):
    """ Common base class for all events. """

    class Tag(Cell.Tag):
        def __init__(self, base, props, type_id):
            super().__init__(base, props)
            self.type_id = type_id

    tag = Tag(None, [], 0)

    def __init__(self, length=0):
        super().__init__(len(Event.tag.props) + length)

    def desc(self):
        prop_descs = []
        tag = self.type_tag()
        self._desc(tag, prop_descs)
        result = ', '.join(prop_descs)
        result = "{} {} {{ {} }}".format(type(self).__name__, tag.type_id, result)
        return result

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
