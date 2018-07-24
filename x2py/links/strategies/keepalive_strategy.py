# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.builtin_events import BuiltinEventType, HeartbeatEvent
from x2py.event_factory import EventFactory
from x2py.hub import Hub
from x2py.links.strategy import HeartbeatStrategy
from x2py.util.trace import Trace

class KeepaliveStrategy(HeartbeatStrategy):
    EventFactory.register_type(HeartbeatEvent)

    def __init__(self):
        super(KeepaliveStrategy, self).__init__()
        self.incoming_heartbeat_enabled = True
        self.outgoing_heartbeat_enabled = True
        self.max_failure_count = 3

    def before_session_setup(self, session):
        session_strategy = KeepaliveSessionStrategy()
        session_strategy.session = session
        session.heartbeat_strategy = session_strategy

class ClientKeepaliveStrategy(KeepaliveStrategy):
    def on_heartbeat(self):
        session = self.link.session
        if session is None or not session.connected():
            return
        session_strategy = self.link.session.heartbeat_strategy
        if session_strategy.on_heartbeat():
            Trace.warn("{} {} closing due to the keepalive failure", \
                self.link.name, session.handle)
            session.close()

class ServerKeepaliveStrategy(KeepaliveStrategy):
    def on_heartbeat(self):
        sessions = list(self.link.sessions.values())
        for session in sessions:
            if session is None or not session.connected():
                continue
            session_strategy = session.heartbeat_strategy
            if session_strategy.on_heartbeat():
                Trace.warn("{} {} closing due to the keepalive failure", \
                    self.link.name, session.handle)
                session.close()

class KeepaliveSessionStrategy(HeartbeatStrategy.SubStrategy):
    def __init__(self):
        super(KeepaliveSessionStrategy, self).__init__()
        self.has_received = False
        self.has_sent = False
        self.successive_failure_count = 0

    def process(event):
        if event.type_id() == BuiltinEventType.HearbeatEvent:
            return True
        return False

    def on_heartbeat(self):
        link_strategy = self.session.link.heartbeat_strategy

        if link_strategy.outgoing_heartbeat_enabled:
            if self.has_sent:
                self.has_sent = False
            else:
                self.session.send(Hub.heartbeat_event)

        if link_strategy.incoming_heartbeat_enabled:
            if self.has_received:
                self.has_received = False
                self.successive_failure_count = 0
            else:
                self.successive_failure_count = self.successive_failure_count + 1
                if not self.marked and \
                    self.successive_failure_count > link_strategy.max_failure_count:
                    Trace.debug("{} {} keepalive failure count {}",
                        self.session.link.name, self.session.handle, self.successive_failure_count)
                    return True

    def on_receive(self):
        self.has_received = True

    def on_send(self, event):
        if not self.has_sent and \
            (event.type_id() != BuiltinEventType.HEARTBEAT_EVENT):
            self.has_sent = True
