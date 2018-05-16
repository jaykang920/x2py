# auto-generated by x2py xpiler

from .cell import *
from .event import *

class BuiltinEventType(object):
    HEARTBEAT_EVENT = -1
    FLOW_START = -2
    FLOW_STOP = -3
    TIMEOUT_EVENT = -4
    PERIODIC_EVENT = -5

def _init_heartbeat_event_tag():
    props = []
    return Event.Tag(Event.tag, 'HeartbeatEvent', props,
        BuiltinEventType.HEARTBEAT_EVENT)

class HeartbeatEvent(Event):
    tag = _init_heartbeat_event_tag()

    def __init__(self, length=0):
        super(HeartbeatEvent, self).__init__(len(HeartbeatEvent.tag.props) + length)
        base = HeartbeatEvent.tag.offset
        pass

    def type_id(self):
        return HeartbeatEvent.tag.type_id

    def type_tag(self):
        return HeartbeatEvent.tag

def _init_flow_start_tag():
    props = []
    return Event.Tag(Event.tag, 'FlowStart', props,
        BuiltinEventType.FLOW_START)

class FlowStart(Event):
    tag = _init_flow_start_tag()

    def __init__(self, length=0):
        super(FlowStart, self).__init__(len(FlowStart.tag.props) + length)
        base = FlowStart.tag.offset
        pass

    def type_id(self):
        return FlowStart.tag.type_id

    def type_tag(self):
        return FlowStart.tag

def _init_flow_stop_tag():
    props = []
    return Event.Tag(Event.tag, 'FlowStop', props,
        BuiltinEventType.FLOW_STOP)

class FlowStop(Event):
    tag = _init_flow_stop_tag()

    def __init__(self, length=0):
        super(FlowStop, self).__init__(len(FlowStop.tag.props) + length)
        base = FlowStop.tag.offset
        pass

    def type_id(self):
        return FlowStop.tag.type_id

    def type_tag(self):
        return FlowStop.tag

def _init_timeout_event_tag():
    props = []
    props.append(MetaProperty('Key', 15))
    props.append(MetaProperty('IntParam', 5))
    return Event.Tag(Event.tag, 'TimeoutEvent', props,
        BuiltinEventType.TIMEOUT_EVENT)

class TimeoutEvent(Event):
    tag = _init_timeout_event_tag()

    def __init__(self, length=0):
        super(TimeoutEvent, self).__init__(len(TimeoutEvent.tag.props) + length)
        base = TimeoutEvent.tag.offset
        self.values[base + 0] = None
        self.values[base + 1] = 0

    @property
    def key(self):
        return self.values[TimeoutEvent.tag.offset + 0]
    @key.setter
    def key(self, value):
        self._set_property(TimeoutEvent.tag.offset + 0, value,
            TimeoutEvent.tag.props[0].type_index)

    @property
    def int_param(self):
        return self.values[TimeoutEvent.tag.offset + 1]
    @int_param.setter
    def int_param(self, value):
        self._set_property(TimeoutEvent.tag.offset + 1, value,
            TimeoutEvent.tag.props[1].type_index)

    def type_id(self):
        return TimeoutEvent.tag.type_id

    def type_tag(self):
        return TimeoutEvent.tag

def _init_periodic_event_tag():
    props = []
    props.append(MetaProperty('Key', 15))
    props.append(MetaProperty('IntParam', 5))
    return Event.Tag(Event.tag, 'PeriodicEvent', props,
        BuiltinEventType.PERIODIC_EVENT)

class PeriodicEvent(Event):
    tag = _init_periodic_event_tag()

    def __init__(self, length=0):
        super(PeriodicEvent, self).__init__(len(PeriodicEvent.tag.props) + length)
        base = PeriodicEvent.tag.offset
        self.values[base + 0] = None
        self.values[base + 1] = 0

    @property
    def key(self):
        return self.values[PeriodicEvent.tag.offset + 0]
    @key.setter
    def key(self, value):
        self._set_property(PeriodicEvent.tag.offset + 0, value,
            PeriodicEvent.tag.props[0].type_index)

    @property
    def int_param(self):
        return self.values[PeriodicEvent.tag.offset + 1]
    @int_param.setter
    def int_param(self, value):
        self._set_property(PeriodicEvent.tag.offset + 1, value,
            PeriodicEvent.tag.props[1].type_index)

    def type_id(self):
        return PeriodicEvent.tag.type_id

    def type_tag(self):
        return PeriodicEvent.tag
