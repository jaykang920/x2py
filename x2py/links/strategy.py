# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

class LinkStrategy(object):
    """Common abstract base class for link strategies."""

    def __init__(self):
        self.link = None

    def setup(self):
        pass
    def teardown(self):
        pass

class SessionBasedLinkStrategy(LinkStrategy):
    """Common abstract base class for session-based link strategies."""

    def before_session_setup(self, link_session):
        pass
    def after_session_teardown(self, link_session):
        pass

class LinkSessionStrategy(object):
    """Common abstract base class for link session strategies."""

    def __init__(self):
        self.session = None

    def process(self, event):
        return False

class ChannelStrategy(SessionBasedLinkStrategy):
    """Common abstract base class for communication channel strategies."""

    class SubStrategy(LinkSessionStrategy):
        def release(self):
            pass
        def before_send(self, buffer):
            return False
        def after_receive(self, buffer):
            pass

    def init_handshake(self, link_session):
        pass
    def cleanup(self):
        pass

class HeartbeatStrategy(SessionBasedLinkStrategy):
    """Common abstract base class for heartbeat strategies."""

    class SubStrategy(LinkSessionStrategy):
        def __init__(self):
            self.marked = False

        def on_heartbeat(self):
            return False
        def on_receive(self):
            pass
        def on_send(self, event):
            pass

    def on_heartbeat(self):
        pass
