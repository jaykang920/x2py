# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

class Serializer:
    @staticmethod
    def len_bool(value):
        return 1

    @staticmethod
    def len_byte(value):
        return 1

    @staticmethod
    def len_int32(value):
        return Serializer.len_variable32(value)

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
    def write_bool(buffer, prop_name, value):
        if value:
            buffer.append(1)
        else:
            buffer.append(0)

    @staticmethod
    def write_byte(buffer, prop_name, value):
        if value < -(2**8) or (2**8 - 1) < value:
            raise ValueError()
        buffer.append(value)

    @staticmethod
    def write_int32(buffer, prop_name, value):
        if value < -(2**31) or (2**31 - 1) < value:
            raise ValueError()
        value = (value << 1) ^ (value >> 31)
        Serializer.write_variable32(buffer, value)

    @staticmethod
    def write_variable32(buffer, value):
        while True:
            b = value & 0x7f
            value = value >> 7
            if value != 0:
                b = b | 0x80
            buffer.append(b)
            if value == 0:
                break

    len_funcs = [ None, len_bool, len_byte, None, None, len_int32 ]
    writers = [ None, write_bool, write_byte, None, None, write_int32 ]

    def __init__(self, buffer=None):
        self.buffer = buffer
        if self.buffer is None:
            self.buffer = bytearray()

    @staticmethod
    def get_length(type_index, value):
        len_func = Serializer.len_funcs[type_index]
        return len_func.__func__(value)

    def write(self, prop, value):
        writer = Serializer.writers[prop[1]]
        writer.__func__(self.buffer, prop[0], value)

    @staticmethod
    def get_length_nonnegative(value):
        if value < 0:
            raise ValueError()
        return Serializer.len_variable32(value)

    def write_nonnegative(self, value):
        if value < 0:
            raise ValueError()
        Serializer.write_variable32(self.buffer, value)
