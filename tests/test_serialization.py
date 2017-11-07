# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys

import pytest

sys.path.append('..')
import x2py

from x2py.deserializer import Deserializer
from x2py.serializer import Serializer

def test_byte():
    buffer = bytearray()
    d = Deserializer(buffer)
    for test_value in [0, 1, 0x07f, 0x080, 0x0ff ]:
        Serializer.write_byte(buffer, None, test_value)
        value = d.read_byte(None)
        assert value == test_value

def test_int32():
    buffer = bytearray()
    d = Deserializer(buffer)
    for test_value in [0, 1, 0x07f, 0x080, 0x03fff, 0x0400 ]:
        Serializer.write_int32(buffer, None, test_value)
        value = d.read_int32(None)
        assert value == test_value

def test_nonnegative():
    s = Serializer()
    assert(len(s.buffer) == 0)
    s.write_nonnegative(0)
    assert(len(s.buffer) == 1)
    d = Deserializer(s.buffer)
    v, n = d.read_nonnegative()
    assert(v == 0)
    assert(n == 1)
    assert(len(s.buffer) == 1)

    s.write_nonnegative(1)
    v, n = d.read_nonnegative()
    assert(v == 1)
    assert(n == 1)

    s.write_nonnegative(127)
    v, n = d.read_nonnegative()
    assert(v == 127)
    assert(n == 1)

    s.write_nonnegative(128)
    v, n = d.read_nonnegative()
    assert(v == 128)
    assert(n == 2)

def test_string():
    for s in ['abcd', '한글']:
        encoded = s.encode('utf-8')
        assert Serializer.len_utf8(s) == len(encoded)

        buffer = bytearray()
        Serializer.write_string(buffer, None, s)
        assert bytes(buffer[1:]) == encoded

        d = Deserializer(buffer)
        decoded = d.read_string(None)
        assert decoded == s
        assert d.pos == len(buffer)