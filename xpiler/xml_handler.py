# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys
import xml.etree.ElementTree as etree

from definition import *
from handler import Handler
from types_ import *

class XmlHandler(Handler):
    def handle(self, path):
        unit = None
        try:
            tree = etree.parse(path)
        except etree.ParseError as err:
            print(err, file=sys.stderr)
            return False, unit

        root = tree.getroot()
        if root.tag != 'x2':
            # Not a valid x2 document.
            return True, unit

        unit = Unit()
        if 'namespace' in root.attrib:
            unit.namespace = root.attrib['namespace']
        if 'builtin' in root.attrib and root.attrib['builtin'].endswith('rue'):
            unit.is_builtin = True

        for node in root:
            if node.tag == 'references':
                if self._parse_references(unit, node) == False:
                    return False, unit
            elif node.tag == 'definitions':
                if self._parse_definitions(unit, node) == False:
                    return False, unit

        return True, unit

    def _parse_references(self, unit, node):
        for child in node:
            # Counts file references only
            if child.tag == 'file':
                ref = Reference(child.attrib['target'].strip())
                unit.references.append(ref)

    def _parse_definitions(self, unit, node):
        for child in node:
            if child.tag == 'consts':
                if self._parse_consts(unit, child) == False:
                    return False
            elif child.tag in ('cell', 'event'):
                if self._parse_cell(unit, child) == False:
                    return False

    def _parse_consts(self, unit, node):
        if 'name' not in node.attrib:
            return False
        name = node.attrib['name']
        if len(name) == 0:
            return False

        typestr = node.attrib['type'] if 'type' in node.attrib else 'int32'

        consts = Consts(name, typestr)

        for child in node:
            if child.tag == 'const':
                if self._parse_const(consts, child) == False:
                    return False

        unit.definitions.append(consts)
        return True

    def _parse_const(self, consts, node):
        if 'name' not in node.attrib:
            return False
        name = node.attrib['name']
        if len(name) == 0:
            return False

        const = Constant(name, node.text)
        consts.constants.append(const)
        return True

    def _parse_cell(self, unit, node):
        if 'name' not in node.attrib:
            return False
        name = node.attrib['name']
        if len(name) == 0:
            return False

        is_event = (node.tag == 'event')
        if is_event:
            if 'id' not in node.attrib:
                return False
            id = node.attrib['id']
            if len(id) == 0:
                return False

        cell = Event() if is_event else Cell()
        cell.name = name
        if is_event:
            cell.id = id
        cell.base = node.attrib['base'] if 'base' in node.attrib else ''

        if 'local' in node.attrib and node.attrib['local'].endswith('rue'):
            cell.local = True

        for child in node:
            if child.tag == 'property':
                if self._parse_property(cell, child) == False:
                    return False

        unit.definitions.append(cell)
        return True

    def _parse_property(self, cell, node):
        if ('name' not in node.attrib) or ('type' not in node.attrib):
            return False
        name = node.attrib['name']
        typestr = node.attrib['type']
        if len(name) == 0 or len(typestr) == 0:
            return False

        typespec = Types.parse(typestr)
        if typespec is None:
            return False

        default_value = node.text.strip() if node.text is not None else ''

        prop = Property(name, default_value)
        prop.typespec = typespec
        cell.properties.append(prop)
        return True
