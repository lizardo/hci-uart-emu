#!/usr/bin/python
from __future__ import print_function
import sys
import socket
import struct
import asynchat
import asyncore
from construct import Container

from bt_lib.hci.transport import uart

class DummyBT(asynchat.async_chat):
    def __init__(self, path, dumpfile):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connect(path)
        self.new_packet()

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
        if isinstance(c, list):
            for i in c:
                data = uart.build(i)
                self.dump_data(data, False)
                self.sendall(data)
        else:
            data = uart.build(c)
            self.dump_data(data, False)
            self.sendall(data)

    def process_acl_data(self, packet):
        if packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'INFO_REQ' and \
                packet.data.data.data.type == 'FEAT_MASK':

            c = Container(
                packet_indicator = 'ACLDATA',
                packet = Container(
                    header = Container(
                        handle = packet.header.handle,
                        flags = 'START',
                    ),
                    data = Container(
                        cid = 'SIGNALING',
                        data = Container(
                            ident = packet.data.data.ident,
                            code = 'INFO_RSP',
                            data = Container(
                                type = 'FEAT_MASK',
                                result = 0x0000,
                                data = 0x00000080,
                            ),
                        ),
                    )
                )
            )
        elif packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'INFO_REQ' and \
                packet.data.data.data.type == 'FIXED_CHAN':

            c = Container(
                packet_indicator = 'ACLDATA',
                packet = Container(
                    header = Container(
                        handle = packet.header.handle,
                        flags = 'START',
                    ),
                    data = Container(
                        cid = 'SIGNALING',
                        data = Container(
                            ident = packet.data.data.ident,
                            code = 'INFO_RSP',
                            data = Container(
                                type = 'FIXED_CHAN',
                                result = 0x0000,
                                data = [0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                            ),
                        ),
                    )
                )
            )
        elif packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'CONN_REQ':
            c = Container(
                packet_indicator = 'ACLDATA',
                packet = Container(
                    header = Container(
                        handle = packet.header.handle,
                        flags = 'START',
                    ),
                    data = Container(
                        cid = 'SIGNALING',
                        data = Container(
                            ident = packet.data.data.ident,
                            code = 'CONN_RSP',
                            data = Container(
                                # arbitrarily set DCID == SCID
                                dcid = packet.data.data.data.scid,
                                scid = packet.data.data.data.scid,
                                result = 0x0000,
                                status = 0x0000,
                            ),
                        ),
                    )
                )
            )
        elif packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'DISCONN_REQ':
            c = Container(
                packet_indicator = 'ACLDATA',
                packet = Container(
                    header = Container(
                        handle = packet.header.handle,
                        flags = 'START',
                    ),
                    data = Container(
                        cid = 'SIGNALING',
                        data = Container(
                            ident = packet.data.data.ident,
                            code = 'DISCONN_RSP',
                            data = Container(
                                # arbitrarily set DCID == SCID
                                dcid = packet.data.data.data.scid,
                                scid = packet.data.data.data.scid,
                            ),
                        ),
                    )
                )
            )
        elif packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'CONF_REQ':
            c = Container(
                packet_indicator = 'ACLDATA',
                packet = Container(
                    header = Container(
                        handle = packet.header.handle,
                        flags = 'START',
                    ),
                    data = Container(
                        cid = 'SIGNALING',
                        data = Container(
                            ident = packet.data.data.ident,
                            code = 'CONF_RSP',
                            data = Container(
                                # arbitrarily set DCID == SCID
                                scid = packet.data.data.data.dcid,
                                flags = 0x0000,
                                result = 0x0000,
                            ),
                        ),
                    )
                )
            )
        else:
            raise NotImplementedError, "Unsupported ACL packet: %s" % packet

        self.send_response(c)

        c = Container(
            packet_indicator = "EVENT",
            packet = Container(
                evt = "NUM_COMP_PKTS",
                params = Container(
                    num_handles = 1,
                    handle = 0x0001,
                    count = 1,
                )
            )
        )
        self.send_response(c)

    def process_packet(self):
        self.dump_data(self.buf)

        d = uart.parse(self.buf)

        if d.packet_indicator == "ACLDATA":
            self.process_acl_data(d.packet)
            return

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
            assert d.packet.params.page_num == 1
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
        elif ocf == "CREATE_CONN":
            assert d.packet.params.bdaddr == [0xfe, 0xca, 0xfe, 0xca, 0xfe, 0xca]
            c = []
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "CONN_COMPLETE",
                    params = Container(
                        status = 0,
                        handle = 0x0001,
                        bdaddr = [0xfe, 0xca, 0xfe, 0xca, 0xfe, 0xca],
                        link_type = 0x01,
                        encr_mode = 0x00,
                    )
                )
            ))
        elif ocf == "DISCONNECT":
            assert d.packet.params.handle == 0x0001
            c = []
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "DISCONN_COMPLETE",
                    params = Container(
                        status = 0,
                        handle = d.packet.params.handle,
                        reason = 0x16, # Connection Terminated By Local Host
                    )
                )
            ))
        elif ocf == "READ_REMOTE_FEATURES":
            assert d.packet.params.handle == 0x0001
            c = []
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "READ_REMOTE_FEATURES_COMPLETE",
                    params = Container(
                        status = 0,
                        handle = 0x0001,
                        features = [0xa4, 0x08, 0x00, 0xc0, 0x58, 0x1e, 0x7b, 0x83],
                    )
                )
            ))
        elif ocf == "READ_REMOTE_EXT_FEATURES":
            assert d.packet.params.handle == 0x0001
            assert d.packet.params.page_num == 1
            c = []
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "READ_REMOTE_EXT_FEATURES_COMPLETE",
                    params = Container(
                        status = 0,
                        handle = 0x0001,
                        page_num = 1,
                        max_page_num = 1,
                        features = [0x00] * 8,
                    )
                )
            ))
        elif ocf == "REMOTE_NAME_REQ":
            assert d.packet.params.bdaddr == [0xfe, 0xca, 0xfe, 0xca, 0xfe, 0xca]
            c = []
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "REMOTE_NAME_REQ_COMPLETE",
                    params = Container(
                        status = 0,
                        bdaddr = [0xfe, 0xca, 0xfe, 0xca, 0xfe, 0xca],
                        name = "cafe",
                    )
                )
            ))
        else:
            raise NotImplementedError, "Unsupported packet: %s" % d

        self.send_response(c)

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
