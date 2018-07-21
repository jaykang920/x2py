# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.event_factory import EventFactory
from x2py.hub import Hub
from x2py.link import Link
from x2py.util.ranged_int_pool import RangedIntPool
from x2py.util.rwlock import ReadLock, WriteLock, ReadWriteLock
from x2py.util.trace import Trace

from x2py.links.link_events import *

def _static_init():
    EventFactory.register(LinkEventType.HANDSHAKE_REQ, HandshakeReq)
    EventFactory.register(LinkEventType.HANDSHAKE_RESP, HandshakeResp)
    EventFactory.register(LinkEventType.HANDSHAKE_ACK, HandshakeAck)

    return RangedIntPool(1, 65536, True)

class SessionBasedLink(Link):
    handle_pool = _static_init()

    def __init__(self, name):
        super(SessionBasedLink, self).__init__(name)
        self.rwlock = ReadWriteLock()
        self.channel_strategy = None
        self.heartbeat_strategy = None

    @property
    def has_channel_strategy(self):
        return (self.channel_strategy is not None)

    @property
    def has_heartbeat_strategy(self):
        return (self.heartbeat_strategy is not None)

    def init_session(self, session):
        if self.has_channel_strategy:
            self.channel_strategy.before_session_setup(session)
        if self.has_heartbeat_strategy:
            self.heartbeat_strategy.before_session_setup(session)

        if self.has_channel_strategy:
            self.channel_strategy.init_handshake(session)
        else:
            self.on_connect(True, session)


    def on_connect(self, result, context):
        Trace.info("{} connected {} {}", self.name, result, context)

        if result:
            handle = SessionBasedLink.handle_pool.acquire()
            context.handle = handle

        self._on_connect(result, context)

        LinkSessionConnected().setattrs(
            link_name = self.name,
            result = result,
            context = context
        ).post()

    def on_disconnect(self, handle, context):
        Trace.info("{} disconnected {} {}", self.name, handle, context)

        self._on_disconnect(handle, context)

        if handle != 0:
            SessionBasedLink.handle_pool.release(handle)

        LinkSessionDisconnected().setattrs(
            link_name = self.name,
            handle = handle,
            context = context
        ).post()

    def _on_connect(self, result, context):
        pass

    def _on_disconnect(self, handle, context):
        pass

    def _setup(self):
        super(SessionBasedLink, self)._setup()

        self.bind(LinkSessionConnected().setattrs(link_name = self.name),
            self.on_link_session_connected)
        self.bind(LinkSessionDisconnected().setattrs(link_name = self.name),
            self.on_link_session_disconnected)

        if self.has_channel_strategy:
            self.channel_strategy.link = self
            self.channel_strategy.setup()

        if self.has_heartbeat_strategy:
            self.heartbeat_strategy.link = self
            self.heartbeat_strategy.setup()

            self.bind(Hub.heartbeat_event, self.on_heartbeat_event)

    def _teardown(self):
        if self.has_heartbeat_strategy:
            self.heartbeat_strategy.teardown()
            self.heartbeat_strategy = None
        if self.has_channel_strategy:
            self.channel_strategy.teardown()
            self.channel_strategy = None

        self.unbind(LinkSessionConnected().setattrs(link_name = self.name),
            self.on_link_session_connected)
        self.unbind(LinkSessionDisconnected().setattrs(link_name = self.name),
            self.on_link_session_disconnected)

        super(SessionBasedLink, self)._teardown()

    def on_link_session_connected(self, event):
        self.on_session_connected(event.result, event.context)

    def on_link_session_disconnected(self, event):
        self.on_session_disconnected(event.handle, event.context)

    def on_session_connected(self, result, context):
        pass

    def on_session_disconnected(slef, handle, context):
        pass

    def on_heartbeat_event(self, event):
        self.heartbeat_strategy.on_heartbeat()
