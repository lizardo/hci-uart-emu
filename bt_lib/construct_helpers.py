from construct import *
from six import BytesIO

# FIXME: Without this hack, context inside If/Switch is incorrectly placed
# inside "_" (just for sizeof())
class FixedSwitch(Switch):
    def _sizeof(self, ctx):
        while ctx.get("_"):
            ctx = ctx._
        return Switch._sizeof(self, ctx)

def FixedIf(predicate, subcon):
    return FixedSwitch(subcon.name, lambda ctx: bool(predicate(ctx)),
        {
            True: subcon,
            False: Pass,
        }
    )

class SwapAdapter(Adapter):
    def _encode(self, obj, context):
        return "".join(reversed(obj))

    def _decode(self, obj, context):
        return "".join(reversed(obj))

# FIXME: Find better way to calculate plen
class PLenAdapter(Adapter):
    def get_plen(self, obj, ctx):
        if obj is None:
            return 0

        c = Container()
        if ctx.get("opcode"):
            c.opcode = ctx.opcode
            if ctx.opcode.ocf == "SET_EVENT_FLT":
                # This command requires checking some fields
                c.update(obj)
        if ctx.get("evt"):
            c.evt = ctx.evt
            if obj.get("opcode"):
                c.opcode = obj.opcode

        return self.subcon.sizeof(c) - 1

    def _encode(self, obj, ctx):
        return (self.get_plen(obj, ctx), obj)

    def _decode(self, obj, ctx):
        assert self.get_plen(obj[1], ctx) == obj[0]

        return obj[1]

class _DataAdapter(Adapter):
    def __init__(self, subcon, data_field = "data", len_field = "dlen"):
        Adapter.__init__(self, subcon)
        self.data_field = data_field
        self.len_field = len_field

    def _encode(self, obj, ctx):
        if isinstance(obj[self.data_field], str):
            obj[self.len_field] = len(obj[self.data_field])
            return obj

        obj[self.len_field] = 0
        self.subcon._build(obj, BytesIO(), ctx)
        s = BytesIO()
        data = filter(lambda x: x.name == self.data_field, self.subcon.subcons)[0]
        data._build(obj[self.data_field], s, obj)
        obj[self.len_field] = len(s.getvalue())

        return obj

    def _decode(self, obj, ctx):
        del obj[self.len_field]

        return obj

def DataStruct(name, *subcons, **kwds):
    return _DataAdapter(Struct(name, *subcons), **kwds)

class AssertEof(Subconstruct):
    def _parse(self, stream, context):
        obj = self.subcon._parse(stream, context)
        pos = stream.tell()
        stream.seek(0, 2)
        eof = stream.tell()
        stream.seek(pos)
        if pos != eof:
            self.subcon.subcon._parse(stream, context)

        return obj

def pprint_container(obj, indent=0):
    s = ""
    if isinstance(obj, Container):
        s += "Container(\n"
        for k in sorted(obj.keys()):
            s += "    " * (indent + 1) + "%s = %s,\n" % (k, pprint_container(obj[k], indent + 1))
        s += "    " * indent + ")"
    elif isinstance(obj, str):
        s += repr(obj)
    elif isinstance(obj, bool):
        s += "True" if obj else "False"
    elif isinstance(obj, int):
        s += "%d" % obj
    elif isinstance(obj, list):
        s += "[\n"
        for i in obj:
            s += "    " * (indent + 1) + "%s,\n" % pprint_container(i, indent + 1)
        s += "    " * indent + "]"
    else:
        assert NotImplementedError, "Not supported: %s" % obj

    return s
