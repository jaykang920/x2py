# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys

import pytest

sys.path.append('..')
import x2py

from x2py.event import EventProxy

from test import *

def test_creation():
    e1 = MyEvent1()
    assert e1 is not None
    e2 = MyEvent2()
    assert e2 is not None

def test_equivalence():
    e1 = MyEvent2()
    e2 = MyEvent2()
    assert e1.equivalent(e1)
    assert e1.equivalent(e2)
    assert e2.equivalent(e1)
    e1.foo = 1
    e2.foo = 1
    e2.bar = 'bar'
    assert e2.equivalent(e1)
    assert not e1.equivalent(e2)

def test_eq_():
    e1 = MyEvent2()
    e2 = MyEvent2()
    assert e1 == e1
    assert e1 == e2
    assert not (e1 != e2)
    e2.bar = 'bar'
    assert not (e1 == e2)
    assert e1 != e2

def test_hash_():
    e1 = MyEvent1()
    e2 = MyEvent1()
    assert e1.__hash__() == e2.__hash__()
    e2.foo = 1
    assert e1.__hash__() != e2.__hash__()

def test_proxy():
    e0 = Event()
    e1 = MyEvent1()
    e2 = MyEvent2()

    e1.foo = 1
    e2.foo = 1
    e2.bar = 'bar'

    d = { e0: 0, e1: 1, e2: 2 }

    ep = EventProxy()

    e = MyEvent1()
    e.foo = 1
    ep.event = e
    ep.fingerprint = e.fingerprint
    ep.type_id = e.type_id()

    n = d.get(ep)
    assert n == 1

    e = Event()
    ep.event = e
    ep.fingerprint = e.fingerprint
    ep.type_id = e.type_id()

    n = d.get(ep)
    assert n == 0

    e = MyEvent2()
    e.foo = 1
    e.bar = 'bar'
    ep.event = e
    ep.fingerprint = e.fingerprint
    ep.type_id = e.type_id()

    n = d.get(ep)
    assert n == 2

    e.foo = 2

    n = d.get(ep)
    assert n is None
