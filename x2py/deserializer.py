# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import datetime
import struct

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

    def read_int8(self, prop_name):
        self.check_length(1)
        b = self.buffer[self.pos:self.pos + 1]
        self.pos += 1
        return int.from_bytes(b, 'big', signed=True)

    def read_int16(self, prop_name):
        self.check_length(2)
        b = self.buffer[self.pos:self.pos + 2]
        self.pos += 2
        return int.from_bytes(b, 'big', signed=True)

    def read_int32(self, prop_name):
        value, _ = self.read_variable32()
        value = (value >> 1) ^ -(value & 1)
        if value < -(2**31) or (2**31 - 1) < value:
            raise ValueError()
        return value

    def read_int64(self, prop_name):
        value, _ = self.read_variable64()
        value = (value >> 1) ^ -(value & 1)
        if value < -(2**63) or (2**63 - 1) < value:
            raise ValueError()
        return value

    def read_float32(self, prop_name):
        self.check_length(4)
        b = self.buffer[self.pos:self.pos + 4]
        self.pos += 4
        return struct.unpack('f', b)[0]

    def read_float64(self, prop_name):
        self.check_length(8)
        b = self.buffer[self.pos:self.pos + 8]
        self.pos += 8
        return struct.unpack('d', b)[0]

    def read_string(self, prop_name):
        length, _ = self.read_nonnegative()
        if length == 0:
            return ''
        temp = self.buffer[self.pos:self.pos + length]
        self.pos += length
        return temp.decode('utf-8')

    def read_datetime(self, prop_name):
        self.check_length(8)
        b = self.buffer[self.pos:self.pos + 8]
        self.pos += 8
        millisecs = int.from_bytes(b, 'big', signed=True)
        unix_epoch = datetime.datetime(1970, 1, 1)
        return unix_epoch + datetime.timedelta(milliseconds=millisecs)

    def read_variable32(self):
        return self._read_variable(5)

    def read_variable64(self):
        return self._read_variable(10)

    def _read_variable(self, max_bytes):
        value = 0
        i = shift = 0
        while i < max_bytes:
            self.check_length(1)
            b = self.buffer[self.pos]
            self.pos += 1
            value = value | ((b & 0x7f) << shift)
            if (b & 0x80) == 0:
                break
            i += 1
            shift += 7
        return value, min(i + 1, max_bytes)

    def check_length(self, num_bytes):
        if (self.pos + num_bytes) > len(self.buffer):
            raise EOFError()

    readers = [ None, read_bool, read_byte, read_int8, read_int16, read_int32, read_int64, read_float32, read_float64,
        read_string, read_datetime ]

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
