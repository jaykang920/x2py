# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

import asyncio

from x2py.deserializer import Deserializer
from x2py.serializer import Serializer
from x2py.util.trace import Trace
from x2py.links.link_session import LinkSession

class TcpSession(LinkSession, asyncio.Protocol):
    def __init__(self, link):
        LinkSession.__init__(self, link)
        asyncio.Protocol.__init__(self)
        self.transport = None

    def cleanup(self):
        super(TcpSession, self).cleanup()
        self.transport.close()

    def connected(self):
        if self.transport is not None:
            if self.transport._sock is not None:
                return (self.transport._sock.fileno() >= 0)
        return False

    def connection_made(self, transport):
        self.transport = transport
        self.link.init_session(self)

    def connection_lost(self, exc=None):
        self.link.on_disconnect(self.handle, self)
        self.transport = None
        super(TcpSession, self).connection_lost(exc)

    def data_received(self, data):
        if not data:
            self.connection_lost(self.transport)
            return
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
