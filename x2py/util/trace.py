# Copyright (c) 2017 Jae-jun Kang
# See the file LICENSE for details.

from enum import IntEnum

class TraceLevel(IntEnum):
    ALL = 0
    TRACE = 1
    DEBUG = 2
    INFO = 3
    WARNING = 4
    ERROR = 5
    NONE = 6

class Trace(object):
    """ Represents the tracing helper class. """

    handler = None
    level = TraceLevel.INFO

    def __init__(self):
        raise AssertionError()

    @staticmethod
    def emit(level, message):
        if Trace.handler is None or Trace.level > level:
            return
        Trace.handler(level, message)
    @staticmethod
    def emit(level, format_string, *args, **kwargs):
        if Trace.handler is None or Trace.level > level:
            return
        Trace.handler(level, format_string.format(*args, **kwargs))

    @staticmethod
    def trace(message):
        Trace.emit(TraceLevel.TRACE, message)
    @staticmethod
    def trace(format_string, *args, **kwargs):
        Trace.emit(TraceLevel.TRACE, format_string, *args, **kwargs)

    @staticmethod
    def debug(message):
        Trace.emit(TraceLevel.DEBUG, message)
    @staticmethod
    def debug(format_string, *args, **kwargs):
        Trace.emit(TraceLevel.DEBUG, format_string, *args, **kwargs)

    @staticmethod
    def info(message):
        Trace.emit(TraceLevel.INFO, message)
    @staticmethod
    def info(format_string, *args, **kwargs):
        Trace.emit(TraceLevel.INFO, format_string, *args, **kwargs)

    @staticmethod
    def warn(message):
        Trace.emit(TraceLevel.WARNING, message)
    @staticmethod
    def warn(format_string, *args, **kwargs):
        Trace.emit(TraceLevel.WARNING, format_string, *args, **kwargs)

    @staticmethod
    def error(message):
        Trace.emit(TraceLevel.ERROR, message)
    @staticmethod
    def error(format_string, *args, **kwargs):
        Trace.emit(TraceLevel.ERROR, format_string, *args, **kwargs)
