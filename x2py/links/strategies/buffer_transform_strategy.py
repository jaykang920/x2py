# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.event_factory import EventFactory
from x2py.links.link_events import *
from x2py.links.strategy import ChannelStrategy
from x2py.util.trace import Trace

class BufferTransformStrategy(ChannelStrategy):
    EventFactory.register_type(HandshakeReq)
    EventFactory.register_type(HandshakeResp)
    EventFactory.register_type(HandshakeAck)

    def __init__(self, buffer_transform=None):
        self.buffer_transform = buffer_transform

    def before_session_setup(self, session):
        session_strategy = BufferTransformSessionStrategy()
        session_strategy.session = session
        session.channel_strategy = session_strategy

    def init_handshake(self, session):
        if self.buffer_transform is None:
            return

        session_strategy = session.channel_strategy

        buffer_transform = self.buffer_transform.clone()
        session_strategy.buffer_transform = buffer_transform

        session.send(HandshakeReq().setattrs(
            _transform = False,
            data = buffer_transform.init_handshake()
        ))

    def cleanup(self):
        if self.buffer_transform is None:
            return
        self.buffer_transform.cleanup()
        self.buffer_transform = None

class BufferTransformSessionStrategy(ChannelStrategy.SubStrategy):
    def __init__(self):
        self.buffer_transform = None
        self.rx_transform_ready = False
        self.tx_transform_ready = False

    def process(self, event):
        type_id = event.type_id()
        if type_id == LinkEventType.HANDSHAKE_REQ:
            response = None
            try:
                response = self.buffer_transform.handshake(event.data)
            except Exception as ex:
                Trace.error("{} error handshaking {}", self.link.name, ex)
            self.session.send(HandshakeResp().setattrs(
                _transform = False,
                data = response
            ))
        elif type_id == LinkEventType.HANDSHAKE_RESP:
            result = False
            try:
                result = self.buffer_transform.fini_handshake(event.data)
            except Exception as ex:
                Trace.error("{} error finishing handshake {}", self.link.name, ex)
            if result:
                self.rx_transform_ready = True
            self.session.send(HandshakeAck().setattrs(
                _transform = False,
                result = result
            ))
        elif type_id == LinkEventType.HANDSHAKE_ACK:
            result = event.result
            if result:
                self.tx_transform_ready = True
            self.session.link.on_connect(result, self.session)
        else:
            return False
        return True

    def cleanup(self):
        if self.buffer_transform is None:
            return
        self.buffer_transform.cleanup()
        self.buffer_transform = None

    def before_send(self, buffer):
        if self.tx_transform_ready:
            buffer = self.buffer_transform.transform(buffer)
            return True, buffer
        return False, buffer

    def after_receive(self, buffer):
        if self.rx_transform_ready:
            buffer = self.buffer_transform.inverse_transform(buffer)
        return buffer

