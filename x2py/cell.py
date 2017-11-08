# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from .fingerprint import Fingerprint
from .serializer import Serializer
from .util.hash import Hash

class MetaProperty:
    """ Represents runtime traits of a cell property. """

    BOOL = 1
    BYTE = 2
    INT8 = 3
    INT16 = 4
    INT32 = 5
    INT64 = 6
    FLOAT32 = 7
    FLOAT64 = 8
    STRING = 9
    DATETIME = 10
    BYTES = 11
    CELL = 12
    LIST = 13
    MAP = 14
    OBJECT = 15

    def __init__(self, name, type_index, factory_method=None, details=None):
        self.name = name
        self.type_index = type_index
        self.factory_method = factory_method
        self.details = details  # list of child MetaProperty objects

class Cell(object):
    """ Common base class for all custom types. """

    class Tag:
        def __init__(self, base, metaprops):
            self.base = base
            self.metaprops = metaprops
            self.offset = 0
            if base is not None:
                self.offset = base.offset + len(base.metaprops)

    tag = Tag(None, [])

    def __init__(self, length):
        self.fingerprint = Fingerprint(length)
        self.values = [None] * length  # property values

    def desc(self):
        prop_descs = []
        self._desc(self.type_tag(), prop_descs)
        result = ', '.join(prop_descs)
        result = "{} {{ {} }}".format(type(self).__name__, result)
        return result

    def _desc(self, tag, prop_descs):
        if tag.base is not None:
            self._desc(tag.base, prop_descs)
        if len(tag.metaprops) == 0:
            return
        for index, prop in enumerate(tag.metaprops):
            value = self.values[tag.offset + index]
            if prop.type_index == 9:
                value = '"' + value + '"'
            prop_descs.append('"{}": {}'.format(prop.name, value))

    def deserialize(self, deserializer):
        self.fingerprint.deserialize(deserializer)
        self._deserialize(self.type_tag(), deserializer)

    def _deserialize(self, tag, deserializer):
        if tag.base is not None:
            self._deserialize(tag.base, deserializer)
        if len(tag.metaprops) == 0:
            return
        base = tag.offset
        for index, prop in enumerate(tag.metaprops):
            if self.fingerprint.get(base + index):
                self.values[base + index] = deserializer.read(prop)

    def get_length(self):
        length = self.fingerprint.get_length()
        length += self._get_length(self.type_tag())
        return length

    def _get_length(self, tag):
        length = 0
        if tag.base is not None:
            length += self._get_length(tag.base)
        if len(tag.metaprops) == 0:
            return length
        base = tag.offset
        for index, prop in enumerate(tag.metaprops):
            if self.fingerprint.get(base + index):
                length += Serializer.get_length(prop, self.values[base + index])
        return length

    def type_tag(self):
        return Cell.tag

    def equals(self, other):
        if self is other:
            return True
        if type(self) != type(other):
            return False
        return self._equals(self.type_tag(), other)

    def _equals(self, tag, other):
        if tag.base is not None:
            if not self._equals(tag.base, other):
                return False
        if len(tag.metaprops) == 0:
            return True
        base = tag.offset
        for index, prop in enumerate(tag.metaprops):
            if self.values[base + index] != other.values[base + index]:
                return False
        return True

    def equivalent(self, other):
        if self is other:
            return True
        if not isinstance(self, type(other)):
            return False
        return self._equivalent(self.type_tag(), other)

    def _equivalent(self, tag, other):
        if tag.base is not None:
            if not self._equivalent(tag.base, other):
                return False
        if len(tag.metaprops) == 0:
            return True
        base = tag.offset
        for index, prop in enumerate(tag.metaprops):
            if other.fingerprint.get(base + index):
                if self.values[base + index] != other.values[base + index]:
                    return False
        return True

    def hash_code(self, fingerprint):
        h = Hash()
        self._hash_code(self.type_tag(), h, fingerprint)
        return h.code

    def _hash_code(self, tag, h, fingerprint):
        if tag.base is not None:
            self._hash_code(tag.base, h, fingerprint)
        if len(tag.metaprops) == 0:
            return
        base = tag.offset
        for index, prop in enumerate(tag.metaprops):
            if fingerprint.get(base + index):
                h.update(base + index)                     # property index
                h.update(hash(self.values[base + index]))  # property value

    def serialize(self, serializer):
        self.fingerprint.serialize(serializer)
        self._serialize(self.type_tag(), serializer)

    def _serialize(self, tag, serializer):
        if tag.base is not None:
            self._serialize(tag.base, serializer)
        if len(tag.metaprops) == 0:
            return
        base = tag.offset
        for index, prop in enumerate(tag.metaprops):
            if self.fingerprint.get(base + index):
                serializer.write(prop, self.values[base + index])

    def _set_property(self, index, value, type_index):
        print("type_index", type_index)
        self.fingerprint.touch(index)
        self.values[index] = value

    def __eq__(self, other):
        return other.equals(self)

    def __hash__(self):
        return self.hash_code(self.fingerprint)

    def __str__(self):
        return self.desc()
