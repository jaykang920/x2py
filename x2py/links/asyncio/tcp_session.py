# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import asyncio

from ...deserializer import Deserializer
from ...event_factory import EventFactory
from ...hub import Hub
from ...serializer import Serializer
from ...util.trace import Trace

class TcpSession(asyncio.Protocol):
    def __init__(self, link):
        super().__init__()
        self.link = link
        self.transport = None
        self.rx_buffer = bytearray()

    def connection_made(self, transport):
        self.transport = transport
        self.link.on_connection_made(self, transport)

    def connection_lost(self, transport):
        self.link.on_connection_lost(self, self.transport)
        self.transport = None

    def data_received(self, data):
        Trace.trace("{} received {}", self.link.name, data)
        self.rx_buffer += data

        deserializer = Deserializer(self.rx_buffer)
        while True:
            try:
                header, num_bytes = deserializer.read_variable32()
            except BaseException as be:
                print(be)
                return

            length = header >> 1
            transformed = ((header & 1) != 0)

            if len(self.rx_buffer) < (length + num_bytes):
                return
            buffer = self.rx_buffer[num_bytes:num_bytes + length]
            self.rx_buffer = self.rx_buffer[num_bytes + length:]

            deserializer.buffer = buffer
            deserializer.pos = 0
            type_id = deserializer.read_int32(None)

            Trace.debug("{} {}", length, type_id)

            event = EventFactory.create(type_id)
            if event is None:
                continue
            event.deserialize(deserializer)

            Hub.post(event)

    def send(self, event):
        serializer = Serializer()
        Serializer.write_int32(serializer.buffer, None, event.type_id())
        event.serialize(serializer)

        length = len(serializer.buffer)
        transformed = False
        header = 1 if transformed else 0
        header = header | (length << 1)

        header_buffer = bytearray()
        Serializer.write_variable32(header_buffer, header)

        data = bytes(header_buffer + serializer.buffer)

        Trace.trace("{} sending {}", self.link.name, data)

        self.transport.write(data)
