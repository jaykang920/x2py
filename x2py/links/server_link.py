# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.links.session_based_link import SessionBasedLink

class ServerLink(SessionBasedLink):
    def __init__(self, name):
        super(ServerLink, self).__init__(name)
        self.sessions = {}

    def cleanup(self):
        super(ServerLink, self).cleanup()

    def send(self, event):
        handle = event._handle
        if handle == 0:
            return
        with self.rwlock.rlock():
            session = self.sessions.get(handle)
        if session is not None:
            session.send(event)

    def _on_connect(self, result, context):
        super(ServerLink, self)._on_connect(result, context)
        if result:
            session = context
            with self.rwlock.wlock():
                self.sessions[session.handle] = session

    def _on_disconnect(self, handle, context):
        super(ServerLink, self)._on_disconnect(handle, context)
        session = context
        with self.rwlock.wlock():
            self.sessions.pop(session.handle)
