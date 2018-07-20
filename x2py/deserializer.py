# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

import datetime
import struct

class Deserializer(object):
    """Binary wire format deserializer."""

    def read_bool(self, metaprop):
        self.check_length(1)
        b = self.buffer[self.pos]
        if isinstance(b, str):
            b = ord(b)
        self.pos += 1
        return True if b != 0 else False

    def read_byte(self, metaprop):
        self.check_length(1)
        b = self.buffer[self.pos]
        if isinstance(b, str):
            b = ord(b)
        self.pos += 1
        return b

    def read_int8(self, metaprop):
        self.check_length(1)
        offset = self.pos
        self.pos += 1
        return struct.unpack_from('b', self.buffer, offset)[0]

    def read_int16(self, metaprop):
        self.check_length(2)
        offset = self.pos
        self.pos += 2
        return struct.unpack_from('!h', self.buffer, offset)[0]

    def read_int32(self, metaprop):
        value, _ = self.read_variable32()
        value = (value >> 1) ^ -(value & 1)
        if value < -(2**31) or (2**31 - 1) < value:
            raise ValueError()
        return value

    def read_int64(self, metaprop):
        value, _ = self.read_variable64()
        value = (value >> 1) ^ -(value & 1)
        if value < -(2**63) or (2**63 - 1) < value:
            raise ValueError()
        return value

    def read_float32(self, metaprop):
        self.check_length(4)
        offset = self.pos
        self.pos += 4
        return struct.unpack_from('!f', self.buffer, offset)[0]

    def read_float64(self, metaprop):
        self.check_length(8)
        offset = self.pos
        self.pos += 8
        return struct.unpack_from('!d', self.buffer, offset)[0]

    def read_string(self, metaprop):
        length, _ = self.read_nonnegative()
        if length == 0:
            return ''
        temp = self.buffer[self.pos:self.pos + length]
        self.pos += length
        return temp.decode('utf-8')

    def read_datetime(self, metaprop):
        self.check_length(8)
        offset = self.pos
        self.pos += 8
        millisecs = struct.unpack_from('!q', self.buffer, offset)[0]
        unix_epoch = datetime.datetime(1970, 1, 1)
        return unix_epoch + datetime.timedelta(milliseconds=millisecs)

    def read_bytes(self, metaprop):
        length, _ = self.read_nonnegative()
        if length == 0:
            return None
        value = self.buffer[self.pos:self.pos + length]
        self.pos += length
        return value

    def read_cell(self, metaprop):
        from x2py.event import Event
        length, _ = self.read_nonnegative()
        if length == 0:
            return None
        temp = self.buffer[self.pos:self.pos + length]
        self.pos += length
        is_event = issubclass(metaprop.runtime_type, Event)
        if is_event:
            type_id = self.read_int32(None)
            value = EventFactory.create(type_id)
        else:
            value = metaprop.runtime_type()
        if value is not None:
            value.deserialize(Deserializer(temp))
        return value

    def read_list(self, metaprop):
        result = []
        length, _ = self.read_nonnegative()
        if length == 0:
            return result
        for i in range(length):
            result.append(self.read(metaprop.details[0]))
        return result

    def read_map(self, metaprop):
        result = {}
        length, _ = self.read_nonnegative()
        if length == 0:
            return result
        for i in range(length):
            key = self.read(metaprop.details[0])
            value = self.read(metaprop.details[1])
            result[key] = value
        return result

    # Reader function table
    readers = [
        None,
        read_bool,
        read_byte,
        read_int8,
        read_int16,
        read_int32,
        read_int64,
        read_float32,
        read_float64,
        read_string,
        read_datetime,
        read_bytes,
        read_cell,
        read_list,
        read_map,
        None  # none for object type
    ]

    def __init__(self, buffer=None):
        self.buffer = buffer
        if self.buffer is None:
            self.buffer = bytearray()
        self.pos = 0

    def read(self, metaprop):
        reader = Deserializer.readers[metaprop.type_index]
        return reader(self, metaprop)

    def read_nonnegative(self):
        value, num_bytes = Deserializer.read_variable32(self)
        if value < 0:
            raise ValueError()
        return value, num_bytes

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
            if isinstance(b, str):
                b = ord(b)
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
