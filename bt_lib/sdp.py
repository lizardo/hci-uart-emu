from construct import *
from construct_helpers import *

sdp_uuid16 = Enum(UBInt16("sdp_uuid16"),
    SDP = 0x0001,
    HIDP = 0x0011,
    L2CAP = 0x0100,
    PUBLIC_BROWSE_GROUP = 0x1002,
    HID = 0x1124,
    PNP_INFO = 0x1200,
)

def SDP_SEQ(name, length_field, fn):
    return TunnelAdapter(
        PascalString(name, length_field),
        AssertEof(GreedyRange(LazyBound("subcon", fn))),
    )

def SDP_DE(name):
    return Struct(name,
        Enum(UBInt8("type_size"),
            UINT8 = 0x08,
            UINT16 = 0x09,
            UINT32 = 0x0a,
            UUID16 = 0x19,
            STR8 = 0x25,
            BOOL = 0x28,
            SEQ8 = 0x35,
            SEQ16 = 0x36,
        ),
        Switch("data", lambda ctx: ctx.type_size,
            {
                "UINT8": UBInt8("UINT8"),
                "UINT16": UBInt16("UINT16"),
                "UINT32": UBInt32("UINT32"),
                "UUID16": sdp_uuid16,
                "STR8": PascalString("STR8"),
                "BOOL": Flag("BOOL"),
                "SEQ8": SDP_SEQ("SEQ8", UBInt8("length"), lambda: SDP_DE(name)),
                "SEQ16": SDP_SEQ("SEQ16", UBInt16("length"), lambda: SDP_DE(name)),
            }
        ),
    )

sdp_pdu_hdr_t = Struct("sdp_pdu_hdr_t",
    Enum(UBInt8("pdu_id"),
        ERROR_RSP = 0x01,
        SVC_SEARCH_REQ = 0x02,
        SVC_SEARCH_RSP = 0x03,
        SVC_ATTR_REQ = 0x04,
        SVC_ATTR_RSP = 0x05,
        SVC_SEARCH_ATTR_REQ = 0x06,
        SVC_SEARCH_ATTR_RSP = 0x07,
    ),
    UBInt16("tid"),
    UBInt16("plen"),
)

sdp_svc_search_attr_req = Struct("sdp_svc_search_attr_req",
    SDP_DE("pattern"),
    UBInt16("max_count"),
    SDP_DE("attr_list"),
    PascalString("cont"),
)

sdp_svc_search_attr_rsp = DataStruct("sdp_svc_search_attr_rsp",
    UBInt16("attr_lists_count"),
    SDP_DE("attr_lists"),
    PascalString("cont"),
    data_field = "attr_lists",
    len_field = "attr_lists_count",
)

sdp = DataStruct("sdp",
    Embed(sdp_pdu_hdr_t),
    Switch("params", lambda ctx: ctx.pdu_id,
        {
            "SVC_SEARCH_ATTR_REQ": sdp_svc_search_attr_req,
            "SVC_SEARCH_ATTR_RSP": sdp_svc_search_attr_rsp,
        }
    ),
    data_field = "params",
    len_field = "plen",
)
