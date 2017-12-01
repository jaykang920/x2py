# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys

sys.path.append('..')
import x2py

from x2py.buffer_transform import BufferTransform, BufferTransformStack
from x2py.transforms.inverse import Inverse

def test_inverse():
    t1 = Inverse()
    t2 = Inverse()

    b = bytearray('abcdef', 'utf-8')

    len1 = t1.transform(b, len(b))
    len2 = t2.inverse_transform(b, len1)
    assert b == b'abcdef'

    s1 = BufferTransformStack()
    s1.add(Inverse())
    s1.add(Inverse())
    s1.add(Inverse())
    s2 = s1.clone()

    chal1 = s1.init_handshake()
    chal2 = s2.init_handshake()

    resp1 = s1.handshake(chal2)
    resp2 = s2.handshake(chal1)

    r1 = s1.fini_handshake(resp2)
    r2 = s2.fini_handshake(resp1)

    assert r1 == True, r2 == True

    len1 = s1.transform(b, len(b))
    len2 = s2.inverse_transform(b, len1)
    assert b == b'abcdef'
