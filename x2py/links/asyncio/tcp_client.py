# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import asyncio
from threading import Thread

from .tcp_session import TcpSession
from ...link import Link
from ...util.trace import Trace

class TcpClient(Link):
    def __init__(self, name):
        super().__init__(name)
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self.loop.run_forever)
        self.session = None

    def cleanup(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

        self.thread.join()

        self.loop.close()

        super().cleanup()

    def connect(self, host, port):
        Trace.info("connecting to {}:{}", host, port)
        factory = self.loop.create_connection(self, host, port)
        transport, protocol = self.loop.run_until_complete(factory)

        self.thread.start()

    def on_connection_made(self, protocol, transport):
        self.session = protocol
        socket = transport.get_extra_info('peername')
        Trace.info("connected to {}:{}", socket[0], socket[1])

    def on_connection_lost(self, protocol, transport):
        self.session = None
        socket = transport.get_extra_info('peername')
        Trace.info("disconnected from {}:{}", socket[0], socket[1])

    def send(self, event):
        if self.session is not None:
            self.session.send(event)

    # protocol factory
    def __call__(self):
        return TcpSession(self)
