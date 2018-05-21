# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

class TypeSpec(object):
    def __init__(self, typestr, details):
        self.typestr = typestr
        self.details = details  # list(TypeSpec)

    def metaprop(self, name):
        tokens = []
        tokens.append('MetaProperty(')
        if name is not None:
            tokens.append("'{}'".format(name))
        else:
            tokens.append('None')
        tokens.append(", {}".format(Types.get_type_index(self.typestr)))
        if not Types.is_builtin(self.typestr):
            tokens.append(", runtime_type={}".format(self.typestr))
        if self.details is not None and len(self.details) != 0:
            tokens.append(', details=[ ')
            for index, detail in enumerate(self.details):
                if index:
                    tokens.append(', ')
                tokens.append(detail.metaprop(None))
            tokens.append(' ]')
        tokens.append(')')
        return ''.join(tokens)

    def __str__(self):
        tokens = [ self.type ]
        if self.details is not None and len(self.details) != 0:
            tokens.append('(')
            for index, detail in enumerate(self.details):
                if index:
                    tokens.append(', ')
                tokens.append(str(detail))
            tokens.append(')')
        return ''.join(tokens)

class TypeProperty(object):
    def __init__(self, is_primitive, is_collection, detail_required, index):
        self.is_primitive = is_primitive
        self.is_collection = is_collection
        self.detail_required = detail_required
        self.index = index

def _init_types():
    result = {}
    # Primitive types
    result["bool"] = TypeProperty(True, False, False, 1)
    result["byte"] = TypeProperty(True, False, False, 2)
    result["int8"] = TypeProperty(True, False, False, 3)
    result["int16"] = TypeProperty(True, False, False, 4)
    result["int32"] = TypeProperty(True, False, False, 5)
    result["int64"] = TypeProperty(True, False, False, 6)
    result["float32"] = TypeProperty(True, False, False, 7)
    result["float64"] = TypeProperty(True, False, False, 8)
    result["string"] = TypeProperty(True, False, False, 9)
    result["datetime"] = TypeProperty(True, False, False, 10)
    # Collection types
    result["bytes"] = TypeProperty(False, True, False, 11)
    result["list"] = TypeProperty(False, True, True, 13)
    result["map"] = TypeProperty(False, True, True, 14)
    # Non-serializable
    result["object"] = TypeProperty(False, False, False, 15)
    return result

class Types(object):
    map = _init_types()

    @staticmethod
    def get_type_index(typestr):
        type_property = Types.map.get(typestr)
        return type_property.index if type_property is not None else 11

    @staticmethod
    def is_builtin(typestr):
        return typestr in Types.map

    @staticmethod
    def is_collection(typestr):
        type_property = Types.map.get(typestr)
        return type_property.is_collection if type_property is not None else False

    @staticmethod
    def is_primitive(typestr):
        type_property = Types.map.get(typestr)
        return type_property.is_primitive if type_property is not None else False

    @staticmethod
    def parse(s):
        typespec, index = Types._parse_typespec(s, 0)
        return typespec

    @staticmethod
    def _parse_typespec(s, index):
        typestr = None
        details = []
        back_margin = 0
        start = index
        length = len(s)
        while (index < length):
            c = s[index]
            if c == '(' and index < (length - 1):
                typestr = s[start:index].strip()
                index += 1
                details, index = Types._parse_details(s, index)
                back_margin = 1
                break
            elif c == ',':
                index += 1
                back_margin = 1
                break
            elif c == ')':
                break
            index += 1

        if typestr is None:
            typestr = s[start:index - back_margin].strip()
        typespec = None if len(typestr) == 0 else TypeSpec(typestr, details)
        return typespec, index

    @staticmethod
    def _parse_details(s, index):
        details = []
        length = len(s)
        while (index < length):
            c = s[index]
            if c == ',':
                continue
            if c == ')':
                index += 1
                break
            else:
                detail, index = Types._parse_typespec(s, index)
                if detail is not None:
                    details.append(detail)
                    index -= 1
            index += 1
        if len(details) == 0:
            details = None
        return details, index
