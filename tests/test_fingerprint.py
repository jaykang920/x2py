# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys

import pytest

sys.path.append('..')
from x2py.fingerprint import Fingerprint

def test_creation():
    with pytest.raises(ValueError):
        fp = Fingerprint(-1)
    fp = Fingerprint(0)
    assert fp.length == 0
    assert fp.blocks is None
    fp = Fingerprint(32)
    assert fp.length == 32
    assert fp.blocks is None
    fp = Fingerprint(33)
    assert fp.length == 33
    assert len(fp.blocks) == 1
    fp = Fingerprint(64)
    assert fp.length == 64
    assert len(fp.blocks) == 1
    fp = Fingerprint(65)
    assert fp.length == 65
    assert len(fp.blocks) == 2

def test_copy_creation():
    for n in [32, 33]:
        fp1 = Fingerprint(n)
        indices = [0, 1, n - 2, n - 1]
        for i in indices:
            fp1.touch(i)
        fp2 = Fingerprint(fp1)
        for i in indices:
            assert fp2.get(i) == True
        # Make sure that we have a deep copy
        for i in indices:
            fp2.wipe(i)
        for i in indices:
            assert fp1.get(i) == True

def test_accessors():
    fp = Fingerprint(65)
    with pytest.raises(ValueError):
        fp.get(-1)
        fp.get(65)
    for i in range(65):
        assert fp.get(i) == False
    for i in [0, 1, 31, 32, 63]:
        fp.touch(i)
        assert fp.get(i) == True
        fp.wipe(i)
        assert fp.get(i) == False

def test_equivalence():
    fp1 = Fingerprint(33)
    fp2 = Fingerprint(33)
    assert fp1.equivalent(fp1)
    assert fp1.equivalent(fp2)
    assert fp2.equivalent(fp1)
    fp1.touch(32)
    fp2.touch(31)
    fp2.touch(32)
    assert fp2.equivalent(fp1)
    assert not fp1.equivalent(fp2)

def test_eq_():
    fp1 = Fingerprint(33)
    fp2 = Fingerprint(33)
    assert fp1 == fp1
    assert fp1 == fp2
    assert not (fp1 != fp2)
    fp2.touch(32)
    assert not (fp1 == fp2)
    assert fp1 != fp2

def test_hash_():
    fp1 = Fingerprint(33)
    fp2 = Fingerprint(33)
    assert fp1.__hash__() == fp2.__hash__()
    fp2.touch(32)
    assert fp1.__hash__() != fp2.__hash__()

def test_lt_():
    fp1 = Fingerprint(32)
    fp2 = Fingerprint(33)
    fp3 = Fingerprint(33)
    assert not (fp1 < fp1)
    # with different lengths
    assert fp1 < fp2
    assert fp2 > fp1
    fp1.touch(0)
    assert fp1 < fp2
    # with same lengths
    assert not (fp2 < fp3)
    fp3.touch(31)
    assert fp2 < fp3
    fp2.touch(32)
    assert fp2 > fp3



