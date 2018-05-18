# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from __future__ import print_function

import sys

sys.path.append('../..')
from x2py import *

if sys.version_info.major >= 3:
    from x2py.links.asyncio import TcpServer
else:
    from x2py.links.asyncore import TcpServer
from x2py.transforms.block_cipher import BlockCipher
from x2py.transforms.inverse import Inverse

from hello_world import *

Trace.level = TraceLevel.ALL
Trace.handler = staticmethod(lambda level, message: \
    print("x2 {} {}".format(TraceLevel.name(level), message)))

class MyCase(Case):
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

EventFactory.register_type(HelloReq)

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
