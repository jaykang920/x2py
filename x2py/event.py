# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from cell import Cell

class Event(Cell):
    """Common base class for all events."""

    class Tag(Cell.Tag):
        def __init__(self, base, runtime_type, num_props, type_id):
            super().__init__(base, runtime_type, num_props)
            self.type_id = type_id

    tag = Tag(None, 'Event', 0, 0)

    def __init__(self, length=0):
        super().__init__(Event.tag.num_props + length)