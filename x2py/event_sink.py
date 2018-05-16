# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import weakref
from threading import Lock

from .util.trace import Trace

class EventSink(object):
    """ Cleanup helper base class for any event-consuming classes. """

    def __init__(self):
        self._bindings = []
        self._disposed = False
        self._flow = None
        from .flow import Flow
        flow = Flow.thread_local.current
        if flow is not None:
            self._flow = weakref.ref(flow)
        self._lock = Lock()

    @property
    def flow(self):
        return self._flow() if self._flow is not None else None

    @flow.setter
    def flow(self, value):
        if self._disposed or len(self._bindings) != 0:
            raise RuntimeError()
        self._flow = weakref.ref(value) if value is not None else None

    def cleanup(self):
        with self._lock:
            if self._disposed:
                return

            flow = self.flow
            if flow is None:
                return

            try:
                for binding in self._bindings:
                    flow._unsubscribe(binding[0], binding[1])
                del self._bindings[:]

                self.flow = None
            except BaseException as ex:
                Trace.warn("eventsink: cleanup error {}", ex)
            finally:
                self_disposed = True

    def bind(self, event, handler):
        flow = self.flow
        if flow is not None:
            flow.subscribe(event, handler)

    def unbind(self, event, handler):
        flow = self.flow
        if flow is not None:
            flow.unsubscribe(event, handler)

    def _add_binding(self, token):
        with self._lock:
            self._bindings.append(token)

    def _remove_binding(self, token):
        with self._lock:
            self._bindings.remove(token)
