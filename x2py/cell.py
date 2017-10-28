# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from .fingerprint import Fingerprint
from .util.misc import HASH_SEED, hash_update

class Cell(object):
    """ Common base class for all custom types. """

    class Tag:
        def __init__(self, base, runtime_type, num_props):
            self.base = base
            self.runtime_type = runtime_type
            self.num_props = num_props
            self.offset = 0
            if (base is not None):
                self.offset = base.offset + base.num_props

    tag = Tag(None, 'Cell', 0)

    def __init__(self, length):
        self.fingerprint = Fingerprint(length)

    def equivalent(self, other):
        if self is other:
            return True
        if not isinstance(self, type(other)):
            return False
        return True

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) != type(other):
            return False
        return True

    def __hash__(self):
        return HASH_SEED
