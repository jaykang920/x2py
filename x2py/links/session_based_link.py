# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.event_factory import EventFactory
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

    def init_handshake(self, session):
        buffer_transform = self.buffer_transform.clone()
        session.buffer_transform = buffer_transform

        session.send(HandshakeReq().setattrs(
            _transform = False,
            data = buffer_transform.init_handshake()
        ))

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

    def _teardown(self):
        super(SessionBasedLink, self)._teardown()
        self.unbind(LinkSessionConnected().setattrs(link_name = self.name),
            self.on_link_session_connected)
        self.unbind(LinkSessionDisconnected().setattrs(link_name = self.name),
            self.on_link_session_disconnected)

    def on_link_session_connected(self, e):
        self.on_session_connected(e.result, e.context)

    def on_link_session_disconnected(self, e):
        self.on_session_disconnected(e.handle, e.context)

    def on_session_connected(self, result, context):
        pass

    def on_session_disconnected(slef, handle, context):
        pass
