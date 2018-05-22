# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.event_sink import EventSink
from x2py.util.trace import Trace

class Case(EventSink):
    """Represents a set of application logic."""

    def __init__(self):
        super(Case, self).__init__()

    def setup_with(self, flow):
        """Initializes this case with the specified holding flow."""
        self.flow = flow

        from x2py.flow import Flow
        backup = Flow.thread_local.current
        Flow.thread_local.current = flow

        self._setup()

        Flow.thread_local.current = backup

    def teardown_with(self, flow):
        """Cleans up this case with the specified holding flow."""
        from x2py.flow import Flow
        backup = Flow.thread_local.current
        Flow.thread_local.current = flow

        self._teardown()

        Flow.thread_local.current = backup

        self.cleanup()  # eventsink cleanup

    def start(self):
        """Called after the holding flow starts."""
        self.on_start()

    def stop(self):
        """Called before the holding flow stops."""
        self.on_stop()

    def setup(self):
        """Overridden by subclasses to build a initialization chain."""
        pass

    def teardown(self):
        """Overridden by subclasses to build a cleanup chain."""
        pass

    def on_start(self):
        """Overridden by subclasses to build a flow startup handler chain."""
        pass

    def on_stop(self):
        """Overridden by subclasses to build a flow shutdown handler chain."""
        pass

    def _setup(self):
        """Called internally when this case is initialized."""
        self.setup()

    def _teardown(self):
        """Called internally when this case is cleaned up."""
        self.teardown()

class CaseStack(object):
    """Handles a group of cases."""

    def __init__(self):
        self.cases = []
        self.activated = False

    def add(self, case):
        if case is None or not isinstance(case, Case):
            raise TypeError()
        if case in self.cases:
            return False
        self.cases.append(case)
        return True

    def remove(self, case):
        if case is None or not isinstance(case, Case):
            raise TypeError()
        if case not in self.cases:
            return False
        self.cases.remove(case)
        return True

    def setup_with(self, flow):
        if self.activated:
            return
        self.activated = True
        for case in self.cases:
            Trace.trace("casestack: setting up case '{}'", type(case).__name__)
            case.setup_with(flow)

    def teardown_with(self, flow):
        if not self.activated:
            return
        self.activated = False
        for case in reversed(self.cases):
            try:
                Trace.trace("casestack: tearing down case '{}'", type(case).__name__)
                case.teardown_with(flow)
            except BaseException as ex:
                Trace.error("{} {} teardown: {}", flow.name, type(case).__name__, ex)

    def start(self):
        for case in self.cases:
            case.start()

    def stop(self):
        for case in reversed(self.cases):
            try:
                case.stop()
            except:
                pass
