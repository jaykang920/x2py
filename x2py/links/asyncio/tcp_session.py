# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import asyncio

from ...deserializer import Deserializer
from ...serializer import Serializer
from ...util.trace import Trace

from ..link_session import LinkSession

class TcpSession(LinkSession, asyncio.Protocol):
    def __init__(self, link):
        LinkSession.__init__(self, link)
        asyncio.Protocol.__init__(self)
        self.transport = None
        self.rx_buffer = bytearray()

    def cleanup(self):
        super(TcpSession, self).cleanup()

    def connection_made(self, transport):
        self.transport = transport
        if self.link.buffer_transform is None:
            self.link.on_connect(True, self)
        else:
            self.link.init_handshake(self)

    def connection_lost(self, transport):
        self.link.on_disconnect(self.handle, self)
        self.transport = None

    def data_received(self, data):
        Trace.trace("{} received {}", self.link.name, data)
        self.on_receive(data)

    def build_header(self, buffer, transformed):
        length = len(buffer)
        header = 1 if transformed else 0
        header = header | (length << 1)

        result = bytearray()
        Serializer.write_variable(result, header)
        return result

    def parse_header(self, deserializer):
        pos = deserializer.pos
        try:
            header, num_bytes = deserializer.read_variable32()
        except:
            return 0, 0, False
        finally:
            deserializer.pos = pos

        length = header >> 1
        transformed = ((header & 1) != 0)
        return num_bytes, length, transformed

    def _send(self, data):
        Trace.trace("{} sending {}", self.link.name, data)
        self.transport.write(data)
