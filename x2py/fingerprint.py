# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from array import array
from copy import copy

from .deserializer import Deserializer
from .serializer import Serializer
from .util.hash import HASH_SEED, hash_update

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

        self.length = length
        self.block = 0
        self.blocks = None

        if length > 32:
            length -= 32
            self.blocks = array('L', [0] * (((length - 1) >> 5) + 1))

    def _copy_ctor(self, other):
        self.length = other.length
        self.block = other.block
        if other.blocks is not None:
            self.blocks = copy(other.blocks)
        else:
            self.blocks = None

    @property
    def length_in_bytes(self):
        return ((self.length - 1) >> 3) + 1

    def get(self, index):
        """ Gets the bit value at the specified index. """
        if index < 0 or self.length <= index:
            raise ValueError()

        if index < 32:
            return ((self.block & (1 << (index & 0x1f))) != 0)
        else:
            index -= 32
            return ((self.blocks[index >> 5] & (1 << (index & 0x1f))) != 0)

    def touch(self, index):
        """ Sets the bit value at the specified index. """
        if index < 0:
            raise ValueError()
        # Allow over-indexing, returning False by default.
        if self.length <= index:
            return False

        if index < 32:
            self.block |= (1 << (index & 0x1f))
        else:
            index -= 32
            self.blocks[index >> 5] |= (1 << (index & 0x1f))

    def wipe(self, index):
        """ Clears the bit value at the specified index. """
        if index < 0 or self.length <= index:
            raise ValueError()

        if index < 32:
            self.block &= ~(1 << (index & 0x1f))
        else:
            index -= 32
            self.blocks[index >> 5] &= ~(1 << (index & 0x1f))

    def deserialize(self, deserializer):
        length, _ = deserializer.read_nonnegative()
        num_bytes = ((length - 1) >> 3) + 1
        num_blocks = ((num_bytes - 1) >> 2) + 1

        i = count = 0
        block = 0
        while i < 4 and count < num_bytes:
            b = deserializer.read_byte(None)
            if count < self.length_in_bytes:
                block = block | (b << (i << 3))
            i += 1
            count += 1
        self.block = block

        j = 0
        while j < num_blocks:
            i = 0
            block = 0
            while i < 4 and count < num_bytes:
                b = deserializer.read_byte(None)
                if count < self.length_in_bytes:
                    block = block | (b << (i << 3))
                i += 1
                count += 1
            if self.blocks is not None and j < len(self.blocks):
                self.blocks[j] = block
            j += 1

    def get_length(self):
        return Serializer.get_length_nonnegative(self.length) + self.length_in_bytes

    def serialize(self, serializer):
        serializer.write_nonnegative(self.length)

        i = count = 0
        while i < 4 and count < self.length_in_bytes:
            Serializer.write_byte(serializer.buffer, None, (self.block >> (i << 3)) & 0x0ff)
            i += 1
            count += 1

        if self.blocks is None:
            return

        for block in self.blocks:
            i = 0
            while i < 4 and count < self.length_in_bytes:
                Serializer.write_byte(serializer.buffer, None, (block >> (i << 3)) & 0x0ff)
                i += 1
                count += 1

    def equivalent(self, other):
        if self is other:
            return True
        if not isinstance(other, Fingerprint) or self.length < other.length:
            return False
        if (self.block & other.block) != other.block:
            return False
        if other.blocks is not None:
            count = len(other.blocks)
            i = 0
            while i < count:
                block = other.blocks[i]
                if (self.blocks[i] & block) != block:
                    return False
                i += 1
        return True

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

    def __hash__(self):
        value = hash_update(HASH_SEED, self.length)
        value = hash_update(value, self.block)
        if self.blocks is not None:
            for block in self.blocks:
                value = hash_update(value, block)
        return value

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
