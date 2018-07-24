# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

class Config(object):
    heartbeat_interval = 5  # in seconds

    class Coroutine(object):
        default_timeout = 60 # in seconds