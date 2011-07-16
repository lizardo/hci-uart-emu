import struct

from bt_lib.util import uint8_t

_commands = {}

class _metacls(type):
    def __new__(mcs, name, bases, dict):
        obj = type.__new__(mcs, name, bases, dict)

        if dict["ogf"] is not None:
            global _commands
            opcode = dict["ogf"] << 10 | dict["ocf"]
            _commands[opcode] = obj

        return obj

class Command(object):
    __metaclass__ = _metacls

    ogf = None
    ocf = None
    params = []

    def __init__(self, *args, **kwds):
        if args:
            raise ValueError, "Invalid non-keyword parameter(s): %s" % (args,)

        if not self.ogf or not self.ocf:
            raise ValueError, "OGF and OCF are required"

        plen = reduce(lambda x, y: x + y[1], self.params, 0)
        self.payload = struct.pack("<HB", self.ogf << 10 | self.ocf, plen)
        if kwds:
            for p in self.params:
                if p[0] not in kwds:
                    raise ValueError, "Missing parameter: %s" % p[0]
                if len(p) > 2:
                    d = p[2].pack(kwds[p[0]])
                else:
                    d = kwds[p[0]]
                self.payload += struct.pack("%ds" % p[1], d)

    @staticmethod
    def from_payload(payload):
        global _commands

        try:
            opcode, plen, = struct.unpack_from("<HB", payload)
        except struct.error:
            raise ValueError, "Invalid payload: %s" % payload.encode("hex")

        if not _commands.get(opcode):
            raise ValueError, "Unknown opcode: 0x%04x" % opcode
        if plen != len(payload[3:]):
            raise ValueError, "Parameter total length does not match payload"

        c = _commands[opcode]()
        c.payload = payload

        if plen != reduce(lambda x, y: x + y[1], c.params, 0):
            raise ValueError, "Parameter total length does not match command"

    def __getattr__(self, name):
        offset = 3 # skip opcode + plen
        for p in self.params:
            if p[0] == name:
                d, = struct.unpack_from("%ds" % p[1], self.payload, offset)
                if len(p) > 2:
                    return p[2].unpack(d)
                else:
                    return d
            offset += p[1]
        raise AttributeError

class Inquiry(Command):
    ogf = 0x01
    ocf = 0x0001
    params = [
        ("LAP", 3),
        ("Inquiry_Length", 1, uint8_t),
        ("Num_Responses", 1, uint8_t),
    ]
