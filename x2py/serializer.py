# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import datetime
import struct

class Serializer:
    @staticmethod
    def len_bool(metaprop, value):
        return 1

    @staticmethod
    def len_byte(metaprop, value):
        return 1

    @staticmethod
    def len_int8(metaprop, value):
        return 1

    @staticmethod
    def len_int16(metaprop, value):
        return 2

    @staticmethod
    def len_int32(metaprop, value):
        return Serializer.len_variable32(value)

    @staticmethod
    def len_int64(metaprop, value):
        return Serializer.len_variable64(value)

    @staticmethod
    def len_float32(metaprop, value):
        return 4

    @staticmethod
    def len_float64(metaprop, value):
        return 8

    @staticmethod
    def len_string(metaprop, value):
        if not isinstance(value, str):
            raise ValueError()
        length = Serializer.len_utf8(value)
        return Serializer.get_length_nonnegative(length) + length

    @staticmethod
    def len_utf8(value):
        length = 0
        if value is not None:
            for char in value:
                c = ord(char)
                if (c & 0xff80) == 0:
                    length += 1
                elif (c & 0xf800) != 0:
                    length += 3
                else:
                    length += 2
        return length

    @staticmethod
    def len_datetime(metaprop, value):
        return 8

    @staticmethod
    def len_bytes(metaprop, value):
        length = 0 if value is None else len(value)
        return Serializer.get_length_nonnegative(length) + length

    @staticmethod
    def len_cell(metaprop, value):
        not_none = (value is not None)
        partial = not_none and metaprop.runtime_type != type(value)
        if not_none:
            if partial:
                length = value.get_length(metaprop.runtime_type)
            else:
                length = value.get_length()
        else:
            length = 0
        return Serializer.get_length_nonnegative(length) + length

    @staticmethod
    def len_list(metaprop, value):
        is_none = (value is None)
        length = 0 if is_none else len(value)
        result = Serializer.get_length_nonnegative(length)
        for v in value:
            result += Serializer.get_length(metaprop.details[0], v)
        return result

    @staticmethod
    def len_map(metaprop, value):
        is_none = (value is None)
        length = 0 if is_none else len(value)
        result = Serializer.get_length_nonnegative(length)
        for k, v in value.items():
            result += Serializer.get_length(metaprop.details[0], k)
            result += Serializer.get_length(metaprop.details[1], v)
        return result

    @staticmethod
    def len_variable32(value):
        if (value & 0xffffff80) == 0:
            return 1
        if (value & 0xffffc000) == 0:
            return 2
        if (value & 0xffe00000) == 0:
            return 3
        if (value & 0xf0000000) == 0:
            return 4
        return 5

    @staticmethod
    def len_variable64(value):
        if (value & 0xffffffffffffff80) == 0:
            return 1
        if (value & 0xffffffffffffc000) == 0:
            return 2
        if (value & 0xffffffffffe00000) == 0:
            return 3
        if (value & 0xfffffffff0000000) == 0:
            return 4
        if (value & 0xfffffff800000000) == 0:
            return 5
        if (value & 0xfffffc0000000000) == 0:
            return 6
        if (value & 0xfffe000000000000) == 0:
            return 7
        if (value & 0xff00000000000000) == 0:
            return 8
        if (value & 0x8000000000000000) == 0:
            return 9
        return 10

    def write_bool(self, metaprop, value):
        if value:
            self.buffer.append(1)
        else:
            self.buffer.append(0)

    def write_byte(self, metaprop, value):
        if value < 0 or (2**8 - 1) < value:
            raise ValueError()
        self.buffer.append(value)

    def write_int8(self, metaprop, value):
        if value < -(2**7) or (2**7 - 1) < value:
            raise ValueError()
        self.buffer += value.to_bytes(1, 'big', signed=True)

    def write_int16(self, metaprop, value):
        if value < -(2**15) or (2**15 - 1) < value:
            raise ValueError()
        self.buffer += value.to_bytes(2, 'big', signed=True)

    def write_int32(self, prop_name, value):
        if value < -(2**31) or (2**31 - 1) < value:
            raise ValueError()
        value = (value << 1) ^ (value >> 31)
        Serializer.write_variable(self.buffer, value)

    def write_int64(self, prop_name, value):
        if value < -(2**63) or (2**63 - 1) < value:
            raise ValueError()
        value = (value << 1) ^ (value >> 63)
        Serializer.write_variable(self.buffer, value)

    def write_float32(self, metaprop, value):
        self.buffer += struct.pack('f', value)

    def write_float64(self, metaprop, value):
        self.buffer += struct.pack('d', value)

    def write_string(self, metaprop, value):
        if not isinstance(value, str):
            raise ValueError()
        # utf-8 encoding
        length = Serializer.len_utf8(value)
        Serializer.write_variable(self.buffer, length)  # write_nonnegative
        if length == 0:
            return
        for char in value:
            c = ord(char)
            if (c & 0xff80) == 0:
                self.buffer.append(c & 0x0ff)
            elif (c & 0xf800) != 0:
                self.buffer.append(0x0e0 | ((c >> 12) & 0x0f))
                self.buffer.append(0x080 | ((c >> 6) & 0x3f))
                self.buffer.append(0x080 | ((c >> 0) & 0x3f))
            else:
                self.buffer.append(0x0c0 | ((c >> 6) & 0x1f))
                self.buffer.append(0x080 | ((c >> 0) & 0x3f))

    def write_datetime(self, metaprop, value):
        if not isinstance(value, datetime.datetime):
            raise ValueError()
        unix_epoch = datetime.datetime(1970, 1, 1)
        millisecs = int((value - unix_epoch).total_seconds() * 1000)
        self.buffer += millisecs.to_bytes(8, 'big', signed=True)

    def write_bytes(self, metaprop, value):
        is_none = (value is None)
        length = 0 if is_none else len(value)
        Serializer.write_variable(self.buffer, length)  # write_nonnegative
        if is_none:
            return
        self.buffer += value

    def write_cell(self, metaprop, value):
        not_none = (value is not None)
        partial = not_none and metaprop.runtime_type != type(value)
        if not_none:
            if partial:
                length = value.get_length(metaprop.runtime_type)
            else:
                length = value.get_length()
        else:
            length = 0
        Serializer.write_variable(self.buffer, length)  # write_nonnegative
        if not_none:
            if partial:
                value.serialize(self, metaprop.runtime_type)
            else:
                value.serialize(self)

    def write_list(self, metaprop, value):
        is_none = (value is None)
        length = 0 if is_none else len(value)
        Serializer.write_variable(self.buffer, length)  # write_nonnegative
        if is_none:
            return
        for v in value:
            self.write(metaprop.details[0], v)

    def write_map(self, metaprop, value):
        is_none = (value is None)
        length = 0 if is_none else len(value)
        Serializer.write_variable(self.buffer, length)  # write_nonnegative
        if is_none:
            return
        for k, v in value.items():
            self.write(metaprop.details[0], k)
            self.write(metaprop.details[1], v)

    @staticmethod
    def write_variable(buffer, value):
        while True:
            b = value & 0x7f
            value = value >> 7
            if value != 0:
                b = b | 0x80
            buffer.append(b)
            if value == 0:
                break

    len_funcs = [ None, len_bool, len_byte, len_int8, len_int16, len_int32, len_int64, len_float32, len_float64,
        len_string, len_datetime, len_bytes, len_cell, len_list, len_map, None ]
    writers = [ None, write_bool, write_byte, write_int8, write_int16, write_int32, write_int64, write_float32, write_float64,
        write_string, write_datetime, write_bytes, write_cell, write_list, write_map, None ]

    def __init__(self, buffer=None):
        self.buffer = buffer
        if self.buffer is None:
            self.buffer = bytearray()

    @staticmethod
    def get_length(metaprop, value):
        len_func = Serializer.len_funcs[metaprop.type_index]
        return len_func.__func__(metaprop, value)

    def write(self, metaprop, value):
        writer = Serializer.writers[metaprop.type_index]
        writer(self, metaprop, value)

    @staticmethod
    def get_length_nonnegative(value):
        if value < 0:
            raise ValueError()
        return Serializer.len_variable32(value)

    def write_nonnegative(self, value):
        if value < 0:
            raise ValueError()
        Serializer.write_variable(self.buffer, value)
