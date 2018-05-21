# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from __future__ import print_function

import keyword
import os
import re

from xpiler.formatter import *
from xpiler.types_ import Types

EXTENSION = ".py"
TAB = "    "

def _underscore(s):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)

def to_snake_case(s):
    return _underscore(s).lower()

def to_SCREAMING_SNAKE_CASE(s):
    return _underscore(s).upper()

def _init_native_types():
    result = {}
    result['bool'] = 'bool'
    result['byte'] = 'int'
    result['int8'] = 'int'
    result['int16'] = 'int'
    result['int32'] = 'int'
    result['int64'] = 'int'
    result['float32'] = 'float'
    result['float64'] = 'float'
    result['string'] = 'str'
    result['datetime'] = 'datetime'
    result['bytes'] = 'bytes'
    result['list'] = 'list'
    result['map'] = 'dict'
    return result

def _init_default_values():
    result = {}
    result['bool'] = 'False'
    result['byte'] = '0'
    result['int8'] = '0'
    result['int16'] = '0'
    result['int32'] = '0'
    result['int64'] = '0'
    result['float32'] = '0.0'
    result['float64'] = '0.0'
    result['string'] = ''
    result['datetime'] = 'datetime(1970, 1, 1)'
    return result

class Python3Formatter(Formatter):
    native_types = _init_native_types()
    default_values = _init_default_values()

    def desc(self):
        return "Python 3"

    def format(self, unit, out_dir):
        basename = to_snake_case(unit.basename)
        target = os.path.join(out_dir, basename + EXTENSION)
        context = Python3FormatterContext(unit, target)
        print(target)
        with open(target, 'w') as f:
            context.out = f
            self._format_head(context)
            self._format_body(context)
            f.flush()

    def is_up_to_date(self, path, out_dir):
        basename = os.path.splitext(os.path.basename(path))[0]
        target = os.path.join(out_dir, basename + EXTENSION)
        return (os.path.exists(target) and
            os.path.getmtime(target) >= os.path.getmtime(path))

    def _format_head(self, context):
        o = context.out
        o.write("# auto-generated by x2py xpiler\n")
        o.write("\n")
        if not context.unit.is_builtin:
            #o.write("import x2py\n")
            o.write("from x2py.cell import MetaProperty, Cell\n")
            o.write("from x2py.event import Event\n")
            o.write("\n")

        for reference in context.unit.references:
            reference.format(context)
        if len(context.unit.references) != 0:
            o.write("\n")

    def _format_body(self, context):
        o = context.out

        leading = True
        for index, definition in enumerate(context.unit.definitions):
            if index:
                o.write("\n")
            definition.format(context)

class Python3FormatterContext(FormatterContext):
    def __init__(self, unit, target):
        self.unit = unit
        self.target = target
        self.out = None

    def format_cell(self, definition):
        tag_type = 'Event' if definition.is_event else 'Cell'
        #if not self.unit.is_builtin:
        #    tag_type = 'x2py.' + tag_type

        definition.base_class = definition.base
        if definition.base_class is None or len(definition.base_class) == 0:
            definition.base = ''
            definition.base_class = tag_type

        self._preprocess_properties(definition)

        base_tag = definition.base_class
        if len(definition.base) == 0:
            base_tag = definition.base_class + '.tag' if definition.is_event else 'None'
        else:
            base_tag += '.tag'

        tag_initializer_name = '_init_' + to_snake_case(definition.name) + '_tag'
        self._out(0, "def {}():\n".format(tag_initializer_name))
        self._out(1, "props = []\n")
        for prop in definition.properties:
            self._out(1, "props.append({})\n".format(prop.typespec.metaprop(prop.name)))
        self._out(1, "return {}.Tag({}, '{}', props".format(tag_type, base_tag, definition.name))
        if definition.is_event:
            self.out.write(",\n")
            if '.' in definition.id:
                tokens = definition.id.split('.')
                tokens[-1] = to_SCREAMING_SNAKE_CASE(tokens[-1])
                definition.id = '.'.join(tokens)
            self._out(2, definition.id)
        self.out.write(")\n\n")

        self._out(0, "class {0}({1}):\n".format(definition.name, definition.base_class))

        self._out(1, "tag = {}()\n\n".format(tag_initializer_name))

        self._format_constructor(definition)
        self._format_properties(definition)
        self._format_methods(definition)

    def format_consts(self, definition):
        if definition.type == 'string':
            for constant in definition.constants:
                constant.value = '"' + constant.value + '"'

        self._out(0, "class {}(object):\n".format(definition.name))
        if definition.constants:
            for constant in definition.constants:
                self._out(1, "{0} = {1}\n".format(
                    to_SCREAMING_SNAKE_CASE(constant.name), constant.value))
        else:
            self._out(1, "pass\n")

    def format_reference(self, reference):
        tokens = reference.target.split('/')
        tokens[-1] = to_snake_case(tokens[-1])
        target = '.'.join(tokens)
        self._out(0, "from {} import *\n".format(target))

    def _preprocess_properties(self, definition):
        index = 0
        for prop in definition.properties:
            prop.index = index
            index += 1

            prop.native_name = to_snake_case(prop.name)
            prop.var_name = '_' + prop.native_name
            if keyword.iskeyword(prop.native_name):
                prop.native_name += '_'

            if Types.is_primitive(prop.typespec.typestr):
                if prop.default_value is None or len(prop.default_value) == 0:
                    prop.default_value = Python3Formatter.default_values[prop.typespec.typestr]
                if prop.typespec.typestr == 'string':
                    prop.default_value = '"' + prop.default_value + '"'
            else:
                prop.default_value = 'None'

            prop.native_type = self._format_typespec(prop.typespec)

    def _format_typespec(self, typespec):
        typestr = typespec.typestr
        if not Types.is_builtin(typestr):
            return typestr  # custom type
        if Types.is_primitive(typestr):
            return Python3Formatter.native_types[typestr]
        else:
            return self._format_collection_type(typespec)

    def _format_collection_type(self, typespec):
        tokens = [ typespec.typestr ]
        if typespec.details is not None:
            tokens.append('(')
            for index, detail in enumerate(typespec.details):
                if index:
                    tokens.append(', ')
                tokens.append(self._format_typespec(detail))
            tokens.append(')')
        return ''.join(tokens)

    def _format_constructor(self, definition):
        self._out(1, "def __init__(self, length=0):\n")
        self._out(2, "super({0}, self).__init__(len({0}.tag.props) + length)\n".format(definition.name))
        self._out(2, "base = {0}.tag.offset\n".format(definition.name))

        if definition.has_properties():
            for index, prop in enumerate(definition.properties):
                self._out(2, "self.values[base + {0}] = {1}\n".format(index, prop.default_value))
            self.out.write("\n")
        else:
            self._out(2, "pass\n")

    def _format_properties(self, definition):
        for index, prop in enumerate(definition.properties):
            if index:
                self.out.write("\n")

            self._out(1, "@property\n")
            self._out(1, "def {}(self):\n".format(prop.native_name))
            self._out(2, "return self.values[{}.tag.offset + {}]\n".format(definition.name, index))
            #self.out.write("\n")
            self._out(1, "@{}.setter\n".format(prop.native_name))
            self._out(1, "def {}(self, value):\n".format(prop.native_name))
            self._out(2, "self._set_property({}.tag.offset + {}, value,\n".format(definition.name, index))
            self._out(3, "{}.tag.props[{}].type_index)\n".format(definition.name, index))

    def _format_methods(self, definition):
        self._format_type(definition)

    def _format_type(self, definition):
        self.out.write("\n")
        self._out(1, "def type_id(self):\n")
        self._out(2, "return {}.tag.type_id\n".format(definition.name))
        self.out.write("\n")
        self._out(1, "def type_tag(self):\n")
        self._out(2, "return {}.tag\n".format(definition.name))

    def _out(self, indentation, s):
        self._indent(indentation)
        self.out.write(s)

    def _indent(self, indentation):
        for _ in range(indentation):
            self.out.write(TAB)
