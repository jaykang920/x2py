# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from ..deserializer import Deserializer
from ..event_factory import EventFactory
from ..hub import Hub
from ..serializer import Serializer
from ..util.trace import Trace

class LinkSession:
    """Abstract base class for concrete link sessions."""

    def __init__(self, link):  # link: SessionBasedLink
        self.link = link
        self.handle = 0
        self.polarity = False

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

            deserializer.buffer = buffer
            deserializer.pos = 0

            type_id = deserializer.read_int32(None)

            Trace.debug("{} {}", length, type_id)

            event = EventFactory.create(type_id)
            if event is None:
                continue
            event.deserialize(deserializer)

            event._handle = self.handle

            Hub.post(event)

    def send(self, event):
        serializer = Serializer()
        serializer.write_int32(None, event.type_id())
        event.serialize(serializer)

        header_buffer = self.build_header(serializer.buffer)

        data = bytes(header_buffer + serializer.buffer)

        self._send(data)
