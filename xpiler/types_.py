# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

class TypeSpec:
    def __init__(self, typestr, details):
        self.typestr = typestr
        self.details = details  # list(TypeSpec)

    def __str__(self):
        tokens = [ self.type ]
        if (self.details is not None and len(self.details) != 0):
            tokens.append('(')
            for index, detail in enumerate(self.details):
                if index:
                    tokens.append(', ')
                tokens.append(str(detail))
            tokens.append(')')
        return ''.join(tokens)

class TypeProperty:
    def __init__(self, is_primitive=False, is_collection=False, detail_required=False):
        self.is_primitive = is_primitive
        self.is_collection = is_collection
        self.detail_required = detail_required

def _init_types():
    result = {}
    # Primitive types
    result["bool"] = TypeProperty(True, False, False)
    result["byte"] = TypeProperty(True, False, False)
    result["int8"] = TypeProperty(True, False, False)
    result["int16"] = TypeProperty(True, False, False)
    result["int32"] = TypeProperty(True, False, False)
    result["int64"] = TypeProperty(True, False, False)
    result["float32"] = TypeProperty(True, False, False)
    result["float64"] = TypeProperty(True, False, False)
    result["string"] = TypeProperty(True, False, False)
    result["datetime"] = TypeProperty(True, False, False)
    # Collection types
    result["bytes"] = TypeProperty(False, True, False)
    result["list"] = TypeProperty(False, True, True)
    result["map"] = TypeProperty(False, True, True)
    return result

class Types:
    map = _init_types()

    @staticmethod
    def is_builtin(typestr):
        return typestr in Types.map

    @staticmethod
    def is_collection(typestr):
        try:
            type_property = Types.map[typestr]
        except KeyError:
            return False
        return type_property.is_collection

    @staticmethod
    def is_primitive(typestr):
        try:
            type_property = Types.map[typestr]
        except KeyError:
            return False
        return type_property.is_primitive

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
            if (c == '(' and index < (length - 1)):
                typestr = s[start:index].strip()
                index += 1
                details, index = Types._parse_details(s, index)
                back_margin = 1
                break
            elif (c == ','):
                index += 1
                back_margin = 1
                break
            elif (c == ')'):
                break
            index += 1

        if (typestr is None):
            typestr = s[start:index - back_margin].strip()
        typespec = None if len(typestr) == 0 else TypeSpec(typestr, details)
        return typespec, index

    @staticmethod
    def _parse_details(s, index):
        details = []
        length = len(s)
        while (index < length):
            c = s[index]
            if (c == ','):
                continue
            if (c == ')'):
                index += 1
                break
            else:
                detail, index = Types._parse_typespec(s, index)
                if (detail is not None):
                    details.append(detail)
                    index -= 1
            index += 1
        if (len(details) == 0):
            details = None
        return details, index
