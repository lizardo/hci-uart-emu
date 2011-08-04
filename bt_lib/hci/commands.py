import struct

from bt_lib.util import uint8_t, uint16_t

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
    rparams = []

    def __init__(self, payload=None, **kwds):
        if payload:
            # Some basic checking is done in from_payload()
            self.payload = payload
            return

        if not self.ogf or not self.ocf:
            raise ValueError, "OGF and OCF are required"

        opcode = self.ogf << 10 | self.ocf
        plen = reduce(lambda x, y: x + y[1], self.params, 0)
        self.payload = struct.pack("<HB", opcode, plen)
        for p in self.params:
            if p[0] not in kwds:
                raise ValueError, "Missing parameter: %s" % p[0]
            if len(p) > 2:
                d = p[2].pack(kwds[p[0]])
            else:
                d = kwds[p[0]]
            self.payload += struct.pack("%ds" % p[1], d)

    def command_complete(self, *args, **kwds):
        if args:
            raise ValueError, "Invalid non-keyword parameter(s): %s" % (args,)

        opcode = self.ogf << 10 | self.ocf
        from bt_lib.hci.events import Command_Complete
        e = Command_Complete(Num_HCI_Command_Packets=1, Command_Opcode=opcode)
        # create a private copy of e.params (which is a class attribute)
        e.params = e.params[:] + self.rparams

        payload = e.payload[2:]
        for p in self.rparams:
            if p[0] not in kwds:
                raise ValueError, "Missing parameter: %s" % p[0]
            if len(p) > 2:
                d = p[2].pack(kwds[p[0]])
            else:
                d = kwds[p[0]]
            payload += struct.pack("%ds" % p[1], d)

        # Fix parameter total length
        e.payload = struct.pack("<BB", e.evcode, len(payload))
        e.payload += payload

        return e

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

        c = _commands[opcode](payload)

        if plen != reduce(lambda x, y: x + y[1], c.params, 0):
            raise ValueError, "Parameter total length does not match command"

        return c

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

class Inquiry_Cancel(Command):
    ogf = 0x01
    ocf = 0x0002
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Disconnect(Command):
    ogf = 0x01
    ocf = 0x0006
    params = [
        ("Connection_Handle", 2, uint16_t),
        ("Reason", 1, uint8_t),
    ]

class Remote_Name_Request(Command):
    ogf = 0x01
    ocf = 0x0019
    params = [
        ("BD_ADDR", 6),
        ("Page_Scan_Repetition_Mode", 1, uint8_t),
        ("Reserved", 1, uint8_t),
        ("Clock_Offset", 2),
    ]

class Read_Remote_Version_Information(Command):
    ogf = 0x01
    ocf = 0x001d
    params = [
        ("Connection_Handle", 2, uint16_t),
    ]

class Write_Default_Link_Policy_Settings(Command):
    ogf = 0x02
    ocf = 0x000f
    params = [
        ("Default_Link_Policy_Settings", 2, uint16_t),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Set_Event_Mask(Command):
    ogf = 0x03
    ocf = 0x0001
    params = [
        ("Event_Mask", 8),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Reset(Command):
    ogf = 0x03
    ocf = 0x0003
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Set_Event_Filter(Command):
    ogf = 0x03
    ocf = 0x0005
    params = [
        ("Filter_Type", 1, uint8_t),
        # FIXME: this command has variadic parameters, depending on Filter_Type
    ]

class Read_Stored_Link_Key(Command):
    ogf = 0x03
    ocf = 0x000d
    params = [
        ("BD_ADDR", 6),
        ("Read_All_Flag", 1, uint8_t),
    ]
    rparams = [
        ("Status", 1, uint8_t),
        ("Max_Num_Keys", 2, uint16_t),
        ("Num_Keys_Read", 2, uint16_t),
    ]

class Delete_Stored_Link_Key(Command):
    ogf = 0x03
    ocf = 0x0012
    params = [
        ("BD_ADDR", 6),
        ("Delete_All_Flag", 1, uint8_t),
    ]
    rparams = [
        ("Status", 1, uint8_t),
        ("Num_Keys_Deleted", 2, uint16_t),
    ]

class Write_Local_Name(Command):
    ogf = 0x03
    ocf = 0x0013
    params = [
        ("Local_Name", 248),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Read_Local_Name(Command):
    ogf = 0x03
    ocf = 0x0014
    rparams = [
        ("Status", 1, uint8_t),
        ("Local_Name", 248),
    ]

class Write_Connection_Accept_Timeout(Command):
    ogf = 0x03
    ocf = 0x0016
    params = [
        ("Conn_Accept_Timeout", 2, uint16_t),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Write_Page_Timeout(Command):
    ogf = 0x03
    ocf = 0x0018
    params = [
        ("Page_Timeout", 2, uint16_t),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Read_Scan_Enable(Command):
    ogf = 0x03
    ocf = 0x0019
    rparams = [
        ("Status", 1, uint8_t),
        ("Scan_Enable", 1, uint8_t),
    ]

class Write_Scan_Enable(Command):
    ogf = 0x03
    ocf = 0x001a
    params = [
        ("Scan_Enable", 1, uint8_t),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Read_Class_of_Device(Command):
    ogf = 0x03
    ocf = 0x0023
    rparams = [
        ("Status", 1, uint8_t),
        ("Class_of_Device", 3),
    ]

class Write_Class_of_Device(Command):
    ogf = 0x03
    ocf = 0x0024
    params = [
        ("Class_of_Device", 3),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Read_Voice_Setting(Command):
    ogf = 0x03
    ocf = 0x0025
    rparams = [
        ("Status", 1, uint8_t),
        ("Voice_Setting", 2, uint16_t),
    ]

class Write_Inquiry_Mode(Command):
    ogf = 0x03
    ocf = 0x0045
    params = [
        ("Inquiry_Mode", 1, uint8_t),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Write_Extended_Inquiry_Response(Command):
    ogf = 0x03
    ocf = 0x0052
    params = [
        ("FEC_Required", 1, uint8_t),
        ("Extended_Inquiry_Response", 240),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Read_Simple_Pairing_Mode(Command):
    ogf = 0x03
    ocf = 0x0055
    rparams = [
        ("Status", 1, uint8_t),
        ("Simple_Pairing_Mode", 1, uint8_t),
    ]

class Write_Simple_Pairing_Mode(Command):
    ogf = 0x03
    ocf = 0x0056
    params = [
        ("Simple_Pairing_Mode", 1, uint8_t),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]

class Read_Inquiry_Response_Transmit_Power_Level(Command):
    ogf = 0x03
    ocf = 0x0058
    rparams = [
        ("Status", 1, uint8_t),
        ("TX_Power", 1, uint8_t),
    ]

class Write_LE_Host_Support(Command):
    ogf = 0x03
    ocf = 0x006d
    params = [
        ("LE_Supported_Host", 1, uint8_t),
        ("Simultaneous_LE_Host", 1, uint8_t),
    ]
    rparams = [
        ("Status", 1, uint8_t),
    ]
