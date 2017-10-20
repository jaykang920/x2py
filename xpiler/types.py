# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

class TypeSpec:
    def __init__(self):
        self.type = ""
        self.details = []  # list(TypeSpec)

class TypeProperty:
    def __init__(self, is_primitive=False, is_collection=False, detail_required=False):
        self.is_primitive = is_primitive
        self.is_collection = is_collection
        self.detail_required = detail_required

def _init_types():
    result = {}
    result["bool"] = TypeProperty(True, False, False)
    result["byte"] = TypeProperty(True, False, False)
    return result

class Types:
    types = _init_types()


