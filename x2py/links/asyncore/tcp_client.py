# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

import asyncore
import errno
import socket
from threading import Thread

from x2py.util.trace import Trace
from x2py.links.client_link import ClientLink
from x2py.links.asyncore.tcp_session import TcpSession

class TcpClient(ClientLink):
    """ TCP/IP client link based on the asyncore module. """

    class Dispatcher(asyncore.dispatcher):
        def __init__(self, owner):
            asyncore.dispatcher.__init__(self, map=owner.map)
            self.owner = owner
        def handle_connect(self):
            self.owner.handle_connect()
        def handle_close(self):
            self.owner.handle_close()
        def handle_error(self):
            self.owner.handle_error()

    def __init__(self, name):
        super(TcpClient, self).__init__(name)
        self.map = {}
        self.dispatcher = TcpClient.Dispatcher(self)
        self.thread = Thread(target=self._loop)
        self.session = None
        self.remote_host = ''
        self.remote_port = 0
        self.connecting = False

    def cleanup(self):
        asyncore.close_all(map=self.map)

        self.thread.join()

        super(TcpClient, self).cleanup()

    def connect(self, host, port):
        self.connecting = True
        self.remote_host = host
        self.remote_port = port
        Trace.info("connecting to {}:{}", host, port)
        self.dispatcher.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dispatcher.connect((host, port))

        self.thread.start()

    def handle_connect(self):
        self.sesison = TcpSession(self, self.dispatcher.socket)
        self.sesison.connection_made()

    def handle_close(self):
        self.handle_error()
        self.dispatcher.close()

    def handle_error(self):
        err = self.dispatcher.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if self.connecting:
            Trace.error("connect error {}", errno.errorcode[err])
            self.connecting = False
            return
        Trace.error("error {}", errno.errorcode[err])

    def _loop(self):
        asyncore.loop(map=self.map)

    def _on_connect(self, result, context):
        super(TcpClient, self)._on_connect(result, context)
        if result:
            peername = context.socket.getpeername()
            Trace.info("connected to {}:{}", peername[0], peername[1])
            context.peername = peername
        else:
            Trace.error("error connecting to {}:{}", self.remote_host, self.remote_port)

    def _on_disconnect(self, handle, context):
        super(TcpClient, self)._on_disconnect(handle, context)
        peername = context.peername
        Trace.info("disconnected from {}:{}", peername[0], peername[1])
