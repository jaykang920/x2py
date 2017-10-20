# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import os

from formatter import Formatter

EXTENSION = ".py"

class Python3Formatter(Formatter):
    def desc(self):
        return "Python 3"

    def format(self, unit, out_dir):
        pass

    def is_up_to_date(self, path, out_dir):
        basename = os.path.basename(path).splitext()[0]
        target = os.path.join(out_dir, basename + EXTENSION)
        return (os.path.exists(target) and
            os.path.getmtime(target) >= os.path.getmtime(path))
