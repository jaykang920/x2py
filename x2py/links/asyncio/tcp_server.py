# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import asyncio
from threading import Thread

from ...util.trace import Trace

from ..server_link import ServerLink

from .tcp_session import TcpSession

class TcpServer(ServerLink):
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

    def _on_connect(self, result, context):
        super()._on_connect(result, context)
        if result:
            peername = context.transport.get_extra_info('peername')
            Trace.info("accepted from {}:{}", peername[0], peername[1])

    def _on_disconnect(self, handle, context):
        super()._on_disconnect(handle, context)
        peername = context.transport.get_extra_info('peername')
        Trace.info("disconnected from {}:{}", peername[0], peername[1])

    # protocol factory
    def __call__(self):
        return TcpSession(self)
