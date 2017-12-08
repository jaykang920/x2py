# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys

sys.path.append('../..')
from x2py import *

from x2py.transforms.block_cipher import BlockCipher
from x2py.transforms.inverse import Inverse

from hello_world import *

Trace.level = TraceLevel.ALL
Trace.handler = lambda level, message: \
    print("x2 {} {}".format(level.name, message))

class MyCase(Case):
    def setup(self):
        self.bind(HelloReq(), self.on_hello_req)

    def on_hello_req(self, req):
        HelloResp().in_response_of(req).setattrs(
            message = "hello, {}".format(req.name)
        ).post()

class MyServer(TcpServer):
    def __init__(self):
        super().__init__("MyServer")
        self.buffer_transform = BlockCipher()

    def setup(self):
        self.bind(HelloResp(), self.send)
        self.listen('0.0.0.0', 8888)

EventFactory.register(1, HelloReq)

(
Hub.instance
    .attach(SingleThreadFlow()
        .add(MyCase())
        .add(MyServer()))
)

with Hub.Flows():
    while True:
        message = sys.stdin.readline().strip()
        if message in ('quit', 'exit'):
            break
        else:
            pass
