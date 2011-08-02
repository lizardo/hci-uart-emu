import struct
import unittest

from bt_lib.util import uint8_t, uint16_t

_events = {}

class _metacls(type):
    def __new__(mcs, name, bases, dict):
        obj = type.__new__(mcs, name, bases, dict)

        if dict["evcode"] is not None:
            global _events
            _events[dict["evcode"]] = obj

        return obj

class Event(object):
    __metaclass__ = _metacls

    evcode = None
    params = []

    def __init__(self, payload=None, **kwds):
        if payload:
            # Some basic checking is done in from_payload()
            self.payload = payload
            return

        if not self.evcode:
            raise ValueError, "Event code is required"

        plen = reduce(lambda x, y: x + y[1], self.params, 0)
        self.payload = struct.pack("<BB", self.evcode, plen)
        if kwds:
            for p in self.params:
                if p[0] not in kwds:
                    print self.params
                    raise ValueError, "Missing parameter: %s" % p[0]
                if len(p) > 2:
                    d = p[2].pack(kwds[p[0]])
                else:
                    d = kwds[p[0]]
                self.payload += struct.pack("%ds" % p[1], d)

    @staticmethod
    def from_payload(payload):
        global _events

        try:
            evcode, plen, = struct.unpack_from("<BB", payload)
        except struct.error:
            raise ValueError, "Invalid payload: %s" % payload.encode("hex")

        if not _events.get(evcode):
            raise ValueError, "Unknown event code: 0x%02x" % evcode
        if plen != len(payload[2:]):
            raise ValueError, "Parameter total length does not match payload"

        e = _events[evcode](payload)

        if plen != reduce(lambda x, y: x + y[1], e.params, 0):
            raise ValueError, "Parameter total length does not match event"

        return e

    def __getattr__(self, name):
        offset = 2 # skip evcode + plen
        for p in self.params:
            if p[0] == name:
                d, = struct.unpack_from("%ds" % p[1], self.payload, offset)
                if len(p) > 2:
                    return p[2].unpack(d)
                else:
                    return d
            offset += p[1]
        raise AttributeError

class InquiryComplete(Event):
    evcode = 0x01
    params = [
        ("Status", 1, uint8_t),
    ]

class CommandComplete(Event):
    evcode = 0x0e
    params = [
        ("Num_HCI_Command_Packets", 1, uint8_t),
        ("Command_Opcode", 2, uint16_t),
    ]

class CommandStatus(Event):
    evcode = 0x0f
    params = [
        ("Status", 1, uint8_t),
        ("Num_HCI_Command_Packets", 1, uint8_t),
        ("Command_Opcode", 2, uint16_t),
    ]
