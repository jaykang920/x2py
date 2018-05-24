# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.deserializer import Deserializer
from x2py.event_factory import EventFactory
from x2py.hub import Hub
from x2py.serializer import Serializer
from x2py.util.trace import Trace

from x2py.links.link_events import *

class LinkSession(object):
    """Abstract base class for concrete link sessions."""

    def __init__(self, link):  # link: SessionBasedLink
        self.link = link
        self.handle = 0
        self.polarity = False
        self.buffer_transform = None
        self.rx_transform_ready = False
        self.tx_transform_ready = False
        self.rx_buffer = bytearray()

    def cleanup(self):
        if self.buffer_transform is not None:
            self.buffer_transform.cleanup()
            self.buffer_transform = None

    def close(self):
        self.cleanup()

    def on_receive(self, data):
        self.rx_buffer += data

        deserializer = Deserializer()
        while True:
            deserializer.buffer = self.rx_buffer
            deserializer.pos = 0

            num_bytes, length, transformed = self.parse_header(deserializer)
            if num_bytes == 0:
                return

            if len(self.rx_buffer) < (length + num_bytes):
                return
            buffer = self.rx_buffer[num_bytes:num_bytes + length]
            self.rx_buffer = self.rx_buffer[num_bytes + length:]

            if self.buffer_transform is not None:
                if self.rx_transform_ready and transformed:
                    try:
                        buffer = self.buffer_transform.inverse_transform(buffer)
                    except Exception as ex:
                        Trace.error("{} inverse transform error {}", self.link.name, ex)
                        continue

            deserializer.buffer = buffer
            deserializer.pos = 0

            type_id = deserializer.read_int32(None)

            event = EventFactory.create(type_id)
            if event is None:
                continue
            event.deserialize(deserializer)

            Trace.debug("{} received {}", self.link.name, event)

            if self._process(event):
                continue

            event._handle = self.handle

            Hub.post(event)

    def _process(self, event):
        type_id = event.type_id()
        if type_id == LinkEventType.HANDSHAKE_REQ:
            response = None
            try:
                response = self.buffer_transform.handshake(event.data)
            except Exception as ex:
                Trace.error("{} error handshaking {}", self.link.name, ex)
            self.send(HandshakeResp().setattrs(
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
            self.send(HandshakeAck().setattrs(
                _transform = False,
                result = result
            ))
        elif type_id == LinkEventType.HANDSHAKE_ACK:
            result = event.result
            if result:
                self.tx_transform_ready = True
            self.link.on_connect(result, self)
        else:
            return False
        return True

    def send(self, event):
        serializer = Serializer()
        serializer.write_int32(None, event.type_id())
        event.serialize(serializer)
        buffer = serializer.buffer

        transformed = False
        if self.buffer_transform is not None:
            if self.tx_transform_ready and event._transform:
                buffer = self.buffer_transform.transform(buffer)
                transformed = True

        header_buffer = self.build_header(buffer, transformed)

        data = bytes(header_buffer + buffer)

        self._send(data)
