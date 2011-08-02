import struct

class uint8_t(object):
    @staticmethod
    def pack(data):
        return struct.pack("B", data)

    @staticmethod
    def unpack(data):
        return struct.unpack("B", data)[0]

class uint16_t(object):
    @staticmethod
    def pack(data):
        return struct.pack("<H", data)

    @staticmethod
    def unpack(data):
        return struct.unpack("<H", data)[0]
