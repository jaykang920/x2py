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
    def len_string(value):
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
    def write_string(buffer, prop_name, value):
        if not isinstance(value, str):
            raise ValueError()
        # utf-8 encoding
        length = Serializer.len_utf8(value)
        Serializer.write_variable32(buffer, length)  # write_nonnegative
        if length == 0:
            return
        for char in value:
            c = ord(char)
            if (c & 0xff80) == 0:
                buffer.append(c & 0x0ff)
            elif (c & 0xf800) != 0:
                buffer.append(0x0e0 | ((c >> 12) & 0x0f))
                buffer.append(0x080 | ((c >> 6) & 0x3f))
                buffer.append(0x080 | ((c >> 0) & 0x3f))
            else:
                buffer.append(0x0c0 | ((c >> 6) & 0x1f))
                buffer.append(0x080 | ((c >> 0) & 0x3f))

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

    len_funcs = [ None, len_bool, len_byte, None, None, len_int32, None, None, None,
        len_string ]
    writers = [ None, write_bool, write_byte, None, None, write_int32, None, None, None,
        write_string ]

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
