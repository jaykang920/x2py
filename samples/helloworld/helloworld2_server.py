# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from __future__ import print_function

import sys

sys.path.append('../..')

import x2py as x2

from x2py.links import *
from x2py.transforms.block_cipher import BlockCipher

from hello_world import *

x2.Trace.level = x2.TraceLevel.ALL
x2.Trace.handler = staticmethod(lambda level, message: \
    print("x2 {} {}".format(x2.TraceLevel.name(level), message)))

class MyCase(x2.Case):
    def setup(self):
        self.bind(HelloReq(), self.on_hello_req)

    def on_hello_req(self, req):
        HelloResp().in_response_of(req).setattrs(
            message = "hello, {}".format(req.name)
        ).post()

class MyServer(TcpServer):
    def __init__(self):
        super(MyServer, self).__init__("MyServer")
        self.buffer_transform = BlockCipher()

    def setup(self):
        self.bind(HelloResp(), self.send)
        self.listen('0.0.0.0', 8888)

x2.EventFactory.register_type(HelloReq)

(
x2.Hub.instance
    .attach(x2.SingleThreadFlow()
        .add(MyCase())
        .add(MyServer()))
)

with x2.Hub.Flows():
    while True:
        message = sys.stdin.readline().strip()
        if message in ('quit', 'exit'):
            break
        else:
            pass
