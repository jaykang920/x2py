# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.coroutine import Coroutine

class WaitForCompletion(object):
    def __init__(self, coroutine, routine):
        c = Coroutine(coroutine)
        c.start(routine(c))
