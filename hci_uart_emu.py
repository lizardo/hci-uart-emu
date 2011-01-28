#!/usr/bin/python
# Author: Anderson Lizardo <anderson.lizardo AT openbossa.org>
# License: GPL v3

import sys
import socket
import select
import struct

bdaddr = "ca:fe:ca:fe:ca:fe"
bdname = "dummy"
hci_scan = 0x00

def build_bdaddr(ba):
    return "".join([ba.split(":")[i] for i in (1, 0, 3, 2, 5, 4)]).decode("hex")

def build_bdname(bn):
    return bn + "\x00" * (248 - min(248, len(bn)))

def dump_data(data, incoming=True):
    # NOTE: flags is inverted because flow is PTS -> dongle
    flags = 0x00 if incoming else 0x01
    if ord(data[0]) in [0x01, 0x04]:
        flags |= 0x02

    # size, len, flags, drops, ts
    btsnoop_pkt = struct.pack(">LLLLQ", len(data), len(data), flags, 0, 0)
    dump.write(btsnoop_pkt + data)

HCI_COMMAND_PKT = 1
HCI_EVENT_PKT = 4

def handle_data(data):
    pkt_type, = struct.unpack("B", data[0])
    idx = 1

    if pkt_type == HCI_COMMAND_PKT:
        # HCI Command Packet
        hci_command_hdr = "<HB"
        opcode, plen = struct.unpack_from(hci_command_hdr, data, idx)
        idx += struct.calcsize(hci_command_hdr)
        pdata, = struct.unpack("%ds" % plen, data[idx:])
        return (opcode, pdata)
    else:
        raise NotImplementedError, "pkt_type: %d" % pkt_type

def parse_opcode(opcode):
    return (opcode >> 10, opcode & 0x03ff)

def cmd_complete(opcode, rparams):
    eparams = struct.pack("<BH", 1, opcode) + rparams
    return struct.pack("<BBB", HCI_EVENT_PKT, 0x0E, len(eparams)) + eparams

def build_event(opcode, pdata):
    global bdname, hci_scan

    ogf, ocf = parse_opcode(opcode)

    if ogf == 0x02:
        # Link Policy Commands
        if ocf == 0x000f:
            # Write Default Link Policy Settings
            return cmd_complete(opcode, "\x00")
    elif ogf == 0x03:
        # Controller & Baseband Commands
        if ocf == 0x0001:
            # Set Event Mask
            # FIXME: implement event masking
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x0003:
            # Reset
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x0005:
            # Set Event Filter
            # FIXME: implement event filtering
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x000d:
            # Read Stored Link Key
            rparams = struct.pack("<BHH", 0x00, 0, 0)
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0013:
            # Write Local Name
            bdname = struct.unpack("248s", pdata)[0]
            print "XXX: New name: %s" % bdname
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x0014:
            # Read Local Name
            rparams = "\x00" + build_bdname(bdname)
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0016:
            # Write Connection Accept Timeout
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x0018:
            # Write Page Timeout
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x0019:
            # Read Scan Enable
            rparams = struct.pack("<BB", 0x00, hci_scan)
            return cmd_complete(opcode, rparams)
        elif ocf == 0x001a:
            # Write Scan Enable
            hci_scan = struct.unpack("B", pdata)[0]
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x0023:
            # Read Class of Device
            rparams = struct.pack("<B3s", 0x00, "\x00\x01\x04")
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0025:
            # Read Voice Setting
            rparams = struct.pack("<BH", 0x00, 0x0000)
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0045:
            # Write Inquiry Mode
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x0052:
            # Write Extended Inquiry Response
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x0055:
            # Read Simple Pairing Mode
            return cmd_complete(opcode, "\x00\x01")
        elif ocf == 0x0056:
            # Write Simple Pairing Mode
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x0058:
            # Read Inquiry Response Transmit Power Level
            return cmd_complete(opcode, "\x00\x00")
        elif ocf == 0x006d:
            # Write LE Host Supported
            return cmd_complete(opcode, "\x00")
    elif ogf == 0x04:
        # Informational Parameters
        if ocf == 0x0001:
            # Read Local Version Information
            rparams = struct.pack("<BBHBHH", 0x00, 6, 0x0000, 6, 65535, 0x0000)
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0003:
            # Read Local Supported Features
            rparams = struct.pack("B8s", 0x00, "\xff\xff\xff\xfe\xfb\xff\x7b\x87")
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0004:
            # Read Local Extended Features
            page = struct.unpack("B", pdata)[0]
            rparams = struct.pack("BBB8s", 0x00, page, 1, "\x07\x00\x00\x00\x00\x00\x00\x00")
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0005:
            # Read Buffer Size
            rparams = struct.pack("<BHBHH", 0x00, 2048, 255, 1, 1)
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0009:
            # Read BD_ADDR
            rparams = struct.pack("<B6s", 0x00, build_bdaddr(bdaddr))
            return cmd_complete(opcode, rparams)
    elif ogf == 0x08:
        # LE Controller Commands
        if ocf == 0x0002:
            # LE Read Buffer Size
            rparams = struct.pack("<BHB", 0x00, 2048, 1)
            return cmd_complete(opcode, rparams)

    raise NotImplementedError, "ogf = 0x%02x, ocf = 0x%04x" % (ogf, ocf)

def wait_data():
    buf = ""
    while True:
        nfds = p.poll()
        if not nfds:
            continue

        data = sock.recv(4096, socket.MSG_DONTWAIT)
        assert data
        print "XXX: data:", data.encode("hex")

        buf += data
        try:
            ret = handle_data(buf)
        except struct.error:
            continue
        else:
            dump_data(buf)
            buf = ""

        print "XXX: handle_data:", ret
        data = build_event(*ret)
        sock.send(data)
        dump_data(data, False)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >>sys.stderr, "Usage: %s <btsnoop.dump>" % sys.argv[0]
        sys.exit(1)

    btsnoop_hdr = struct.pack(">8BLL", 0x62, 0x74, 0x73, 0x6e, 0x6f, 0x6f, 0x70, 0x00, 1, 1002)
    dump = open(sys.argv[1], "wb")
    dump.write(btsnoop_hdr)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("10.100.1.1", 9999))

    p = select.poll()
    p.register(sock, select.POLLIN)

    try:
        wait_data()
    except KeyboardInterrupt:
        pass

    print >>sys.stderr, "\nExiting..."

    sock.close()
    dump.close()
