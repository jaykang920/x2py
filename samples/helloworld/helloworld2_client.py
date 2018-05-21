# Copyright (c) 2017, 2018 Jae-jun Kang
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
        self.bind(HelloResp(), self.on_hello_resp)

    def on_hello_resp(self, resp):
        print(resp.message)

class MyClient(TcpClient):
    def __init__(self):
        super(MyClient, self).__init__("MyClient")
        self.buffer_transform = BlockCipher()

    def setup(self):
        self.bind(HelloReq(), self.send)
        self.connect('127.0.0.1', 8888)

x2.EventFactory.register_type(HelloResp)

(
x2.Hub.instance
    .attach(x2.SingleThreadFlow()
        .add(MyCase())
        .add(MyClient()))
)

with x2.Hub.Flows():
    while True:
        message = sys.stdin.readline().strip()
        if message in ('quit', 'exit'):
            break
        else:
            HelloReq().setattrs(
                name = message
            ).post()
