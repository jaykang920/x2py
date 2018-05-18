import sys

if sys.version_info.major >= 3:
    from .asyncio import *
else:
    from .asyncore import *

