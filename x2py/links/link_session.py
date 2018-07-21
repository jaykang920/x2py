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
        self.rx_buffer = bytearray()
        self.channel_strategy = None
        self.heartbeat_strategy = None

    @property
    def has_channel_strategy(self):
        return (self.channel_strategy is not None)

    @property
    def has_heartbeat_strategy(self):
        return (self.heartbeat_strategy is not None)

    def cleanup(self):
        if self.has_channel_strategy:
            self.channel_strategy.cleanup()

    def close(self):
        self.cleanup()

    def on_receive(self, data):
        if self.has_heartbeat_strategy:
            self.heartbeat_strategy.on_receive()

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

            if self.has_channel_strategy and transformed:
                try:
                    buffer = self.channel_strategy.after_receive(buffer)
                except Exception as ex:
                    Trace.error("{} inverse transform error {}", self.link.name, ex)
                    continue

            deserializer.buffer = buffer
            deserializer.pos = 0

            type_id = deserializer.read_int32(None)

            event = self.link.create_event(type_id)
            if event is None:
                Trace.Error("unknown event type id {}", type_id)
                continue
            event.deserialize(deserializer)

            Trace.debug("{} received {}", self.link.name, event)

            processed = False

            if self.has_channel_strategy:
                processed = self.channel_strategy.process(event)
            elif not processed and self.has_heartbeat_strategy:
                processed = self.heartbeat_strategy.process(event)
            elif not processed:
                processed = self._process(event)

            if not processed:
                event._handle = self.handle
                Hub.post(event)

    def _process(self, event):
        return False

    def send(self, event):
        serializer = Serializer()
        serializer.write_int32(None, event.type_id())
        event.serialize(serializer)
        buffer = serializer.buffer

        transformed = False
        if self.has_channel_strategy and event._transform:
            transformed, buffer = self.channel_strategy.before_send(buffer)

        header_buffer = self.build_header(buffer, transformed)

        data = bytes(header_buffer + buffer)

        if self.has_heartbeat_strategy:
            self.heartbeat_strategy.on_send(event)

        self._send(data)
