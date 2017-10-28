# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from .cell import Cell
from .util.misc import hash_update

class Event(Cell):
    """ Common base class for all events. """

    class Tag(Cell.Tag):
        def __init__(self, base, runtime_type, num_props, type_id):
            super().__init__(base, runtime_type, num_props)
            self.type_id = type_id

    tag = Tag(None, 'Event', 0, 0)

    def __init__(self, length=0):
        super().__init__(Event.tag.num_props + length)

    def type_id(self):
        return Event.tag.type_id

    def equivalent(self, other):
        if not super().equivalent(other):
            return False
        return True

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return True

    def __hash__(self):
        value = super().__hash__()
        value = hash_update(value, self.type_id())
        return value
