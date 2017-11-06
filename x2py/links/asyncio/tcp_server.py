# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import asyncio
from threading import Thread

from .tcp_session import TcpSession
from ...link import Link
from ...util.trace import Trace

class TcpServer(Link):
    def __init__(self, name):
        super().__init__(name)
        self.loop = asyncio.new_event_loop()
        self.server = None
        self.thread = Thread(target=self.loop.run_forever)

    def cleanup(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

        self.thread.join()

        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())

        #self.loop.close()

        super().cleanup()

    def listen(self, host, port):
        factory = self.loop.create_server(self, host, port)
        self.server = self.loop.run_until_complete(factory)

        Trace.info("listening on {}:{}", host, port)

        self.thread.start()

    def on_connection_made(self, protocol, transport):
        peername = transport.get_extra_info('peername')
        Trace.info("accepted from {}:{}", peername[0], peername[1])

    def on_connection_lost(self, protocol, transport):
        peername = transport.get_extra_info('peername')
        Trace.info("disconnected from {}:{}", peername[0], peername[1])

    # protocol factory
    def __call__(self):
        return TcpSession(self)

