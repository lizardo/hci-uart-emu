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

        def cmd_complete(rparams):
            return Container(
                packet_indicator = 'EVENT',
                packet = Container(
                    evt = 'CMD_COMPLETE',
                    params = Container(
                        opcode = d.packet.opcode,
                        ncmd = 1,
                        rparams = rparams,
                    )
                )
            )

        def cmd_status(status):
            return Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "CMD_STATUS",
                    params = Container(
                        status = status,
                        ncmd = 1,
                        opcode = d.packet.opcode,
                    )
                )
            )

        if ocf == "READ_LOCAL_FEATURES":
            c = cmd_complete(Container(status = 0,
                features = [164, 8, 0, 192, 88, 30, 123, 131],
            ))
        elif ocf == "READ_LOCAL_VERSION":
            c = cmd_complete(Container(status = 0,
                hci_ver = 6,
                hci_rev = 0,
                lmp_subver = 0,
                lmp_ver = 6,
                manufacturer = 63,
            ))
        elif ocf == "READ_BD_ADDR":
            c = cmd_complete(Container(status = 0,
                bdaddr = [0x42, 0x00, 0x00, 0x01, 0xAA, 0x00],
            ))
        elif ocf == "READ_BUFFER_SIZE":
            c = cmd_complete(Container(status = 0,
                acl_mtu = 192,
                acl_max_pkt = 1,
                sco_max_pkt = 0,
                sco_mtu = 0,
            ))
        elif ocf == "READ_CLASS_OF_DEV":
            c = cmd_complete(Container(status = 0,
                dev_class = [0, 0, 0],
            ))
        elif ocf == "READ_LOCAL_NAME":
            c = cmd_complete(Container(status = 0,
                name = "test",
            ))
        elif ocf == "READ_VOICE_SETTING":
            c = cmd_complete(Container(status = 0,
                voice_setting = 0x0000,
            ))
        elif ocf == "SET_EVENT_FLT":
            c = cmd_complete(Container(status = 0))
        elif ocf == "WRITE_CONN_ACCEPT_TIMEOUT":
            c = cmd_complete(Container(status = 0))
        elif ocf == "DELETE_STORED_LINK_KEY":
            c = cmd_complete(Container(status = 0,
                num_keys = 0,
            ))
        elif ocf == "LE_READ_BUFFER_SIZE":
            c = cmd_complete(Container(status = 0,
                pkt_len = 0x00c0,
                max_pkt = 0x01,
            ))
        elif ocf == "LE_READ_ADVERTISING_CHANNEL_TX_POWER":
            c = cmd_complete(Container(status = 0,
                level = 0,
            ))
        elif ocf == "SET_EVENT_MASK":
            c = cmd_complete(Container(status = 0))
        elif ocf == "LE_SET_EVENT_MASK":
            c = cmd_complete(Container(status = 0))
        elif ocf == "READ_LOCAL_COMMANDS":
            c = cmd_complete(Container(status = 0,
                commands = [0] * 64,
            ))
        elif ocf == "WRITE_SIMPLE_PAIRING_MODE":
            c = cmd_complete(Container(status = 0))
        elif ocf == "WRITE_INQUIRY_MODE":
            c = cmd_complete(Container(status = 0))
        elif ocf == "READ_INQ_RESPONSE_TX_POWER_LEVEL":
            c = cmd_complete(Container(status = 0,
                level = 0,
            ))
        elif ocf == "READ_LOCAL_EXT_FEATURES":
            c = cmd_complete(Container(status = 0,
                page_num = 1,
                max_page_num = 1,
                features = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            ))
        elif ocf == "WRITE_LE_HOST_SUPPORTED":
            c = cmd_complete(Container(status = 0))
        elif ocf == "LE_SET_ADVERTISING_DATA":
            c = cmd_complete(Container(status = 0))
        elif ocf == "WRITE_SCAN_ENABLE":
            c = cmd_complete(Container(status = 0))
        elif ocf == "WRITE_CLASS_OF_DEV":
            c = cmd_complete(Container(status = 0))
        elif ocf == "CHANGE_LOCAL_NAME":
            c = cmd_complete(Container(status = 0))
        elif ocf == "WRITE_EXT_INQUIRY_RESPONSE":
            c = cmd_complete(Container(status = 0))
        elif ocf == "RESET":
            c = cmd_complete(Container(status = 0))
        elif ocf == "LE_SET_SCAN_PARAMETERS":
            c = cmd_complete(Container(status = 0))
        elif ocf == "LE_SET_SCAN_ENABLE":
            c = cmd_complete(Container(status = 0))
        elif ocf == "INQUIRY":
            c = []
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "INQUIRY_RESULT",
                    params = Container(
                        num_rsp = 1,
                        bdaddr = [0xfe, 0xca, 0xfe, 0xca, 0xfe, 0xca],
                        pscan_rep_mode = 0,
                        reserved1 = 0,
                        reserved2 = 0,
                        dev_class = [0, 0, 0],
                        clock_offset = 0x0000,
                    )
                )
            ))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "INQUIRY_COMPLETE",
                    params = Container(status = 0)
                )
            ))

        else:
            raise NotImplementedError, "Unsupported packet: %s" % d

        if isinstance(c, list):
            for i in c:
                self.sendall(uart.build(i))
        else:
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
