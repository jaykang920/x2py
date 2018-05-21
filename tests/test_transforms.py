# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

import sys

sys.path.append('..')
import x2py

from x2py.buffer_transform import BufferTransform, BufferTransformStack
from x2py.transforms.inverse import Inverse

def test_inverse():
    t1 = Inverse()
    t2 = Inverse()

    chal1 = t1.init_handshake()
    chal2 = t2.init_handshake()

    resp1 = t1.handshake(chal2)
    resp2 = t2.handshake(chal1)

    r1 = t1.fini_handshake(resp2)
    r2 = t2.fini_handshake(resp1)

    assert r1 == True, r2 == True

    b = bytearray('abcdef', 'utf-8')

    r1 = t1.transform(b)
    r2 = t2.inverse_transform(r1)
    assert r2 == b'abcdef'


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

    r1 = s1.transform(b)
    r2 = s2.inverse_transform(r1)
    assert r2 == b'abcdef'
