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


class MyServer(TcpServer):
    def __init__(self):
        super().__init__("MyServer")
    def setup(self):
        super().setup()
        self.listen('0.0.0.0', 8888)

EventFactory.register(3, NumReq)

(
Hub.instance
    .insert(0, MyHubCase())
    .attach(SingleThreadFlow().add(MyServer()))
)

with Hub.Flows():
    while True:
        message = sys.stdin.readline().strip()
        if message in ('quit', 'exit'):
            break
        else:
            pass

Hub.instance.detach_all()
