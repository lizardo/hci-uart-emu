from construct import *
from bt_lib.construct_helpers import *

l2cap_hdr = Struct("l2cap_hdr",
    ULInt16("dlen"),
    Enum(ULInt16("cid"),
        SIGNALING = 0x0001,
    ),
)

l2cap_cmd_hdr = Struct("l2cap_cmd_hdr",
    Enum(ULInt8("code"),
        CONN_REQ = 0x02,
        CONN_RSP = 0x03,
        CONF_REQ = 0x04,
        CONF_RSP = 0x05,
        DISCONN_REQ = 0x06,
        DISCONN_RSP = 0x07,
        INFO_REQ = 0x0a,
        INFO_RSP = 0x0b,
    ),
    ULInt8("ident"),
    ULInt16("dlen"),
)

l2cap_conn_req = Struct("l2cap_conn_req",
    ULInt16("psm"),
    ULInt16("scid"),
)

l2cap_conn_rsp = Struct("l2cap_conn_rsp",
    ULInt16("dcid"),
    ULInt16("scid"),
    ULInt16("result"),
    ULInt16("status"),
)

l2cap_conf_opt = DataStruct("l2cap_conf_opt",
    Enum(ULInt8("type"),
        MTU = 0x01,
    ),
    ULInt8("dlen"),
    Switch("data", lambda ctx: ctx.type,
        {
            "MTU": ULInt16("mtu"),
        }
    ),
)

l2cap_conf_req = Struct("l2cap_conf_req",
    ULInt16("dcid"),
    ULInt16("flags"),
    OptionalGreedyRange(l2cap_conf_opt),
)

l2cap_conf_rsp = Struct("l2cap_conf_rsp",
    ULInt16("scid"),
    ULInt16("flags"),
    ULInt16("result"),
    OptionalGreedyRange(l2cap_conf_opt),
)

l2cap_disconn_req = Struct("l2cap_disconn_req",
    ULInt16("dcid"),
    ULInt16("scid"),
)

l2cap_disconn_rsp = Struct("l2cap_disconn_rsp",
    ULInt16("dcid"),
    ULInt16("scid"),
)

l2cap_info_type = Enum(ULInt16("type"),
    FEAT_MASK = 0x0002,
    FIXED_CHAN = 0x0003,
)

l2cap_info_req = Struct("l2cap_info_req",
    l2cap_info_type,
)

l2cap_info_rsp = Struct("l2cap_info_rsp",
    l2cap_info_type,
    ULInt16("result"),
    Switch("data", lambda ctx: ctx.type,
        {
            "FEAT_MASK": ULInt32("feat_mask"),
            "FIXED_CHAN": Array(8, ULInt8("fixed_chan")),
        }
    ),
)

l2cap_sig = DataStruct("l2cap_sig",
    Embed(l2cap_cmd_hdr),
    Switch("data", lambda ctx: ctx.code,
        {
            "CONN_REQ": l2cap_conn_req,
            "CONN_RSP": l2cap_conn_rsp,
            "CONF_REQ": l2cap_conf_req,
            "CONF_RSP": l2cap_conf_rsp,
            "DISCONN_REQ": l2cap_disconn_req,
            "DISCONN_RSP": l2cap_disconn_rsp,
            "INFO_REQ": l2cap_info_req,
            "INFO_RSP": l2cap_info_rsp,
        }
    ),
)

l2cap = DataStruct("l2cap",
    Embed(l2cap_hdr),
    Switch("data", lambda ctx: ctx.cid,
        {
            "SIGNALING": l2cap_sig,
        }
    ),
)
