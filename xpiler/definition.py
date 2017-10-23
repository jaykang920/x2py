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
    def __init__(self, target=""):
        self.target = target

    def format(self, context):
        context.format_reference(self)

class Definition:
    def __init__(self, name=""):
        self.name = name

    def format(self, context):
        raise NotImplementedError()

class Constant:
    def __init__(self, name="", value=""):
        self.name = name
        self.value = value

class Consts(Definition):
    def __init__(self, name, type):
        super().__init__(name)
        self.type = type
        self.constants = []

    def format(self, context):
        context.format_consts(self)

class Property:
    def __init__(self, name="", default_value=""):
        self.index = 0
        self.name = name
        self.typespec = None
        self.default_value = default_value

class Cell(Definition):
    def __init__(self):
        super().__init__()
        self.base = ""
        self.base_class = ""
        self.is_event = False
        self.local = False
        self.properties = []

    def has_properties(self):
        return (len(self.properties) != 0)

    def format(self, context):
        context.format_cell(self)

class Event(Cell):
    def __init__(self):
        super().__init__()
        self.id = ""
        self.is_event = True