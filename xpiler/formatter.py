# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

class Formatter(object):
    def desc(self):
        raise NotImplementedError()

    def format(self, unit, out_dir):
        raise NotImplementedError()

    def is_up_to_date(self, path, out_dir):
        raise NotImplementedError()

class FormatterContext(object):
    def format_cell(self, definition):
        raise NotImplementedError()

    def format_consts(self, definition):
        raise NotImplementedError()

    def format_reference(self, reference):
        raise NotImplementedError()
