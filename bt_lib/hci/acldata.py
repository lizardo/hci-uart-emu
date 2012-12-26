from construct import *
from bt_lib.construct_helpers import *
from l2cap import l2cap

Header = TunnelAdapter(
    SwapAdapter(Bytes("header", 2)),
    EmbeddedBitStruct(
        Enum(BitField("flags", 4),
            START_NO_FLUSH = 0x00,
            CONT = 0x01,
            START = 0x02,
            COMPLETE = 0x03,
            #ACTIVE_BCAST = 0x04,
            #PICO_BCAST = 0x08,
        ),
        BitField("handle", 12),
    )
)

acldata = Struct("acldata",
    Header,
    TunnelAdapter(
        PascalString("data", ULInt16("dlen")),
        l2cap,
    ),
    Terminator,
)
