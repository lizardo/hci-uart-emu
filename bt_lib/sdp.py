from construct import *
from construct_helpers import *

sdp_uuid16 = Enum(UBInt16("sdp_uuid16"),
    L2CAP = 0x0100,
)

sdp_de = Struct("sdp_de",
    Enum(UBInt8("type_size"),
        UINT32 = 0x0a,
        UUID16 = 0x19,
        SEQ8 = 0x35,
    ),
    Switch("data", lambda ctx: ctx.type_size,
        {
            "UUID16": sdp_uuid16,
            "UINT32": UBInt32("uint32"),
            "SEQ8": TunnelAdapter(PascalString("seq8"), GreedyRange(LazyBound("sdp_de", lambda: sdp_de))),
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
    Rename("pattern", sdp_de),
    UBInt16("max_count"),
    Rename("attr_list", sdp_de),
    PascalString("cont"),
)

sdp = DataStruct("sdp",
    Embed(sdp_pdu_hdr_t),
    Switch("params", lambda ctx: ctx.pdu_id,
        {
            "SVC_SEARCH_ATTR_REQ": sdp_svc_search_attr_req,
        }
    ),
    data_field = "params",
    len_field = "plen",
)
