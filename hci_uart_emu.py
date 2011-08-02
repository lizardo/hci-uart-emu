#!/usr/bin/python
# Author: Anderson Lizardo <anderson.lizardo AT openbossa.org>
# License: GPL v3

import sys
import socket
import select
import struct

from bt_lib.hci.events import CommandComplete, CommandStatus, InquiryComplete
from bt_lib.hci.commands import InquiryCancel

remote_bdaddr = "f0:af:f0:af:f0:af"
remote_bdname = "remote_dummy"

bdaddr = "ca:fe:ca:fe:ca:fe"
bdname = "dummy"
class_of_device = "\x00\x01\x04"
hci_scan = False
hci_le_scan = False
conn_handle = 0x0001

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
HCI_ACLDATA_PKT = 2
HCI_EVENT_PKT = 4

def handle_data(data):
    pkt_type, = struct.unpack_from("B", data, 0)
    if pkt_type == HCI_COMMAND_PKT:
        # HCI Command Packet
        hdr = "<HB"
    elif pkt_type == HCI_ACLDATA_PKT:
        # HCI ACL Data Packet
        hdr = "<HH"
    else:
        raise NotImplementedError, "Packet type: 0x%02x" % pkt_type
    pkt_id, dlen = struct.unpack_from(hdr, data, 1)
    payload, = struct.unpack_from("%ds" % dlen, data, 1 + struct.calcsize(hdr))
    return (pkt_type, pkt_id, payload)

def parse_opcode(opcode):
    return (opcode >> 10, opcode & 0x03ff)

def cmd_complete(opcode, rparams):
    eparams = struct.pack("<BH", 1, opcode) + rparams
    return struct.pack("<BBB", HCI_EVENT_PKT, 0x0E, len(eparams)) + eparams

def cmd_status(opcode, status):
    eparams = struct.pack("<BBH", status, 1, opcode)
    return struct.pack("<BBB", HCI_EVENT_PKT, 0x0F, len(eparams)) + eparams

def le_adv_report():
    eparams = struct.pack("<BBBB6s4sb", 0x02, 0x01, 0x00, 0x00, build_bdaddr(remote_bdaddr), "\x03\x02\x01\x06", -127)
    return struct.pack("<BBB", HCI_EVENT_PKT, 0x3E, len(eparams)) + eparams

def handle_att(data):
    if data.encode("hex") == "100100ffff0028":
        # Discover All Primary Services
        rdata = struct.pack("<BB", 0x11, 6)
        for i in [(0x0001, 0x0008, 0x1800), (0x0010, 0x0010, 0x1801)]:
            # Attribute handle, End Group Handle, Attribute Value
            rdata += struct.pack("<HHH", *i)
        return rdata
    elif data.encode("hex") == "101100ffff0028":
        # End of "Discover All Primary Services"
        return struct.pack("<BBHB", 0x01, 0x10, 0x0011, 0x0A)
    else:
        raise NotImplementedError, "ATT Packet: %s" % data.encode("hex")

def handle_l2cap(data):
    hdr = "<HH"
    dlen, cid = struct.unpack_from(hdr, data, 0)
    if cid != 0x0004:
        raise NotImplementedError, "Unsupported CID (%#04x)" % cid
    payload, = struct.unpack_from("%ds" % dlen, data, struct.calcsize(hdr))
    rdata = handle_att(payload)
    return struct.pack(hdr, len(rdata), cid) + rdata

def build_event(pkt_type, opcode, pdata):
    global bdname, hci_scan, hci_le_scan, class_of_device

    if pkt_type == HCI_ACLDATA_PKT:
        print "XXX: ACL:", (opcode, pdata.encode("hex"))
        # Set PB flag to 10 and BC flag to 00
        opcode &= 0xfff
        opcode |= 1 << 13
        rdata = handle_l2cap(pdata)
        acl_data = struct.pack("<BHH", HCI_ACLDATA_PKT, opcode, len(rdata)) + rdata
        eparams = struct.pack("<BHH", 1, conn_handle, 1)
        completed = struct.pack("<BBB", HCI_EVENT_PKT, 0x13, len(eparams)) + eparams
        return acl_data + completed

    ogf, ocf = parse_opcode(opcode)

    if ogf == 0x01:
        # Link Control Commands
        if ocf == 0x0001:
            # Inquiry
            # Return command status, followed by inquiry complete
            status = CommandStatus(Status=0x00, Num_HCI_Command_Packets=1, Command_Opcode=opcode)
            inq_complete = InquiryComplete(Status=0x00)
            return struct.pack("B", HCI_EVENT_PKT) + status.payload + struct.pack("B", HCI_EVENT_PKT) + inq_complete.payload
        elif ocf == 0x0002:
            # Inquiry Cancel
            c = InquiryCancel()
            return struct.pack("B", HCI_EVENT_PKT) + c.command_complete(Status=0x00).payload
        elif ocf == 0x0006:
            # Disconnect
            handle, reason = struct.unpack("<HB", pdata)
            assert handle == conn_handle
            print "XXX: disconnect (reason=%#02X)" % reason
            # Return command status, followed by disconnection complete
            status = cmd_status(opcode, 0x00)
            eparams = struct.pack("<BHB", 0x00, handle, reason)
            disconn = struct.pack("<BBB", HCI_EVENT_PKT, 0x05, len(eparams)) + eparams
            return status + disconn
        elif ocf == 0x0019:
            # Remote Name Request
            # Return command status, followed by remote name request complete
            status = cmd_status(opcode, 0x00)
            eparams = struct.pack("<B6s248s", 0x00, build_bdaddr(remote_bdaddr), build_bdname(remote_bdname))
            remote_name_req = struct.pack("<BBB", HCI_EVENT_PKT, 0x07, len(eparams)) + eparams
            return status + remote_name_req
        elif ocf == 0x001d:
            # Read Remote Version Information
            handle, = struct.unpack("<H", pdata)
            assert handle == conn_handle
            # Return command status, followed by remote version information complete
            status = cmd_status(opcode, 0x00)
            eparams = struct.pack("<BHBHH", 0x00, conn_handle, 6, 65535, 0x0000)
            remote_version = struct.pack("<BBB", HCI_EVENT_PKT, 0x0C, len(eparams)) + eparams
            return status + remote_version
    elif ogf == 0x02:
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
        elif ocf == 0x0012:
            # Delete Stored Link Key
            rparams = struct.pack("<BH", 0x00, 0)
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0013:
            # Write Local Name
            bdname = struct.unpack("<248s", pdata)[0]
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
            rparams = struct.pack("<BB", 0x00, 0x01 if hci_scan else 0x00)
            return cmd_complete(opcode, rparams)
        elif ocf == 0x001a:
            # Write Scan Enable
            hci_scan = True if struct.unpack("B", pdata)[0] else False
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x0023:
            # Read Class of Device
            rparams = struct.pack("<B3s", 0x00, class_of_device)
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0024:
            # Write Class of Device
            class_of_device = struct.unpack("<3s", pdata)[0]
            print "XXX: New class of device: %s" % class_of_device.encode("hex")
            return cmd_complete(opcode, "\x00")
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
        if ocf == 0x0002:
            # Read Local Supported Commands
            reserved = {
                    3: range(2, 8),
                    4: [1],
                    8: [4, 5],
                    12: [2, 3],
                    13: range(4, 8),
                    14: [0, 1, 2, 4],
                    16: [6, 7],
                    17: [3],
                    18: [4, 5, 6],
                    20: [0, 1, 5, 6, 7],
                    23: [3, 4],
                    24: range(1, 8),
                    25: [3],
                    28: [7],
            }
            # reserved bytes
            for i in range(29, 64):
                reserved[i] = range(0, 8)

            cmds = ""
            for i in range(0, 64):
                if not reserved.get(i):
                    cmds += "\xff"
                    continue

                d = 0
                for j in range(0, 8):
                    if j not in reserved[i]:
                        d |= 1 << j
                cmds += chr(d)

            print "XXX: Supported Commands:", cmds.encode("hex")
            rparams = struct.pack("<B64s", 0x00, cmds)
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0003:
            # Read Local Supported Features
            rparams = struct.pack("<B8s", 0x00, "\xff\xff\xff\xfe\xfb\xff\x7b\x87")
            return cmd_complete(opcode, rparams)
        elif ocf == 0x0004:
            # Read Local Extended Features
            page = struct.unpack("B", pdata)[0]
            rparams = struct.pack("<BBB8s", 0x00, page, 1, "\x07\x00\x00\x00\x00\x00\x00\x00")
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
        elif ocf == 0x000b:
            # LE Set Scan Parameters
            return cmd_complete(opcode, "\x00")
        elif ocf == 0x000c:
            # LE Set Scan Enable
            hci_le_scan = True if struct.unpack("B", pdata[0])[0] else False
            if hci_le_scan:
                return cmd_complete(opcode, "\x00") + le_adv_report()
            else:
                return cmd_complete(opcode, "\x00")
        elif ocf == 0x000d:
            # LE Create Connection
            peer_bdaddr, = struct.unpack_from("<6s", pdata, 6)
            assert peer_bdaddr == build_bdaddr(remote_bdaddr)

            # Return command status, followed by LE connection complete
            status = cmd_status(opcode, 0x00)
            eparams = struct.pack("<BBHBB6sHHHB", 0x01, 0x00, conn_handle, 0x00, 0x00, build_bdaddr(remote_bdaddr), 0x0006, 0x0006, 0x000A, 0x00)
            le_conn_complete = struct.pack("<BBB", HCI_EVENT_PKT, 0x3E, len(eparams)) + eparams
            return status + le_conn_complete

    raise NotImplementedError, "ogf = 0x%02x, ocf = 0x%04x" % (ogf, ocf)

def wait_data():
    buf = ""
    while True:
        nfds = p.poll()
        if not nfds:
            continue

        data = sock.recv(4096, socket.MSG_DONTWAIT)
        if not data:
            return

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
        if data:
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
