# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import asyncore
import socket
from threading import Thread

from x2py.util.trace import Trace
from x2py.links.server_link import ServerLink
from x2py.links.asyncore.tcp_session import TcpSession

class TcpServer(ServerLink):
    """ TCP/IP server link based on the asyncore module. """

    class Dispatcher(asyncore.dispatcher):
        def __init__(self, owner):
            asyncore.dispatcher.__init__(self, map=owner.map)
            self.owner = owner
        def handle_accept(self):
            self.owner.handle_accept()

    def __init__(self, name):
        super(TcpServer, self).__init__(name)
        self.map = {}
        self.dispatcher = TcpServer.Dispatcher(self)
        self.thread = Thread(target=self._loop)

    def cleanup(self):
        asyncore.close_all(map=self.map)
        self.dispatcher.close()

        self.thread.join()

        super(TcpServer, self).cleanup()

    def listen(self, host, port):
        self.dispatcher.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dispatcher.bind((host, port))
        self.dispatcher.listen(5)

        Trace.info("listening on {}:{}", host, port)

        self.thread.start()

    def handle_accept(self):
        pair = self.dispatcher.accept()
        if pair is not None:
            sock, addr = pair
            session = TcpSession(self, sock)
            session.connection_made()

    def _loop(self):
        asyncore.loop(map=self.map)

    def _on_connect(self, result, context):
        super(TcpServer, self)._on_connect(result, context)
        if result:
            peername = context.socket.getpeername()
            Trace.info("accepted from {}:{}", peername[0], peername[1])
            context.peername = peername

    def _on_disconnect(self, handle, context):
        super(TcpServer, self)._on_disconnect(handle, context)
        peername = context.peername
        Trace.info("disconnected from {}:{}", peername[0], peername[1])
