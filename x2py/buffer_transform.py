# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from abc import ABC, abstractmethod

class BufferTransform(ABC):
    """ Defines methods to be implemented by concrete buffer transforms. """

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def clone(self):
        pass

    @abstractmethod
    def handshake_block_length(self):
        pass

    @abstractmethod
    def init_handshake(self):
        pass
    @abstractmethod
    def handshake(self, challenge):
        pass
    @abstractmethod
    def fini_handshake(self, response):
        pass

    @abstractmethod
    def transform(self, buffer, length):
        """ Transform the specified trailing byte(s) of the buffer. """
        pass
    @abstractmethod
    def inverse_transform(self, buffer, length):
        """ Inverse transform the specified leading byte(s) of the buffer. """
        pass

class BufferTransformStack(BufferTransform):
    """ Represents a single collective buffer transform that is actually a
        stacked set of child buffer transforms. """

    def __init__(self, transforms=None):
        self.transforms = []
        if transforms is None:
            return
        for transform in transforms:
            self.transforms.append(transform.clone())

    def add(self, transform):
        if transform not in self.transforms:
            self.transforms.append(transform)

    def remove(self, transform):
        self.transforms.remove(transform)

    def cleanup(self):
        for transform in self.transforms:
            transform.cleanup()
        self.transforms.clear()

    def clone(self):
        return BufferTransformStack(self.transforms)

    def handshake_block_length(self):
        result = 0
        for transform in self.transforms:
            result += transform.handshake_block_length()
        return result

    def init_handshake(self):
        result = bytearray()
        for transform in self.transforms:
            block = transform.init_handshake()
            if block:
                result += block
        return result

    def handshake(self, challenge):
        result = bytearray()
        offset = 0
        for transform in self.transforms:
            block_length = transform.handshake_block_length()
            if block_length:
                block = challenge[offset:offset + block_length]
                result += transform.handshake(block)
                offset += block_length
        return result

    def fini_handshake(self, response):
        offset = 0
        for transform in self.transforms:
            block_length = transform.handshake_block_length()
            if block_length:
                block = response[offset:offset + block_length]
                if not transform.fini_handshake(block):
                    return False
                offset += block_length
        return True

    def transform(self, buffer, length):
        for transform in self.transforms:
            length = transform.transform(buffer, length)
        return length

    def inverse_transform(self, buffer, length):
        for transform in reversed(self.transforms):
            length = transform.inverse_transform(buffer, length)
        return length
