#!/usr/bin/python
from __future__ import print_function
import socket
import struct
import asynchat
import asyncore
from construct import Container

from bt_lib.hci.transport import uart

class DummyBT(asynchat.async_chat):
    def __init__(self, path):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connect(path)
        self.new_packet()

    def process_packet(self):
        d = uart.parse(self.buf)

        assert d.packet_indicator == "COMMAND"
        ocf = d.packet.opcode.ocf

        if ocf == "READ_LOCAL_FEATURES":
            c = Container(
                packet_indicator = 'EVENT',
                packet = Container(
                    evt = 'CMD_COMPLETE',
                    params = Container(
                        opcode = d.packet.opcode,
                        ncmd = 1,
                        rparams = Container(
                            status = 0,
                            features = [164, 8, 0, 192, 88, 30, 123, 131]),
                        )
                    )
                )
        elif ocf == "READ_LOCAL_VERSION":
            c = Container(
                packet_indicator = 'EVENT',
                packet = Container(
                    evt = 'CMD_COMPLETE',
                    params = Container(
                        opcode = d.packet.opcode,
                        ncmd = 1,
                        rparams = Container(
                            status = 0,
                            hci_ver = 6,
                            hci_rev = 0,
                            lmp_subver = 0,
                            lmp_ver = 6,
                            manufacturer = 63),
                        )
                    )
                )
        elif ocf == "READ_BD_ADDR":
            c = Container(
                packet_indicator = 'EVENT',
                packet = Container(
                    evt = 'CMD_COMPLETE',
                    params = Container(
                        opcode = d.packet.opcode,
                        ncmd = 1,
                        rparams = Container(
                            status = 0,
                            bdaddr = [0x42, 0x00, 0x00, 0x01, 0xAA, 0x00]),
                        )
                    )
                )
        elif ocf == "READ_BUFFER_SIZE":
            c = Container(
                packet_indicator = 'EVENT',
                packet = Container(
                    evt = 'CMD_COMPLETE',
                    params = Container(
                        opcode = d.packet.opcode,
                        ncmd = 1,
                        rparams = Container(
                            status = 0,
                            acl_mtu = 192,
                            acl_max_pkt = 1,
                            sco_max_pkt = 0,
                            sco_mtu = 0),
                        )
                    )
                )
        elif ocf == "READ_CLASS_OF_DEV":
            c = Container(
                packet_indicator = 'EVENT',
                packet = Container(
                    evt = 'CMD_COMPLETE',
                    params = Container(
                        opcode = d.packet.opcode,
                        ncmd = 1,
                        rparams = Container(
                            status = 0,
                            dev_class = [0, 0, 0]),
                        )
                    )
                )
        else:
            raise NotImplementedError, "Unsupported packet: %s" % d

        self.sendall(uart.build(c))

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
                self.set_terminator(3)
            else:
                raise NotImplementedError, "Unsupported transport: %#x" % self.transport
        elif self.transport == 0x01:
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
        else:
            raise NotImplementedError, "Unsupported transport: %#x" % self.transport

bt = DummyBT("/tmp/qemu-serial")
asyncore.loop()
