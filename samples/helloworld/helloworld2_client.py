# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys

sys.path.append('../..')
from x2py import *

from x2py.transforms.inverse import Inverse

from hello_world import *

def trace_handler(level, message):
    print("x2 {} {}".format(level.name, message))

Trace.level = TraceLevel.ALL
Trace.handler = trace_handler

class MyHubCase(Hub.Case):
    pass

class MyCase(Case):
    def setup(self):
        super().setup()
        self.bind(HelloReq(), self.on_hello_req)

    def on_hello_req(self, e):
        pass


class MyClient(TcpClient):
    def __init__(self):
        super().__init__("MyClient")
        self.buffer_transform = Inverse()

    def setup(self):
        super().setup()
        Flow.bind(HelloReq(), self.send)
        self.connect('127.0.0.1', 8888)

EventFactory.register(2, HelloResp)

(
Hub.instance
    .insert(0, MyHubCase())
    .attach(SingleThreadFlow().add(MyClient()))
)

with Hub.Flows():
    while True:
        message = sys.stdin.readline().strip()
        if message in ('quit', 'exit'):
            break
        else:
            e = HelloReq()
            e.name = message
            Hub.post(e)

Hub.instance.detach_all()
