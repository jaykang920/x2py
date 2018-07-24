# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from datetime import timedelta

from x2py.builtin_events import HeartbeatEvent
from x2py.config import Config
from x2py.event import Event
from x2py.flow import Flow
from x2py.flows.time_flow import TimeFlow
from x2py.util.rwlock import ReadLock, WriteLock, ReadWriteLock
from x2py.util.trace import Trace

class Hub(object):
    """Represents the singleton event distribution bus."""

    class _Hub(object):
        def __init__(self):
            self.cases = []  # list of hub cases
            self.flows = []  # list of all the flows attached to this hub
            self.rwlock = ReadWriteLock()

        def add(self, case):
            """Adds the specified hub case to the hub."""
            if case is None or not isinstance(case, Hub.Case):
                raise TypeError()
            with self.rwlock.wlock():
                if case not in self.cases:
                    self.cases.append(case)
                    Trace.debug("hub: added case {}", type(case).__name__)
            return self

        def insert(self, index, case):
            """Inserts the specified hub case to the hub, at the specified index."""
            if case is None or not isinstance(case, Hub.Case):
                raise TypeError()
            with self.rwlock.wlock():
                if case not in self.cases:
                    self.cases.insert(index, case)
                    Trace.debug("hub: inserted case {} at index {}",
                        type(case).__name__, index)
            return self

        def remove(self, case):
            """Removes the specified hub case from the hub."""
            if case is None or not isinstance(case, Hub.Case):
                raise TypeError()
            with self.rwlock.wlock():
                if case in self.cases:
                    self.cases.remove(case)
                    Trace.debug("hub: removed case {}", type(case).__name__)
            return self

        def attach(self, flow):
            """Attaches the specified flow to the hub."""
            if flow is None or not isinstance(flow, Flow):
                raise TypeError()
            with self.rwlock.wlock():
                if flow not in self.flows:
                    self.flows.append(flow)
                    Trace.debug("hub: attached flow {}", flow.name)
            return self

        def detach(self, flow):
            """Detaches the specified flow from the hub."""
            if flow is None or not isinstance(flow, Flow):
                raise TypeError()
            with self.rwlock.wlock():
                if flow in self.flows:
                    self.flows.remove(flow)
                    Trace.debug("hub: detached flow {}", flow.name)
            return self

        def detach_all(self):
            """Detaches all the attached flows."""
            snapshot = self.flows[::-1]
            for flow in snapshot:
                self.detach(flow)

        def feed(self, event):
            if event is None or not isinstance(event, Event):
                raise TypeError()
            with self.rwlock.rlock():
                for flow in self.flows:
                    flow.feed(event)

        def setup(self):
            with self.rwlock.rlock():
                snapshot = self.cases[:]
            for case in snapshot:
                Trace.trace("hub: setting up case {}", type(case).__name__)
                case.setup()

        def teardown(self):
            with self.rwlock.rlock():
                snapshot = self.cases[::-1]
            for case in snapshot:
                try:
                    Trace.trace("hub: tearing down case {}", type(case).__name__)
                    case.teardown()
                except:
                    pass

        def start_flows(self):
            with self.rwlock.rlock():
                snapshot = self.flows[:]
            for flow in snapshot:
                Trace.trace("hub: starting flow {}", flow.name)
                flow.start()
                Trace.debug("hub: started flow {}", flow.name)

        def stop_flows(self):
            with self.rwlock.rlock():
                snapshot = self.flows[::-1]
            for flow in snapshot:
                try:
                    Trace.trace("hub: stopping flow {}", flow.name)
                    flow.stop()
                    Trace.debug("hub: stopped flow {}", flow.name)
                except:
                    pass

    instance = _Hub()
    heartbeat_event = HeartbeatEvent().setattrs( _transform = False )

    def __init__(self):
        raise AssertionError()

    @staticmethod
    def post(event):
        """Posts up the specified event to the hub."""
        Hub.instance.feed(event)

    @staticmethod
    def startup():
        """Starts all the flows attached to the hub."""
        Trace.debug("starting up")
        Hub.instance.setup()
        Hub.instance.start_flows()
        TimeFlow.get().reserve_repetition(Hub.heartbeat_event, \
            timedelta(seconds=Config.heartbeat_interval))
        Trace.info("started")

    @staticmethod
    def shutdown():
        """Stops all the flows attached to the hub."""
        Trace.debug("shutting down")
        Hub.instance.stop_flows()
        Hub.instance.teardown()
        Trace.info("stopped")

    class Case(object):
        """Represents a hub-scope case that is initialized and terminated
        along with startup/shutdown of the hub."""

        def setup(self):
            """Overridden by subclasses for initialization."""
            pass

        def teardown(self):
            """Overridden by subclasses for clean-up."""
            pass

    class Flows(object):
        """Represents the set of attached flows for convenient cleanup."""

        def startup(self):
            """Starts all the attached flows."""
            Hub.startup()

        def shutdown(self):
            """Stops all the attached flows."""
            Hub.shutdown()

        def __enter__(self):
            self.startup()
            return self

        def __exit__(self, type, value, traceback):
            self.shutdown()
