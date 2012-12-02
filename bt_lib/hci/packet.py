from construct import *

# Commands

host_ctl_commands = Enum(Value("ocf", lambda ctx: ctx.opcode & 0x3ff),
    READ_CLASS_OF_DEV = 0x0023,
)

info_param_commands = Enum(Value("ocf", lambda ctx: ctx.opcode & 0x3ff),
    READ_LOCAL_VERSION = 0x0001,
    READ_LOCAL_FEATURES = 0x0003,
    READ_BUFFER_SIZE = 0x0005,
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
            "HOST_CTL": host_ctl_commands,
            "INFO_PARAM": info_param_commands,
        }
    ),
))

command = Struct("command",
    Opcode,
    ULInt8("plen"),
    Terminator,
)

# Controller & Baseband (OGF 0x03)

read_class_of_dev_rp = Struct("read_class_of_dev_rp",
    ULInt8("status"),
    Array(3, ULInt8("dev_class")),
)

# Informational Parameters (OGF 0x04)

read_local_version_rp = Struct("read_local_version_rp",
    ULInt8("status"),
    ULInt8("hci_ver"),
    ULInt16("hci_rev"),
    ULInt8("lmp_ver"),
    ULInt16("manufacturer"),
    ULInt16("lmp_subver"),
)

read_local_features_rp = Struct("read_local_features_rp",
    ULInt8("status"),
    Array(8, ULInt8("features")),
)

read_buffer_size_rp = Struct("read_buffer_size_rp",
    ULInt8("status"),
    ULInt16("acl_mtu"),
    ULInt8("sco_mtu"),
    ULInt16("acl_max_pkt"),
    ULInt16("sco_max_pkt"),
)

read_bd_addr_rp = Struct("read_bd_addr_rp",
    ULInt8("status"),
    Array(6, ULInt8("bdaddr")),
)

# Events

evt_cmd_complete = Struct("evt_cmd_complete",
    ULInt8("ncmd"),
    Opcode,
    Switch("rparams", lambda ctx: ctx.ocf,
        {
            # Controller & Baseband (OGF 0x03)
            "READ_CLASS_OF_DEV": read_class_of_dev_rp,
            # Informational Parameters (OGF 0x04)
            "READ_LOCAL_VERSION": read_local_version_rp,
            "READ_LOCAL_FEATURES": read_local_features_rp,
            "READ_BUFFER_SIZE": read_buffer_size_rp,
            "READ_BD_ADDR": read_bd_addr_rp,
        }
    ),
)

event = Struct("event",
    Enum(ULInt8("evt"),
        CMD_COMPLETE = 0x0e,
    ),
    ULInt8("plen"),
    Switch("pdata", lambda ctx: ctx.evt,
        {
            "CMD_COMPLETE": evt_cmd_complete,
        }
    ),
    Terminator,
)
