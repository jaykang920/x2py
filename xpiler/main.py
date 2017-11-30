# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import os
import sys

from .options import Options

def _init_handlers():
    result = {}
    from xpiler.xml_handler import XmlHandler
    result['.xml'] = XmlHandler()
    return result

def _init_formatters():
    result = {}
    from xpiler.python3_formatter import Python3Formatter
    result['py'] = Python3Formatter()
    return result

class Main:
    handlers = _init_handlers()
    formatters = _init_formatters()
    options = Options()

    def __init__(self):
        self.formatter = Main.formatters[Main.options.spec]
        self.subdirs = []
        self.error = False

    @staticmethod
    def main(argv):
        args = Main.options.parse(argv[1:])
        if len(args) < 1:
            print("error: at least one input path is required", file=sys.stderr)
            sys.exit(2)

        main = Main()
        for path in args:
            main.process(path)
        return 1 if main.error else 0

    def process(self, path):
        if os.path.isdir(path):
            self._process_dir(path)
        elif os.path.isfile(path):
            self._process_file(path)
        else:
            print(path + " doesn't exist.", file=sys.stderr)
            self.error = True

    def _process_dir(self, path):
        print("Directory " + os.path.abspath(path))
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            if os.path.isdir(entry_path):
                if Main.options.recursive:
                    self.subdirs.append(entry)
                    self._process_dir(entry_path)
                    self.subdirs.pop()
            else:
                self._process_file(entry_path)

    def _process_file(self, path):
        filename = os.path.basename(path)
        basename, extension = os.path.splitext(filename)

        if Main.options.out_dir is None:
            out_dir = os.path.dirname(path)
        else:
            out_dir = os.path.join(Main.options.out_dir, os.path.sep.join(self.subdirs))

        if (extension.lower() not in Main.handlers) or (not Main.options.forced
                and self.formatter.is_up_to_date(path, out_dir)):
            return

        print(filename)

        handler = Main.handlers[extension.lower()]
        result, unit = handler.handle(path)
        if result == False:
            self.error = True
        if self.error or unit is None:
            return

        unit.basename = basename

        if (out_dir and len(out_dir) != 0) and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        result = self.formatter.format(unit, out_dir)
        if result == False:
            self.error = True
