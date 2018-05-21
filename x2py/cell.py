# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import datetime

from x2py.fingerprint import Fingerprint
from x2py.serializer import Serializer
from x2py.util.hash import Hash

class MetaProperty(object):
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
    OBJECT = 15  # not serializable

    def __init__(self, name, type_index, runtime_type=None, details=None):
        self.name = name
        self.type_index = type_index
        self.runtime_type = runtime_type
        self.details = details  # list of child MetaProperty objects

class Cell(object):
    """ Common base class for all custom types. """

    class Tag(object):
        def __init__(self, base, type_name, props):
            self.base = base
            self.type_name = type_name
            self.props = props
            self.offset = 0
            if base is not None:
                self.offset = base.offset + len(base.props)

    tag = Tag(None, 'Cell', [])

    def __init__(self, length):
        self.fingerprint = Fingerprint(length)
        self.values = [None] * length  # property values

    def desc(self):
        prop_descs = []
        tag = self.type_tag()
        self._desc(tag, prop_descs)
        result = ', '.join(prop_descs)
        result = "{} {{ {} }}".format(tag.type_name, result)
        return result

    def _desc(self, tag, prop_descs):
        if tag.base is not None:
            self._desc(tag.base, prop_descs)
        if len(tag.props) == 0:
            return
        for index, prop in enumerate(tag.props):
            if prop.name.startswith('_'):
                continue
            value = self.values[tag.offset + index]
            if prop.type_index == 9:
                value = '"' + value + '"'
            prop_descs.append('"{}": {}'.format(prop.name, repr(value)))

    def deserialize(self, deserializer):
        self.fingerprint.deserialize(deserializer)
        self._deserialize(self.type_tag(), deserializer)

    def _deserialize(self, tag, deserializer):
        if tag.base is not None:
            self._deserialize(tag.base, deserializer)
        if len(tag.props) == 0:
            return
        base = tag.offset
        for index, prop in enumerate(tag.props):
            if prop.name.startswith('_'):
                if prop.name == '_Handle':
                    continue
            if self.fingerprint.get(base + index):
                self.values[base + index] = deserializer.read(prop)

    def get_length(self, target_type=None):
        result = self.fingerprint.get_length()
        length, _ = self._get_length(self.type_tag(), target_type, True)
        result += length
        return result

    def _get_length(self, tag, target_type, flag):
        result = 0
        if tag.base is not None:
            length, flag = self._get_length(tag.base, target_type, flag)
            result += length
            if not flag:
                return result, flag
        if len(tag.props) == 0:
            return result, flag
        base = tag.offset
        for index, prop in enumerate(tag.props):
            if prop.name.startswith('_'):
                if prop.name == '_Handle':
                    continue
            if self.fingerprint.get(base + index):
                result += Serializer.get_length(prop, self.values[base + index])
        if (target_type is not None) and (target_type.__name__ == tag.type_name):
            flag = False
        return result, flag

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
        if len(tag.props) == 0:
            return True
        base = tag.offset
        for index, prop in enumerate(tag.props):
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
        if len(tag.props) == 0:
            return True
        base = tag.offset
        for index, prop in enumerate(tag.props):
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
        if len(tag.props) == 0:
            return
        base = tag.offset
        for index, prop in enumerate(tag.props):
            if fingerprint.get(base + index):
                h.update(base + index)                     # property index
                h.update(hash(self.values[base + index]))  # property value

    def serialize(self, serializer, target_type=None):
        self.fingerprint.serialize(serializer)
        self._serialize(self.type_tag(), serializer, target_type, True)

    def _serialize(self, tag, serializer, target_type, flag):
        if tag.base is not None:
            flag = self._serialize(tag.base, serializer, target_type, flag)
            if not flag:
                return flag
        if len(tag.props) == 0:
            return flag
        base = tag.offset
        for index, prop in enumerate(tag.props):
            if prop.name.startswith('_'):
                if prop.name == '_Handle':
                    continue
            if self.fingerprint.get(base + index):
                serializer.write(prop, self.values[base + index])
        if (target_type is not None) and (target_type.__name__ == tag.type_name):
            flag = False
        return flag

    def setattrs(self, **kwargs):
        """Sets multiple attributes of this cell object at once."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def __eq__(self, other):
        return other.equals(self)

    def __ne__(self, other):
        return not other.equals(self)

    def __hash__(self):
        return self.hash_code(self.fingerprint)

    def __str__(self):
        return self.desc()

    # Property type checkers

    @staticmethod
    def is_bool(value):
        if value == True or value == False:
            return True, value
        else:
            return False, value

    @staticmethod
    def is_byte(value):
        if not isinstance(value, int):
            try:
                value = int(value)
            except:
                return False, value
        if value < 0 or (2**8 - 1) < value:
            return False, value
        return True, value

    @staticmethod
    def is_int8(value):
        if not isinstance(value, int):
            try:
                value = int(value)
            except:
                return False, value
        if value < -(2**7) or (2**7 - 1) < value:
            return False, value
        return True, value

    @staticmethod
    def is_int16(value):
        if not isinstance(value, int):
            try:
                value = int(value)
            except:
                return False, value
        if value < -(2**15) or (2**15 - 1) < value:
            return False, value
        return True, value

    @staticmethod
    def is_int32(value):
        if not isinstance(value, int):
            try:
                value = int(value)
            except:
                return False, value
        if value < -(2**31) or (2**31 - 1) < value:
            return False, value
        return True, value

    @staticmethod
    def is_int64(value):
        if not isinstance(value, int):
            try:
                value = int(value)
            except:
                return False, value
        if value < -(2**63) or (2**63 - 1) < value:
            return False, value
        return True, value

    @staticmethod
    def is_float32(value):
        if not isinstance(value, float):
            try:
                value = float(value)
            except:
                return False, value
        return True, value

    @staticmethod
    def is_float64(value):
        if not isinstance(value, float):
            try:
                value = float(value)
            except:
                return False, value
        return True, value

    @staticmethod
    def is_string(value):
        if value is not None:  # allow None
            if not isinstance(value, str):
                try:
                    value = str(value)
                except:
                    return False, value
        return True, value

    @staticmethod
    def is_datetime(value):
        if not isinstance(value, datetime.datetime):
            try:
                value = datetime.datetime(value)
            except:
                return False, value
        return True, value

    @staticmethod
    def is_bytes(value):
        if value is not None:  # allow None
            if not isinstance(value, bytes):
                try:
                    value = bytes(value)
                except:
                    return False, value
        return True, value

    @staticmethod
    def is_cell(value):
        if value is not None:  # allow None
            if not isinstance(value, Cell):
                return False, value
        return True, value

    @staticmethod
    def is_list(value):
        if value is not None:  # allow None
            if not isinstance(value, list):
                return False, value
        return True, value

    @staticmethod
    def is_map(value):
        if value is not None:  # allow None
            if not isinstance(value, dict):
                return False, value
        return True, value

    @staticmethod
    def is_object(value):
        return True, value

    # Property type checker function table
    checkers = [
        None,
        is_bool,
        is_byte,
        is_int8,
        is_int16,
        is_int32,
        is_int64,
        is_float32,
        is_float64,
        is_string,
        is_datetime,
        is_bytes,
        is_cell,
        is_list,
        is_map,
        is_object
    ]

    def _set_property(self, index, value, type_index):
        checker = Cell.checkers[type_index]
        valid, value = checker.__func__(value)
        if not valid:
            raise ValueError()
        if value is not None:
            self.fingerprint.touch(index)
        self.values[index] = value
