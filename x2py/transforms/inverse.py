# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from x2py.buffer_transform import BufferTransform

class Inverse(BufferTransform):
    """A trivial example of BufferTransform that just invert every bit."""

    def cleanup(self):
        pass

    def clone(self):
        return Inverse()

    def handshake_block_length(self):
        return 0

    def init_handshake(self):
        return None
    def handshake(self, challenge):
        return None
    def fini_handshake(self, response):
        return True

    def transform(self, buffer):
        result = bytearray()
        for b in buffer:
            result.append(~b & 0x0ff)
        return result
    def inverse_transform(self, buffer):
        result = bytearray()
        for b in buffer:
            result.append(~b & 0x0ff)
        return result
