# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import datetime
import sys

import pytest

sys.path.append('..')
import x2py

from x2py.deserializer import Deserializer
from x2py.serializer import Serializer

from test import *

def test_byte():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)
    for test_value in [0, 1, 0x07f, 0x080, 0x0ff ]:
        s.write_byte(None, test_value)
        value = d.read_byte(None)
        assert value == test_value

def test_int8():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)
    for test_value in [ -128, -1, 0, 1, 127 ]:
        s.write_int8(None, test_value)
        value = d.read_int8(None)
        assert value == test_value

def test_int16():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)
    for test_value in [ -32768, -1, 0, 1, 32767 ]:
        s.write_int16(None, test_value)
        value = d.read_int16(None)
        assert value == test_value

def test_int32():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)
    for test_value in [ -2147483648, -1, 0, 1, 2147483647 ]:
        s.write_int32(None, test_value)
        value = d.read_int32(None)
        assert value == test_value

def test_int64():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)
    for test_value in [ -9223372036854775808, -1, 0, 1, 9223372036854775807 ]:
        s.write_int64(None, test_value)
        value = d.read_int64(None)
        assert value == test_value

def test_float64():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)
    for test_value in [ 0.01 ]:
        s.write_float64(None, test_value)
        value = d.read_float64(None)
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
        serializer = Serializer(buffer)
        serializer.write_string(None, s)
        assert bytes(buffer[1:]) == encoded

        d = Deserializer(buffer)
        decoded = d.read_string(None)
        assert decoded == s
        assert d.pos == len(buffer)

def test_datetime():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)
    for test_value in [ datetime.datetime.now(), datetime.datetime(1969, 12, 31) ]:
        s.write_datetime(None, test_value)
        value = d.read_datetime(None)
        truncated = test_value - datetime.timedelta(microseconds=(test_value.microsecond % 1000))
        assert value == truncated

def test_bytes():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)

    test_value = b'abcd'
    s.write_bytes(None, test_value)
    assert len(buffer) == 5
    value = d.read_bytes(None)
    assert value == test_value

def test_cell():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)

    test_value = MyCell1()
    test_value.foo = 1
    s.write_cell(None, test_value)

    print(buffer)

    value = d.read_cell(MetaProperty(None, MetaProperty.CELL, factory_method=MyCell1))
    assert value == test_value

def test_list():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)

    # list(int32)
    metaprop = MetaProperty('List', 13, details=[ MetaProperty('None', 5) ])

    test_value = [ 1, 2, 3 ]
    s.write_list(metaprop, test_value)

    value = d.read_list(metaprop)
    assert len(value) == len(test_value)
    assert value == test_value

def test_map():
    buffer = bytearray()
    s = Serializer(buffer)
    d = Deserializer(buffer)

    # map(int32, string)
    metaprop = MetaProperty('Map', 14, details=[ MetaProperty(None, 5), MetaProperty(None, 9) ])

    test_value = { 1: "one", 2: 'two', 3: 'three' }
    s.write_map(metaprop, test_value)

    value = d.read_map(metaprop)
    assert len(value) == len(test_value)
    assert value == test_value
