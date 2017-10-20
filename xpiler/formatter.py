# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

class Formatter:
    def desc(self):
        raise NotImplementedError()

    def format(self, unit, out_dir):
        raise NotImplementedError()

    def is_up_to_date(self, path, out_dir):
        raise NotImplementedError()

class FormatterContext:
    def format_cell(self, cell_def):
        raise NotImplementedError()

    def format_consts(self, consts__def):
        raise NotImplementedError()

    def format_reference(self, reference):
        raise NotImplementedError()
