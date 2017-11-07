# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys

import pytest

sys.path.append('..')
import x2py

from x2py.util.ranged_int_pool import RangedIntPool

def test_creation():
    p1 = RangedIntPool(0, 1)
    assert p1 is not None
    assert p1._min_value == 0
    assert p1._max_value == 1
    assert p1._advancing == False
    assert p1._offset == 0
    assert len(p1._blocks) == 1
    assert p1._blocks[0] == 0

    p2 = RangedIntPool(2, 34, True)
    assert p2 is not None
    assert p2._min_value == 2
    assert p2._max_value == 34
    assert p2._advancing == True
    assert p2._offset == 0
    assert len(p2._blocks) == 2
    assert p2._blocks[0] == 0
    assert p2._blocks[1] == 0

def test_functions():
    p1 = RangedIntPool(0, 32)
    assert p1.acquire() == 0
    p1.release(0)
    assert p1.acquire() == 0
    p1.claim(1)
    assert p1.acquire() == 2

    for i in range(3, 33):
        assert p1.acquire() == i

    with pytest.raises(ResourceWarning):
        p1.acquire()

    p2 = RangedIntPool(0, 32, True)
    assert p2.acquire() == 0
    p2.release(0)
    assert p2.acquire() == 1

    for i in range(2, 33):
        assert p2.acquire() == i

    assert p2.acquire() == 0

    with pytest.raises(ResourceWarning):
        p1.acquire()

    p2.release(16)
    assert p2.acquire() == 16
