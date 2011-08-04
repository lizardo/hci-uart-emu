#!/usr/bin/python
# Author: Anderson Lizardo <anderson.lizardo AT openbossa.org>
# License: GPL v3

import sys
import socket
import select
import struct

from bt_lib.hci.events import Command_Status, Inquiry_Complete, \
        Disconnection_Complete, Remote_Name_Request_Complete, Read_Remote_Version_Information_Complete
from bt_lib.hci.commands import Command

remote_bdaddr = "f0:af:f0:af:f0:af"
remote_bdname = "remote_dummy"

bdaddr = "ca:fe:ca:fe:ca:fe"
bdname = "dummy"
class_of_device = "\x00\x01\x04"
hci_scan = 0x00
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
    payload = struct.pack("<HB", opcode, len(pdata)) + pdata
    events = None

    if ogf == 0x01:
        # Link Control Commands
        c = Command.from_payload(payload)
        if ocf == 0x0001:
            # Inquiry
            print "XXX: Inquiry(LAP=%s, Inquiry_Length=%d, Num_Responses=%d)" % \
                    (c.LAP.encode("hex"), c.Inquiry_Length, c.Num_Responses)

            # Return command status, followed by inquiry complete
            status = Command_Status(Status=0x00, Num_HCI_Command_Packets=1,
                    Command_Opcode=opcode)
            inq_cp = Inquiry_Complete(Status=0x00)

            events = (status, inq_cp)
        elif ocf == 0x0002:
            # Inquiry Cancel
            print "XXX: Inquiry_Cancel()"

            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0006:
            # Disconnect
            print "XXX: Disconnect(Connection_Handle=0x%04x, Reason=0x%02x)" % \
                    (c.Connection_Handle, c.Reason)
            assert c.Connection_Handle == conn_handle

            # Return command status, followed by disconnection complete
            status = Command_Status(Status=0x00, Num_HCI_Command_Packets=1,
                    Command_Opcode=opcode)
            disconn_cp = Disconnection_Complete(Status=0x00,
                    Connection_Handle=c.Connection_Handle, Reason=c.Reason)

            events = (status, disconn_cp)
        elif ocf == 0x0019:
            # Remote Name Request
            print "XXX: Remote_Name_Request(BD_ADDR=%s, Page_Scan_Repetition_Mode=%d, Reserved=%d, Clock_Offset=%s)" % \
                    (c.BD_ADDR.encode("hex"), c.Page_Scan_Repetition_Mode, c.Reserved, c.Clock_Offset.encode("hex"))

            # Return command status, followed by remote name request complete
            status = Command_Status(Status=0x00, Num_HCI_Command_Packets=1,
                    Command_Opcode=opcode)
            remote_name_req_cp = Remote_Name_Request_Complete(Status=0x00,
                    BD_ADDR=build_bdaddr(remote_bdaddr),
                    Remote_Name=build_bdname(remote_bdname))

            events = (status, remote_name_req_cp)
        elif ocf == 0x001d:
            # Read Remote Version Information
            print "XXX: Read_Remote_Version_Information(Connection_Handle=0x%04x)" % c.Connection_Handle
            assert c.Connection_Handle == conn_handle

            # Return command status, followed by remote version information complete
            status = Command_Status(Status=0x00, Num_HCI_Command_Packets=1,
                    Command_Opcode=opcode)
            remote_version_info_cp = Read_Remote_Version_Information_Complete(Status=0x00,
                    Connection_Handle=c.Connection_Handle,
                    Version=6, Manufacturer_Name=65535, Subversion=0x0000)

            events = (status, remote_version_info_cp)
    elif ogf == 0x02:
        # Link Policy Commands
        c = Command.from_payload(payload)
        if ocf == 0x000f:
            # Write Default Link Policy Settings
            print "XXX: Write_Default_Link_Policy_Settings(Default_Link_Policy_Settings=0x%04x)" % \
                    c.Default_Link_Policy_Settings

            events = (c.command_complete(Status=0x00),)
    elif ogf == 0x03:
        # Controller & Baseband Commands
        c = Command.from_payload(payload)
        if ocf == 0x0001:
            # Set Event Mask
            print "XXX: Set_Event_Mask(Event_Mask=%s)" % c.Event_Mask.encode("hex")

            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0003:
            # Reset
            print "XXX: Reset()"

            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0005:
            # Set Event Filter
            # FIXME: implement event filtering
            print "XXX: [FIXME] Set_Event_Filter(Filter_Type=0x%02x, ...)" % \
                    c.Filter_Type
            assert c.Filter_Type == 0x00

            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x000d:
            # Read Stored Link Key
            print "XXX: Read_Stored_Link_Key(BD_ADDR=%s, Read_All_Flag=0x%02x)" % \
                    (c.BD_ADDR.encode("hex"), c.Read_All_Flag)

            events = (c.command_complete(Status=0x00, Max_Num_Keys=0, Num_Keys_Read=0),)
        elif ocf == 0x0012:
            # Delete Stored Link Key
            print "XXX: Delete_Stored_Link_Key(BD_ADDR=%s, Delete_All_Flag=0x%02x)" % \
                    (c.BD_ADDR.encode("hex"), c.Delete_All_Flag)

            events = (c.command_complete(Status=0x00, Num_Keys_Deleted=0),)
        elif ocf == 0x0013:
            # Write Local Name
            print "XXX: Write_Local_Name(Local_Name=%s)" % c.Local_Name
            bdname = c.Local_Name
            print "XXX: New name: %s" % bdname
            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0014:
            # Read Local Name
            print "XXX: Read_Local_Name()"
            events = (c.command_complete(Status=0x00, Local_Name=build_bdname(bdname)),)
        elif ocf == 0x0016:
            # Write Connection Accept Timeout
            print "XXX: Write_Connection_Accept_Timeout(Conn_Accept_Timeout=0x%04x)" % \
                    c.Conn_Accept_Timeout
            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0018:
            # Write Page Timeout
            print "XXX: Write_Page_Timeout(Page_Timeout=0x%04x)" % c.Page_Timeout
            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0019:
            # Read Scan Enable
            print "XXX: Read_Scan_Enable()"
            events = (c.command_complete(Status=0x00, Scan_Enable=hci_scan),)
        elif ocf == 0x001a:
            # Write Scan Enable
            print "XXX: Write_Scan_Enable(Scan_Enable=0x%02x)" % c.Scan_Enable
            hci_scan = c.Scan_Enable
            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0023:
            # Read Class of Device
            print "XXX: Read_Class_of_Device()"
            events = (c.command_complete(Status=0x00, Class_of_Device=class_of_device),)
        elif ocf == 0x0024:
            # Write Class of Device
            print "XXX: Write_Class_of_Device(Class_of_Device=%s)" % c.Class_of_Device.encode("hex")
            class_of_device = c.Class_of_Device
            print "XXX: New class of device: %s" % class_of_device.encode("hex")
            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0025:
            # Read Voice Setting
            print "XXX: Read_Voice_Setting()"
            events = (c.command_complete(Status=0x00, Voice_Setting=0x0000),)
        elif ocf == 0x0045:
            # Write Inquiry Mode
            print "XXX: Write_Inquiry_Mode(Inquiry_Mode=0x%02x)" % c.Inquiry_Mode
            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0052:
            # Write Extended Inquiry Response
            print "XXX: Write_Extended_Inquiry_Response(FEC_Required=0x%02x, Extended_Inquiry_Response=%s)" % \
                    (c.FEC_Required, c.Extended_Inquiry_Response.encode("hex"))
            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0055:
            # Read Simple Pairing Mode
            print "XXX: Read_Simple_Pairing_Mode()"
            events = (c.command_complete(Status=0x00, Simple_Pairing_Mode=0x01),)
        elif ocf == 0x0056:
            # Write Simple Pairing Mode
            print "XXX: Write_Simple_Pairing_Mode(Simple_Pairing_Mode=0x%02x)" % c.Simple_Pairing_Mode
            events = (c.command_complete(Status=0x00),)
        elif ocf == 0x0058:
            # Read Inquiry Response Transmit Power Level
            print "XXX: Read_Inquiry_Response_Transmit_Power_Level()"
            events = (c.command_complete(Status=0x00, TX_Power=0x00),)
        elif ocf == 0x006d:
            # Write LE Host Supported
            print "XXX: Write_LE_Host_Support(LE_Supported_Host=0x%02x, Simultaneous_LE_Host=0x%02x)" % \
                    (c.LE_Supported_Host, c.Simultaneous_LE_Host)
            events = (c.command_complete(Status=0x00),)
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

    if events:
        d = ""
        for e in events:
            d += struct.pack("B", HCI_EVENT_PKT) + e.payload
        return d

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
