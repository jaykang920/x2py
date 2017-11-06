# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

class Deserializer:
    def read_bool(self, prop_name, pos):
        self.check_length(1)
        b = self.buffer[self.pos]
        self.pos += 1
        return True if b != 0 else False

    def read_byte(self, prop_name):
        self.check_length(1)
        b = self.buffer[self.pos]
        self.pos += 1
        return b

    def read_int32(self, prop_name):
        value, _ = self.read_variable32()
        value = (value >> 1) ^ -(value & 1)
        if value < -(2**31) or (2**31 - 1) < value:
            raise ValueError()
        return value

    def read_variable32(self):
        value = 0
        i = shift = 0
        while i < 5:
            self.check_length(1)
            b = self.buffer[self.pos]
            self.pos += 1
            value = value | ((b & 0x7f) << shift)
            if (b & 0x80) == 0:
                break
            i += 1
            shift += 7
        return value, min(i + 1, 5)

    def check_length(self, num_bytes):
        if (self.pos + num_bytes) > len(self.buffer):
            raise EOFError()

    readers = [ None, read_bool, read_byte, None, None, read_int32 ]

    def __init__(self, buffer=None):
        self.buffer = buffer
        if self.buffer is None:
            self.buffer = bytearray()
        self.pos = 0

    def read(self, prop):
        reader = Deserializer.readers[prop[1]]
        return reader(self, prop[0])

    def read_nonnegative(self):
        value, num_bytes = Deserializer.read_variable32(self)
        if value < 0:
            raise ValueError()
        return value, num_bytes
