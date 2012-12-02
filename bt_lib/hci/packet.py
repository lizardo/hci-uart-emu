from construct import *

info_param_commands = Enum(Value("ocf", lambda ctx: ctx.opcode & 0x3ff),
    READ_LOCAL_VERSION = 0x0001,
    READ_LOCAL_FEATURES = 0x0003,
    READ_BD_ADDR = 0x0009,
)

Opcode = Embedded(Struct("opcode",
    ULInt16("opcode"),
    Enum(Value("ogf", lambda ctx: ctx.opcode >> 10 & 0x3f),
        LINK_CTL = 0x01,
        LINK_POLICY = 0x02,
        HOST_CTL = 0x03,
        INFO_PARAM = 0x04,
        STATUS_PARAM = 0x05,
        LE_CTL = 0x08,
    ),
    Switch("ocf", lambda ctx: ctx.ogf,
        {
            "INFO_PARAM": info_param_commands,
        }
    ),
))

command = Struct("command",
    Opcode,
    Byte("plen"),
    Terminator,
)

read_local_version_rp = Struct("read_local_version_rp",
    ULInt8("status"),
    ULInt8("hci_ver"),
    ULInt16("hci_rev"),
    ULInt8("lmp_ver"),
    ULInt16("manufacturer"),
    ULInt16("lmp_subver"),
)

read_local_features_rp = Struct("read_local_features_rp",
    Byte("status"),
    Array(8, Byte("features")),
)

read_bd_addr_rp = Struct("read_bd_addr_rp",
    Byte("status"),
    Array(6, Byte("bdaddr")),
)

evt_cmd_complete = Struct("evt_cmd_complete",
    Byte("ncmd"),
    Opcode,
    Switch("rparams", lambda ctx: ctx.ocf,
        {
            "READ_LOCAL_FEATURES": read_local_features_rp,
            "READ_LOCAL_VERSION": read_local_version_rp,
            "READ_BD_ADDR": read_bd_addr_rp,
        }
    ),
)

event = Struct("event",
    Enum(Byte("evt"),
        CMD_COMPLETE = 0x0e,
    ),
    Byte("plen"),
    Switch("pdata", lambda ctx: ctx.evt,
        {
            "CMD_COMPLETE": evt_cmd_complete,
        }
    ),
    Terminator,
)
