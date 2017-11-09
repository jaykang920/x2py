# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys

sys.path.append('../..')
from x2py import *

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
        self.bind(NumReq(), self.on_num_req)

    def on_num_req(self, e):
        #print("hello, {}".format(e.name))
        pass


class MyClient(TcpClient):
    def __init__(self):
        super().__init__("MyClient")

    def setup(self):
        super().setup()
        Flow.bind(NumReq(), self.send)
        self.connect('127.0.0.1', 8888)

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
            e = NumReq()
            e.value = 1
            Hub.post(e)

Hub.instance.detach_all()
