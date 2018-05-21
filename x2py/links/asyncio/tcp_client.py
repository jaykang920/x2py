# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import asyncio
from threading import Thread

from x2py.util.trace import Trace
from x2py.links.client_link import ClientLink
from x2py.links.asyncio.tcp_session import TcpSession

class TcpClient(ClientLink):
    def __init__(self, name):
        super(TcpClient, self).__init__(name)
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self.loop.run_forever)
        self.session = None
        self.remote_host = ''
        self.remote_port = 0

    def cleanup(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

        self.thread.join()

        self.loop.close()

        super(TcpClient, self).cleanup()

    def connect(self, host, port):
        self.remote_host = host
        self.remote_port = port
        Trace.info("connecting to {}:{}", host, port)
        factory = self.loop.create_connection(self, host, port)
        transport, protocol = self.loop.run_until_complete(factory)

        self.thread.start()

    def _on_connect(self, result, context):
        super(TcpClient, self)._on_connect(result, context)
        if result:
            peername = context.transport.get_extra_info('peername')
            Trace.info("connected to {}:{}", peername[0], peername[1])
        else:
            Trace.error("error connecting to {}:{}", self.remote_host, self.remote_port)

    def _on_disconnect(self, handle, context):
        super(TcpClient, self)._on_disconnect(handle, context)
        peername = context.transport.get_extra_info('peername')
        Trace.info("disconnected from {}:{}", peername[0], peername[1])

    # protocol factory
    def __call__(self):
        return TcpSession(self)
