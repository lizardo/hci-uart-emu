from construct import *
from packet import command, event
from acldata import acldata

uart = Struct("uart",
    Enum(ULInt8("packet_indicator"),
        COMMAND = 0x01,
        ACLDATA = 0x02,
        SCODATA = 0x03,
        EVENT   = 0x04,
    ),
    Switch("packet", lambda ctx: ctx.packet_indicator,
        {
            "COMMAND": command,
            "ACLDATA": acldata,
            #"SCODATA": scodata,
            "EVENT": event,
        }
    ),
    Terminator,
)
