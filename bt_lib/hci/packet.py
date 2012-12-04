from construct import *

# Controller & Baseband (OGF 0x03)

host_ctl_commands = Enum(Value("ocf", lambda ctx: ctx.opcode & 0x3ff),
    SET_EVENT_FLT = 0x0005,
    DELETE_STORED_LINK_KEY = 0x0012,
    READ_LOCAL_NAME = 0x0014,
    WRITE_CONN_ACCEPT_TIMEOUT = 0x0016,
    READ_CLASS_OF_DEV = 0x0023,
    READ_VOICE_SETTING = 0x0025,
)

set_event_flt_cp = Struct("set_event_flt_cp",
    Enum(ULInt8("flt_type"),
        CLEAR_ALL = 0x00,
        INQ_RESULT = 0x01,
        CONN_SETUP = 0x02,
    ),
    If(lambda ctx: ctx.flt_type != "CLEAR_ALL",
        Switch("cond_type", lambda ctx: ctx.flt_type,
            {
                "INQ_RESULT": Enum(ULInt8("cond_type"),
                    RETURN_ALL = 0x00,
                    RETURN_CLASS = 0x01,
                    RETURN_BDADDR = 0x02,
                ),
                "CONN_SETUP": Enum(ULInt8("cond_type"),
                    ALLOW_ALL = 0x00,
                    ALLOW_CLASS = 0x01,
                    ALLOW_BDADDR = 0x02,
                ),
            }
        ),
    ),
    If(lambda ctx: ctx.flt_type != "CLEAR_ALL",
        Switch("condition", lambda ctx: ctx.cond_type,
            {
                "RETURN_ALL": Pass,
                "RETURN_CLASS": Struct("cond_class",
                    Array(3, ULInt8("dev_class")),
                    Array(3, ULInt8("dev_class_mask")),
                ),
                "RETURN_BDADDR": Array(6, ULInt8("bdaddr")),
                "ALLOW_ALL": ULInt8("auto_accept_flag"),
                "ALLOW_CLASS": Struct("cond_class",
                    Array(3, ULInt8("dev_class")),
                    Array(3, ULInt8("dev_class_mask")),
                    ULInt8("auto_accept_flag"),
                ),
                "ALLOW_BDADDR": Struct("cond_bdaddr",
                    Array(6, ULInt8("bdaddr")),
                    ULInt8("auto_accept_flag"),
                ),
            }
        ),
    ),
)

set_event_flt_rp = Struct("set_event_flt_rp",
    ULInt8("status"),
)

delete_stored_link_key_cp = Struct("delete_stored_link_key_cp",
    Array(6, ULInt8("bdaddr")),
    ULInt8("delete_all"),
)

delete_stored_link_key_rp = Struct("delete_stored_link_key_rp",
    ULInt8("status"),
    ULInt16("num_keys"),
)

read_local_name_rp = Struct("read_local_name_rp",
    ULInt8("status"),
    String("name", 248, padchar="\x00"),
)

write_conn_accept_timeout_cp = Struct("write_conn_accept_timeout_cp",
    ULInt16("timeout"),
)

write_conn_accept_timeout_rp = Struct("write_conn_accept_timeout_rp",
    ULInt8("status"),
)

read_class_of_dev_rp = Struct("read_class_of_dev_rp",
    ULInt8("status"),
    Array(3, ULInt8("dev_class")),
)

read_voice_setting_rp = Struct("read_voice_setting_rp",
    ULInt8("status"),
    ULInt16("voice_setting"),
)

# Informational Parameters (OGF 0x04)

info_param_commands = Enum(Value("ocf", lambda ctx: ctx.opcode & 0x3ff),
    READ_LOCAL_VERSION = 0x0001,
    READ_LOCAL_FEATURES = 0x0003,
    READ_BUFFER_SIZE = 0x0005,
    READ_BD_ADDR = 0x0009,
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

# Commands

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
    If(lambda ctx: ctx.plen > 0,
        Switch("pdata", lambda ctx: ctx.ocf,
            {
                # Controller & Baseband (OGF 0x03)
                "SET_EVENT_FLT": set_event_flt_cp,
                "DELETE_STORED_LINK_KEY": delete_stored_link_key_cp,
                "WRITE_CONN_ACCEPT_TIMEOUT": write_conn_accept_timeout_cp,
            }
        ),
    ),
    Terminator,
)

# Events

evt_cmd_complete = Struct("evt_cmd_complete",
    ULInt8("ncmd"),
    Opcode,
    Switch("rparams", lambda ctx: ctx.ocf,
        {
            # Controller & Baseband (OGF 0x03)
            "SET_EVENT_FLT": set_event_flt_rp,
            "DELETE_STORED_LINK_KEY": delete_stored_link_key_rp,
            "READ_LOCAL_NAME": read_local_name_rp,
            "WRITE_CONN_ACCEPT_TIMEOUT": write_conn_accept_timeout_rp,
            "READ_CLASS_OF_DEV": read_class_of_dev_rp,
            "READ_VOICE_SETTING": read_voice_setting_rp,
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
