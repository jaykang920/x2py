# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys

import pytest

sys.path.append('..')
import x2py
from test import *

def test_creation():
    c1 = MyCell1()
    assert c1 is not None
    c2 = MyCell2()
    assert c2 is not None

def test_equivalence():
    c1 = MyCell2()
    c2 = MyCell2()
    assert c1.equivalent(c1)
    assert c1.equivalent(c2)
    assert c2.equivalent(c1)
    c1.foo = 1
    c2.foo = 1
    c2.bar = 'bar'
    assert c2.equivalent(c1)
    assert not c1.equivalent(c2)

def test_eq_():
    c1 = MyCell2()
    c2 = MyCell2()
    assert c1 == c1
    assert c1 == c2
    assert not (c1 != c2)
    c2.bar = 'bar'
    assert not (c1 == c2)
    assert c1 != c2

def test_hash_():
    c1 = MyCell1()
    c2 = MyCell1()
    assert c1.__hash__() == c2.__hash__()
    c2.foo = 1
    assert c1.__hash__() != c2.__hash__()
