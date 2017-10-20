# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

class Unit:
    """Represents a single definition unit."""

    def __init__(self):
        self.basename = ""
        self.namespace = ""
        self.references = []
        self.definitions = []

class Reference:
    def __init__(self):
        self.target = ""

    def format(self, context):
        context.format_reference(self)

class Definition:
    def __init__(self):
        self.name = ""

    def format(self, context):
        raise NotImplementedError()

class Constant:
    def __init__(self):
        self.name = ""
        self.value = ""

class Consts(Definition):
    def __init__(self):
        self.type = ""
        self.constants = []

    def format(self, context):
        context.format_consts(self)

class Property:
    def __init__(self):
        self.index = 0
        self.name = ""
        self.typespec
        self.default_value = ""

class Cell(Definition):
    def __init__(self):
        self.base = ""
        self.base_class = ""
        self.is_event = False
        self.properties = []

    def has_properties(self):
        return (len(self.properties) != 0)

    def format(self, context):
        context.format_cell(self)

class Event(Cell):
    def __init__(self):
        self.id = ""
        self.is_event = True