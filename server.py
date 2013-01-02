#!/usr/bin/python
from __future__ import print_function
import sys
import socket
import struct
import asynchat
import asyncore
from construct import Container

from bt_lib.hci.transport import uart
from emulator import Adapter, Device

class DummyBT(asynchat.async_chat):
    def __init__(self, path, dumpfile):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connect(path)
        self.new_packet()
        self.adapter = Adapter("foaf", "f0:af:f0:af:f0:af")
        self.adapter.add_device(Device("cafe", "ca:fe:ca:fe:ca:fe"))

        btsnoop_hdr = struct.pack(">8BLL", 0x62, 0x74, 0x73, 0x6e, 0x6f, 0x6f,
                0x70, 0x00, 1, 1002)
        self.dumpfile = open(dumpfile, "wb")
        self.dumpfile.write(btsnoop_hdr)
        self.dumpfile.flush()

    def dump_data(self, data, incoming=True):
        flags = 0x00 if incoming else 0x01
        if ord(data[0]) in [0x01, 0x04]:
            flags |= 0x02

        # size, len, flags, drops, ts
        btsnoop_pkt = struct.pack(">LLLLQ", len(data), len(data), flags, 0, 0)
        self.dumpfile.write(btsnoop_pkt + data)
        self.dumpfile.flush()

    def send_response(self, c):
        for i in c:
            data = uart.build(i)
            self.dump_data(data, False)
            self.sendall(data)

    def process_packet(self):
        self.dump_data(self.buf)

        d = uart.parse(self.buf)

        if d.packet_indicator == "ACLDATA":
            c = self.adapter.process_acl_data(d.packet)
            self.send_response(c)
        elif d.packet_indicator == "COMMAND":
            c = self.adapter.process_command(d.packet)
            self.send_response(c)
        else:
            raise NotImplementedError, "Unsupported packet type: %s" % d.packet_indicator

    def new_packet(self, process_buffer=False):
        if process_buffer:
            self.process_packet()

        self.buf = b""
        self.set_terminator(1)
        self.transport = None
        self.plen = None

    def collect_incoming_data(self, data):
        self.buf += data

    def found_terminator(self):
        if not self.transport:
            self.transport = struct.unpack_from("B", self.buf, 0)[0]
            if self.transport == 0x01:
                # HCI Command packet
                self.set_terminator(3)
            elif self.transport == 0x02:
                # HCI ACL Data packet
                self.set_terminator(4)
            else:
                raise NotImplementedError, "Unsupported transport: %#x" % self.transport
        elif self.transport == 0x01:
            # HCI Command packet
            if self.plen is None:
                self.plen = struct.unpack_from("B", self.buf, 3)[0]
                if self.plen:
                    self.set_terminator(self.plen)
                else:
                    print("(plen=0):", self.buf.encode("hex"))
                    self.new_packet(True)
            else:
                print("(plen=%d):" % self.plen, self.buf.encode("hex"))
                self.new_packet(True)
        elif self.transport == 0x02:
            # HCI ACL Data packet
            if self.plen is None:
                self.plen = struct.unpack_from("H", self.buf, 3)[0]
                if self.plen:
                    self.set_terminator(self.plen)
                else:
                    print("(plen=0):", self.buf.encode("hex"))
                    self.new_packet(True)
            else:
                print("(plen=%d):" % self.plen, self.buf.encode("hex"))
                self.new_packet(True)
        else:
            raise NotImplementedError, "Unsupported transport: %#x" % self.transport

if len(sys.argv) != 2:
    print("Usage: %s <file.dump>" % sys.argv[0], file=sys.stderr)
    sys.exit(1)

bt = DummyBT("/tmp/qemu-serial", sys.argv[1])
asyncore.loop()
