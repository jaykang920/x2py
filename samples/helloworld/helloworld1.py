# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from __future__ import print_function

import sys

sys.path.append('../..')
from x2py import *

from hello_world import *

Trace.level = TraceLevel.ALL
Trace.handler = lambda level, message: \
    print("x2 {} {}".format(level.name, message))

class MyCase(Case):
    def setup(self):
        self.bind(HelloReq(), self.on_hello_req)
        self.bind(HelloResp(), self.on_hello_resp)

    def on_hello_req(self, req):
        HelloResp().in_response_of(req).setattrs(
            message = "hello, {}".format(req.name)
        ).post()

    def on_hello_resp(self, resp):
        print(resp.message)

Hub.instance.attach(SingleThreadFlow().add(MyCase()))

with Hub.Flows():
    while True:
        message = sys.stdin.readline().strip()
        if message in ('quit', 'exit'):
            break
        else:
            HelloReq().setattrs(
                name=message
            ).post()
