# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.util.ranged_int_pool import RangedIntPool

class WaitHandlePool(object):
    pool = RangedIntPool(1, 65536, True)

    def __init__(self):
        raise AssertionError()

    @staticmethod
    def acquire():
        return WaitHandlePool.pool.acquire()

    @staticmethod
    def release(handle):
        return WaitHandlePool.pool.release(handle)
