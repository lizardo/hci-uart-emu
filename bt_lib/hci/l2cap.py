from construct import *
from bt_lib.construct_helpers import *

# FIXME: find more elegant solution for calculating dlen
class HeaderAdapter(Adapter):
    def _encode(self, obj, ctx):
        assert self.subcon.subcons[1].name == "data"

        c = Container()
        if ctx.data.get("cid"):
            c.cid = ctx.data.cid
        if ctx.data.get("code"):
            c.code = ctx.data.code
        if ctx.data.data.get("code"):
            c.code = ctx.data.data.code

        if ctx.data.data.get("data"):
            if ctx.data.data.get("type"):
                c.type = ctx.data.data.type
            else:
                c.type = ctx.data.data.data.type

        obj.dlen = self.subcon.subcons[1].sizeof(c)

        return obj

    def _decode(self, obj, ctx):
        assert self.subcon.subcons[1].name == "data"
        del obj.dlen
        return obj

l2cap_hdr = Struct("l2cap_hdr",
    ULInt16("dlen"),
    Enum(ULInt16("cid"),
        SIGNALING = 0x0001,
    ),
)

l2cap_cmd_hdr = Struct("l2cap_cmd_hdr",
    Enum(ULInt8("code"),
        INFO_REQ = 0x0a,
        INFO_RSP = 0x0b,
    ),
    ULInt8("ident"),
    ULInt16("dlen"),
)

l2cap_info_type = Enum(ULInt16("type"),
    FEAT_MASK = 0x0002,
)

l2cap_info_req = Struct("l2cap_info_req",
    l2cap_info_type,
)

l2cap_info_rsp = Struct("l2cap_info_rsp",
    l2cap_info_type,
    ULInt16("result"),
    FixedSwitch("data", lambda ctx: ctx.type,
        {
            "FEAT_MASK": ULInt32("feat_mask"),
        }
    ),
)

l2cap_sig = HeaderAdapter(Struct("l2cap_sig",
    Embed(l2cap_cmd_hdr),
    FixedSwitch("data", lambda ctx: ctx.code,
        {
            "INFO_REQ": l2cap_info_req,
            "INFO_RSP": l2cap_info_rsp,
        }
    ),
))

l2cap = HeaderAdapter(Struct("l2cap",
    Embed(l2cap_hdr),
    Switch("data", lambda ctx: ctx.cid,
        {
            "SIGNALING": l2cap_sig,
        }
    ),
))
