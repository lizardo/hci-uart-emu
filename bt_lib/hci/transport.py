class UART(object):
    _packet_types = {
            "command": 0x01,
            "acl": 0x02,
            "synchronous": 0x03,
            "event": 0x04,
    }

    def __init__(self, pkt_type, payload):
        self.payload = payload
        self.pkt_type = pkt_type

    def pack(self):
        return self._packet_types[self.pkt_type] + self.payload.pack()

    def unpack(self):
        return [self.pkt_type] + self.payload.unpack()


