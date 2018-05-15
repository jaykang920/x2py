# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from __future__ import print_function

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
        self.bind(HelloResp(), self.on_hello_resp)

    def on_hello_resp(self, resp):
        print(resp.message)

class MyClient(TcpClient):
    def __init__(self):
        super().__init__("MyClient")
        self.buffer_transform = BlockCipher()

    def setup(self):
        self.bind(HelloReq(), self.send)
        self.connect('127.0.0.1', 8888)

EventFactory.register_type(HelloResp)

(
Hub.instance
    .attach(SingleThreadFlow()
        .add(MyCase())
        .add(MyClient()))
)

with Hub.Flows():
    while True:
        message = sys.stdin.readline().strip()
        if message in ('quit', 'exit'):
            break
        else:
            HelloReq().setattrs(
                name = message
            ).post()
