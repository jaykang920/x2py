# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.builtin_events import HeartbeatEvent
from x2py.event_factory import EventFactory
from x2py.links.strategy import HeartbeatStrategy
from x2py.util.trace import Trace

class KeepaliveStrategy(HeartbeatStrategy):
    EventFactory.register_type(HeartbeatEvent)

    def __init__(self):
        self.incoming_heartbeat_enabled = True
        self.outgoing_heartbeat_enabled = True
        self.max_failure_count = 3

    def before_session_setup(self, session):
        session_strategy = KeepaliveSessionStrategy()
        session_strategy.session = session
        session.heartbeat_strategy = session_strategy

class ClientKeepaliveStrategy(KeepaliveStrategy):
    def on_heartbeat(self):
        pass

class ServerKeepaliveStrategy(KeepaliveStrategy):
    def on_heartbeat(self):
        pass

class KeepaliveSessionStrategy(HeartbeatStrategy.SubStrategy):
    def __init__(self):
        self.has_received = False
        self.has_sent = False
        self.successive_failure_count = 0

    def process(event):
        if event.type_id() == BuiltinEventType.HearbeatEvent:
            return True
        return False

    def on_hearbeat(self):
        link_strategy = self.session.link.heartbeat_strategy

        if link_strategy.outgoing_heartbeat_enabled:
            if has_sent:
                has_sent = False
            else:
                self.session.send(Hub.heartbeat_event)

        if link_strategy.incoming_heartbeat_enabled:
            if has_received:
                has_received = False
                successive_failure_count = 0
            else:
                successive_failure_count = successive_failure_count + 1
                if not self.marked and \
                    successive_failure_count > link_strategy.max_failure_count:
                    return True

    def on_receive(self):
        has_received = True

    def on_send(self, event):
        if not has_sent and \
            (event.type_id() != BuiltinEventType.HeartbeatEvent):
            has_sent = True
