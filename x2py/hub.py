# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from .event import Event
from .flow import Flow
from .util.trace import Trace

class Hub:
    """ Represents the singleton event distribution bus. """

    class _Hub:
        def __init__(self):
            self._flows = []

        def attach(self, flow):
            """ Attaches the specified flow to the hub. """
            if (flow is None or not isinstance(flow, Flow)):
                raise TypeError()
            if flow not in self._flows:
                self._flows.append(flow)
                Trace.debug("hub: attached flow '{}'", flow.name)
            return self

        def detach(self, flow):
            """ Detaches the specified flow from the hub. """
            if (flow is None or not isinstance(flow, Flow)):
                raise TypeError()
            if flow in self._flows:
                self._flows.remove(flow)
                Trace.debug("hub: detached flow '{}'", flow.name)
            return self

        def detach_all(self):
            """ Detaches all the attached flows. """
            snapshot = self._flows[::-1]
            for flow in snapshot:
                self.detach(flow)

        def feed(self, event):
            if (event is None or not isinstance(event, Event)):
                raise TypeError()
            for flow in self._flows:
                flow.feed(event)

        def start_flows(self):
            for flow in self._flows:
                flow.start()

        def stop_flows(self):
            for flow in reversed(self._flows):
                flow.stop()

    instance = _Hub()

    def __init__(self):
        raise AssertionError()

    @staticmethod
    def post(event):
        Hub.instance.feed(event)

    @staticmethod
    def startup():
        """ Starts all the flows attached to the hub. """

        Trace.debug("starting up")

        Hub.instance.start_flows()

        Trace.info("started")

    @staticmethod
    def shutdown():
        """ Stops all the flows attached to the hub. """

        Trace.debug("shutting down")

        Hub.instance.stop_flows()

        Trace.info("stopped")

    class Flows:
        """ Represents the set of attached flows for convenient cleanup. """

        def startup(self): Hub.startup()
        def shutdown(self): Hub.shutdown()

        def __enter__(self):
            self.startup()
            return self

        def __exit__(self, type, value, traceback):
            self.shutdown()
