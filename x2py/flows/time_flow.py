# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from datetime import datetime, timedelta
import heapq

from x2py.builtin_events import *
from x2py.event import EventProxy
from x2py.flow import Flow
from x2py.flows.frame_based_flow import FrameBasedFlow
from x2py.util.rwlock import ReadLock, WriteLock, ReadWriteLock
from x2py.util.trace import Trace

class Timer(object):
    class Tag(object):
        def __init__(self, time_delta, next_utc_time=datetime.utcnow()):
            self.time_delta = time_delta
            self.next_utc_time = next_utc_time

    class Repeater(object):
        def __init__(self, owner):
            self.rwlock = ReadWriteLock()
            self.map = {}
            self.owner = owner
            self.default_case = None

        def add(self, state, time_tag):
            with self.rwlock.wlock():
                if state is not None:
                    self.map[state] = time_tag
                else:
                    default_case = time_tag

        def remove(self, state):
            with self.rwlock.wlock():
                if state is not None:
                    del self.map[state]
                else:
                    default_case = None

        def tick(self, utc_now):
            with self.rwlock.rlock():
                if self.default_case is not None:
                    self.try_fire(utc_now, None, self.default_case)
                if self.map:
                    for key, value in self.map.items():
                        self.try_fire(utc_now, key, value)

        def try_fire(self, utc_now, state, time_tag):
            if utc_now > time_tag.next_utc_time:
                self.owner.callback(state)
                time_tag.next_utc_time = utc_now + time_tag.time_delta

    def __init__(self, callback):
        self.rwlock = ReadWriteLock()
        self.reserved = []
        self.repeater = Timer.Repeater(self)
        self.callback = callback

    def reserve(self, state, time_delta):
        return self.reserve_at_utc_time(state, datetime.utcnow() + time_delta)

    def reserve_at_utc_time(self, state, utc_time):
        with self.rwlock.wlock():
            heapq.heappush(self.reserved, (utc_time, state))
        return (utc_time, state)

    def cancel(self, timer_token):
        with self.rwlock.wlock():
            self.reserved.remove(timer_token)
            heapq.heapify(self.reserved)

    def reserve_repetition(self, state, time_delta, next_utc_time=None):
        if next_utc_time is None:
            next_utc_time = datetime.utcnow() + time_delta
        self.repeater.add(state, Timer.Tag(time_delta, next_utc_time))

    def cancel_repetition(self, state):
        self.repeater.remove(state)

    def tick(self):
        utc_now = datetime.utcnow()
        events = None
        with self.rwlock.rlock() as rlock:
            if self.reserved:
                peeked = self.reserved[0]
                if utc_now >= peeked[0]:
                    events = []
                    rlock.upgrade()
                    while utc_now >= peeked[0]:
                        popped = heapq.heappop(self.reserved)
                        events.append(popped[1])
                        if not self.reserved:
                            break
                        peeked = self.reserved[0]

        if events:
            for event in events:
                self.callback(event)

        self.repeater.tick(utc_now)


class TimeFlow(FrameBasedFlow):
    rwlock = ReadWriteLock()
    instances = {}

    def __init__(self, name):
        super(TimeFlow, self).__init__(name=name)
        self.timer = Timer(self.on_timer)

    @staticmethod
    def get(name='default'):
        with TimeFlow.rwlock.rlock():
            flow = None
            if name not in TimeFlow.instances:
                flow_name = "TimeFlow.{}".format(name)
                flow = TimeFlow(flow_name)
                TimeFlow.instances[name] = flow
                flow.start()
                flow.attach()
            else:
                flow = TimeFlow.instances[name]
        return flow

    def reserve(self, event, time_delta):
        return self.timer.reserve(event, time_delta)

    def reserve_at_utc_time(self, event, utc_time):
        return self.timer.reserve_at_utc_time(event, utc_time)

    def cancel(self, timer_token):
        self.timer.cancel(timer_token)

    def reserve_repetition(self, event, time_delta, next_utc_time=None):
        if next_utc_time is None:
            next_utc_time = datetime.utcnow() + time_delta
        self.timer.reserve_repetition(event, time_delta, next_utc_time)

    def cancel_repetition(self, event):
        self.timer.cancel_repetition(event)

    def update(self):
        self.timer.tick()

    def on_timer(self, event):
        event.post()
