# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from array import array
from copy import copy

class Fingerprint:
    """ Manages a fixed-length compact array of bit values.
        (zero-based indexing) """

    def __init__(self, arg):
        if isinstance(arg, int):
            self._ctor(arg)
        elif isinstance(arg, Fingerprint):
            self._copy_ctor(arg)
        else:
            raise TypeError()

    def _ctor(self, length):
        if length < 0:
            raise ValueError()

        self.block = 0
        self.blocks = None
        self.length = length

        if length > 32:
            length -= 32
            self.blocks = array('L', [0] * (((length - 1) >> 5) + 1))

    def _copy_ctor(self, other):
        self.block = other.block
        if other.blocks is not None:
            self.blocks = copy(other.blocks)
        self.length = other.length

    def get(self, index):
        """ Gets the bit value at the specified index. """
        if index < 0 or self.length <= index:
            raise ValueError()

        if index < 32:
            return ((self.block & (1 << index)) != 0)
        else:
            index -= 32
            return ((self.blocks[index >> 5] & (1 << index)) != 0)

    def touch(self, index):
        """ Sets the bit value at the specified index. """
        if index < 0 or self.length <= index:
            raise ValueError()

        if index < 32:
            self.block |= (1 << index)
        else:
            index -= 32
            self.blocks[index >> 5] |= (1 << index)

    def wipe(self, index):
        """ Clears the bit value at the specified index. """
        if index < 0 or self.length <= index:
            raise ValueError()

        if index < 32:
            self.block &= ~(1 << index)
        else:
            index -= 32
            self.blocks[index >> 5] &= ~(1 << index)

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Fingerprint) or self.length != other.length:
            return False
        if self.block != other.block:
            return False
        if self.blocks is not None:
            count = len(self.blocks)
            i = 0
            while i < count:
                if self.blocks[i] != other.blocks[i]:
                    return False
                i += 1
        return True

    def __lt__(self, other):
        if self is other:
            return False
        if self.length < other.length:
            return True
        if self.length > other.length:
            return False
        # assert self.length == other.length
        if self.blocks is not None:
            i = len(self.blocks) - 1
            while i >= 0:
                block = self.blocks[i]
                other_block = other.blocks[i]
                if block < other_block:
                    return True
                if block > other_block:
                    return False
                i -= 1
        if self.block >= other.block:
            return False
        return True
