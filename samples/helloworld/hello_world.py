# auto-generated by x2py xpiler

from x2py.cell import MetaProperty, Cell
from x2py.event import Event

def _init_hello_req_tag():
    metaprops = []
    metaprops.append(MetaProperty('Name', 9))
    return Event.Tag(Event.tag, metaprops,
        1)

class HelloReq(Event):
    tag = _init_hello_req_tag()

    def __init__(self, length=0):
        super().__init__(len(HelloReq.tag.metaprops) + length)
        base = HelloReq.tag.offset
        self.values[base + 0] = ""

    @property
    def name(self):
        return self.values[HelloReq.tag.offset + 0]
    @name.setter
    def name(self, value):
        self._set_property(HelloReq.tag.offset + 0, value,
            HelloReq.tag.metaprops[0].type_index)

    def type_id(self):
        return HelloReq.tag.type_id

    def type_tag(self):
        return HelloReq.tag

def _init_hello_resp_tag():
    metaprops = []
    metaprops.append(MetaProperty('Message', 9))
    return Event.Tag(Event.tag, metaprops,
        2)

class HelloResp(Event):
    tag = _init_hello_resp_tag()

    def __init__(self, length=0):
        super().__init__(len(HelloResp.tag.metaprops) + length)
        base = HelloResp.tag.offset
        self.values[base + 0] = ""

    @property
    def message(self):
        return self.values[HelloResp.tag.offset + 0]
    @message.setter
    def message(self, value):
        self._set_property(HelloResp.tag.offset + 0, value,
            HelloResp.tag.metaprops[0].type_index)

    def type_id(self):
        return HelloResp.tag.type_id

    def type_tag(self):
        return HelloResp.tag

def _init_num_req_tag():
    metaprops = []
    metaprops.append(MetaProperty('Value', 5))
    return Event.Tag(Event.tag, metaprops,
        3)

class NumReq(Event):
    tag = _init_num_req_tag()

    def __init__(self, length=0):
        super().__init__(len(NumReq.tag.metaprops) + length)
        base = NumReq.tag.offset
        self.values[base + 0] = 0

    @property
    def value(self):
        return self.values[NumReq.tag.offset + 0]
    @value.setter
    def value(self, value):
        self._set_property(NumReq.tag.offset + 0, value,
            NumReq.tag.metaprops[0].type_index)

    def type_id(self):
        return NumReq.tag.type_id

    def type_tag(self):
        return NumReq.tag

def _init_num_resp_tag():
    metaprops = []
    metaprops.append(MetaProperty('Result', 5))
    return Event.Tag(Event.tag, metaprops,
        4)

class NumResp(Event):
    tag = _init_num_resp_tag()

    def __init__(self, length=0):
        super().__init__(len(NumResp.tag.metaprops) + length)
        base = NumResp.tag.offset
        self.values[base + 0] = 0

    @property
    def result(self):
        return self.values[NumResp.tag.offset + 0]
    @result.setter
    def result(self, value):
        self._set_property(NumResp.tag.offset + 0, value,
            NumResp.tag.metaprops[0].type_index)

    def type_id(self):
        return NumResp.tag.type_id

    def type_tag(self):
        return NumResp.tag
