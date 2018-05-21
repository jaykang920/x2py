# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from __future__ import print_function

import sys

sys.path.append('../..')

import x2py as x2

from hello_world import *

x2.Trace.level = x2.TraceLevel.ALL
x2.Trace.handler = staticmethod(lambda level, message: \
    print("x2 {} {}".format(x2.TraceLevel.name(level), message)))

class MyCase(x2.Case):
    def setup(self):
        self.bind(HelloReq(), self.on_hello_req)
        self.bind(HelloResp(), self.on_hello_resp)

    def on_hello_req(self, req):
        HelloResp().in_response_of(req).setattrs(
            message = "hello, {}".format(req.name)
        ).post()

    def on_hello_resp(self, resp):
        print(resp.message)

(
x2.Hub.instance
    .attach(x2.SingleThreadFlow()
        .add(MyCase()))
)

with x2.Hub.Flows():
    while True:
        message = sys.stdin.readline().strip()
        if message in ('quit', 'exit'):
            break
        else:
            HelloReq().setattrs(
                name=message
            ).post()
