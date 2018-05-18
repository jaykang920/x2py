# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import asyncore
import socket

from ...deserializer import Deserializer
from ...serializer import Serializer
from ...util.trace import Trace

from ..link_session import LinkSession

class TcpSession(LinkSession):
    """ TCP/IP link session based on the asyncore module. """

    class Dispatcher(asyncore.dispatcher_with_send):
        def __init__(self, owner, sock, map):
            asyncore.dispatcher_with_send.__init__(self, sock, map)
            self.owner = owner
        def handle_read(self):
            self.owner.handle_read()

    def __init__(self, link, sock):
        super(TcpSession, self).__init__(link)
        self.dispatcher = TcpSession.Dispatcher(self, sock, link.map)
        self.socket = sock

        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

    def cleanup(self):
        super(TcpSession, self).cleanup()

    def handle_read(self):
        data = self.dispatcher.recv(4096)
        if not data:
            self.connection_lost()
            return
        Trace.trace("{} received {}", self.link.name, repr(data))
        self.on_receive(data)

    def connection_made(self):
        if self.link.buffer_transform is None:
            self.link.on_connect(True, self)
        else:
            self.link.init_handshake(self)

    def connection_lost(self):
        self.link.on_disconnect(self.handle, self)

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
        Trace.trace("{} sending {}", self.link.name, repr(data))
        self.dispatcher.send(data)
