# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

class Coroutine(object):
    def __init__(self, parent=None):
        self.result = None
        self.routine = None
        self.running = False
        self.started = False
        self.parent = parent

    @staticmethod
    def start(routine):
        coroutine = Coroutine()
        coroutine.start(routine(coroutine))

    @staticmethod
    def start1(routine, arg1):
        coroutine = Coroutine()
        coroutine.start(routine(coroutine, arg1))

    def start(self, routine):
        self.routine = iter(routine)
        self.running = bool(routine)
        if not self.next():
            if self.parent:
                # Indirectly chain into the parent coroutine.
                WaitForNext(self.parent, self.result)

    def next(self):
        if not self.running:
            return False

        if next(self.routine, False):
            self.started = True
            return True

        self.running = False

        if self.started and self.parent:
            self.parent.result = self.result
            self.parent.next()

        return False

class CoroutineHandler(object):
    def __init__(self, routine):
        self.routine = routine

    def __call__(self, e):
        Coroutine.start1(self.routine, e)
