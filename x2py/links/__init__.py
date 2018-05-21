# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

import sys

if sys.version_info.major >= 3:
    from x2py.links.asyncio import *
else:
    from x2py.links.asyncore import *
