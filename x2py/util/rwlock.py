

# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from threading import RLock, Semaphore

class WriteLock(object):
    def __init__(self, rwlock):
        self.rwlock = rwlock

    def __enter__(self):
        self.rwlock.wlock_acquire()
        return self

    def __exit__(self, type, value, traceback):
        self.rwlock.wlock_release()

class ReadLock(object):
    def __init__(self, rwlock):
        self.rwlock = rwlock
        self.upgraded = False

    def upgrade(self):
        self.rwlock.rlock_release()
        self.rwlock.wlock_acquire()
        self.upgraded = True

    def __enter__(self):
        self.rwlock.rlock_acquire()
        return self

    def __exit__(self, type, value, traceback):
        if self.upgraded:
            self.rwlock.wlock_release()
        else:
            self.rwlock.rlock_release()

class ReadWriteLock(object):
    """Reader-writer lock with preference to writers."""

    def __init__(self):
        self._lock = RLock()
        self._can_read = Semaphore(0)
        self._can_write = Semaphore(0)
        self._active_readers  = 0
        self._active_writers  = 0
        self._waiting_readers = 0
        self._waiting_writers = 0

    def rlock(self):
        return ReadLock(self)

    def rlock_acquire(self):
        with self._lock:
            if self._active_writers == 0 and self._waiting_writers == 0:
                self._active_readers += 1
                self._can_read.release()
            else:
                self._waiting_readers += 1
        self._can_read.acquire()

    def rlock_release(self):
        with self._lock:
            self._active_readers -= 1
            if self._active_readers == 0 and self._waiting_writers != 0:
                self._active_writers  += 1
                self._waiting_writers -= 1
                self._can_write.release()

    def wlock(self):
        return WriteLock(self)

    def wlock_acquire(self):
        with self._lock:
            if self._active_writers == 0 and self._waiting_writers == 0 and self._active_readers == 0:
                self._active_writers += 1
                self._can_write.release()
            else:
                self._waiting_writers += 1
        self._can_write.acquire()

    def wlock_release(self):
        with self._lock:
            self._active_writers -= 1
            if self._waiting_writers != 0:
                self._active_writers  += 1
                self._waiting_writers -= 1
                self._can_write.release()
            elif self._waiting_readers != 0:
                t = self._waiting_readers
                self._waiting_readers = 0
                self._active_readers += t
                while t > 0:
                    self._can_read.release()
                    t -= 1
