from bt_lib.hci.transport import uart
from construct import Container
from bt_lib.sdp import sdp

def h2b(h):
    return h.replace(" ","").decode("hex")

def test1():
    # HCI Command: Read Local Supported Features (0x04|0x0003) plen 0
    b = h2b("01 03 10 00")
    c = Container(
        packet_indicator = 'COMMAND',
        packet = Container(
            opcode = Container(
                ogf = 'INFO_PARAM',
                ocf = 'READ_LOCAL_FEATURES'),
            params = None)
        )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test2():
    # HCI Event: Command Complete (0x0e) plen 12
    #     Read Local Supported Features (0x04|0x0003) ncmd 1
    #     status 0x00
    #     Features: 0xa4 0x08 0x00 0xc0 0x58 0x1e 0x7b 0x83
    b = h2b("04 0E 0C 01 03 10 00 A4 08 00 C0 58 1E 7B 83")
    c = Container(
        packet_indicator = 'EVENT',
        packet = Container(
            evt = 'CMD_COMPLETE',
            params = Container(
                ncmd = 1,
                rparams = Container(
                    status = 0,
                    features = [164, 8, 0, 192, 88, 30, 123, 131]),
                opcode = Container(
                    ogf = 'INFO_PARAM',
                    ocf = 'READ_LOCAL_FEATURES')
                )
            )
        )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test3():
    # HCI Event: Command Complete (0x0e) plen 12
    #     Read Local Version Information (0x04|0x0001) ncmd 1
    #     status 0x00
    #     HCI Version: 4.0 (0x6) HCI Revision: 0x0
    #     LMP Version: 4.0 (0x6) LMP Subversion: 0x0
    #     Manufacturer: Bluetooth SIG, Inc (63)
    b = h2b("04 0E 0C 01 01 10 00 06 00 00 06 3F 00 00 00")
    c = Container(
        packet_indicator = 'EVENT',
        packet = Container(
            evt = 'CMD_COMPLETE',
            params = Container(
                ncmd = 1,
                rparams = Container(
                    status = 0,
                    hci_ver = 6,
                    hci_rev = 0,
                    lmp_subver = 0,
                    lmp_ver = 6,
                    manufacturer = 63),
                opcode = Container(
                    ogf = 'INFO_PARAM',
                    ocf = 'READ_LOCAL_VERSION')
                )
            )
        )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test4():
    # HCI Event: Command Complete (0x0e) plen 10
    #     Read BD ADDR (0x04|0x0009) ncmd 1
    #     status 0x00 bdaddr 00:AA:01:00:00:42
    b = h2b("04 0E 0A 01 09 10 00 42 00 00 01 AA 00")
    c = Container(
        packet_indicator = 'EVENT',
        packet = Container(
            evt = 'CMD_COMPLETE',
            params = Container(
                ncmd = 1,
                rparams = Container(
                    status = 0,
                    bdaddr = [0x42, 0x00, 0x00, 0x01, 0xAA, 0x00]),
                opcode = Container(
                    ogf = 'INFO_PARAM',
                    ocf = 'READ_BD_ADDR')
                )
            )
        )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test5():
    # HCI Command: Read Class of Device (0x03|0x0023) plen 0
    b = h2b("01 23 0C 00")
    c = Container(
        packet_indicator = 'COMMAND',
        packet = Container(
            opcode = Container(
                ogf = 'HOST_CTL',
                ocf = 'READ_CLASS_OF_DEV'),
            params = None)
        )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test6():
    # HCI Command: Set Event Filter (0x03|0x0005) plen 1
    #     type 0 condition 0
    #     Clear all filters
    b = h2b("01 05 0C 01 00")
    c = Container(
        packet_indicator = 'COMMAND',
        packet = Container(
            opcode = Container(
                ogf = 'HOST_CTL',
                ocf = 'SET_EVENT_FLT'),
            params = Container(
                condition = None,
                flt_type = 'CLEAR_ALL',
                cond_type = None)
            )
        )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test7():
    # HCI Command: Write Connection Accept Timeout (0x03|0x0016) plen 2
    #     timeout 32000
    b = h2b("01 16 0C 02 00 7D")
    c = Container(
        packet_indicator = 'COMMAND',
        packet = Container(
            opcode = Container(
                ogf = 'HOST_CTL',
                ocf = 'WRITE_CONN_ACCEPT_TIMEOUT'),
            params = Container(
                timeout = 32000)
            )
        )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test8():
    # HCI Command: Delete Stored Link Key (0x03|0x0012) plen 7
    #     bdaddr 00:00:00:00:00:00 all 1
    b = h2b("01 12 0C 07 00 00 00 00 00 00 01")
    c = Container(
        packet_indicator = 'COMMAND',
        packet = Container(
            opcode = Container(
                ogf = 'HOST_CTL',
                ocf = 'DELETE_STORED_LINK_KEY'),
            params = Container(
                bdaddr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                delete_all = 1)
            )
        )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test9():
    # HCI Event: Command Complete (0x0e) plen 6
    #     Delete Stored Link Key (0x03|0x0012) ncmd 1
    #     status 0x00 deleted 0
    b = h2b("04 0E 06 01 12 0C 00 00 00")
    c = Container(
        packet_indicator = 'EVENT',
        packet = Container(
            evt = 'CMD_COMPLETE',
            params = Container(
                ncmd = 1,
                rparams = Container(
                    status = 0,
                    num_keys = 0),
                opcode = Container(
                    ogf = 'HOST_CTL',
                    ocf = 'DELETE_STORED_LINK_KEY')
                )
            )
        )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test10():
    # ACL data: handle 1 flags 0x00 dlen 10
    #     L2CAP(s): Info req: type 2
    b = h2b("02 01 00 0A 00 06 00 01 00 0A 01 02 00 02 00")
    c = Container(
        packet_indicator = 'ACLDATA',
        packet = Container(
            header = Container(
                handle = 1,
                flags = 'START_NO_FLUSH',
            ),
            data = Container(
                cid = 'SIGNALING',
                data = Container(
                    ident = 1,
                    code = 'INFO_REQ',
                    data = Container(
                        type = 'FEAT_MASK',
                    ),
                ),
            )
        )
    )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test11():
    # ACL data: handle 1 flags 0x02 dlen 16
    #     L2CAP(s): Info rsp: type 2 result 0
    #       Extended feature mask 0x0080
    #         Fixed Channels
    b = h2b("02 01 20 10 00 0C 00 01 00 0B 01 08 00 02 00 00 00 80 00 00 00")
    c = Container(
        packet_indicator = 'ACLDATA',
        packet = Container(
            header = Container(
                handle = 1,
                flags = 'START',
            ),
            data = Container(
                cid = 'SIGNALING',
                data = Container(
                    ident = 1,
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
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test12():
    # ACL data: handle 42 flags 0x02 dlen 16
    #     L2CAP(s): Config req: dcid 0x0040 flags 0x00 clen 4
    #       MTU 48
    b = h2b("02 2A 20 10 00 0C 00 01 00 04 01 08 00 40 00 00 00 01 02 30 00")
    c = Container(
        packet_indicator = 'ACLDATA',
        packet = Container(
            header = Container(
                handle = 42,
                flags = 'START',
            ),
            data = Container(
                cid = 'SIGNALING',
                data = Container(
                    ident = 1,
                    code = 'CONF_REQ',
                    data = Container(
                        dcid = 0x0040,
                        flags = 0x0000,
                        l2cap_conf_opt = [
                            Container(type = 'MTU', data = 48),
                        ],
                    ),
                ),
            )
        )
    )
    assert uart.parse(b) == c
    assert uart.build(c) == b

def test13():
    b = h2b("060000000f3503190100ffff35050a0000ffff00")
    c = Container(
        pdu_id = 'SVC_SEARCH_ATTR_REQ',
        tid = 0,
        params = Container(
            pattern = Container(
                data = [
                    Container(data = "L2CAP", type_size = "UUID16"),
                ],
                type_size = "SEQ8",
            ),
            attr_list = Container(
                data = [
                    Container(data = 0xffff, type_size = "UINT32"),
                ],
                type_size = "SEQ8",
            ),
            max_count = 0xffff,
            cont = "",
        ),
    )
    assert sdp.parse(b) == c, sdp.parse(b)
    assert sdp.build(c) == b

def test14():
    b = h2b("07 00 00 02 21 02 1E 36 02 1B 36 01 C3 09 00 00 0A 00 01 00 00 09 00 01 35 03 19 11 24 09 00 04 35 0D 35 06 19 01 00 09 00 11 35 03 19 00 11 09 00 05 35 03 19 10 02 09 00 06 35 09 09 65 6E 09 00 6A 09 01 00 09 00 09 35 08 35 06 19 11 24 09 01 00 09 00 0D 35 0F 35 0D 35 06 19 01 00 09 00 13 35 03 19 00 11 09 01 00 25 17 41 70 70 6C 65 20 57 69 72 65 6C 65 73 73 20 4B 65 79 62 6F 61 72 64 09 01 01 25 08 4B 65 79 62 6F 61 72 64 09 01 02 25 0A 41 70 70 6C 65 20 49 6E 63 2E 09 02 01 09 01 11 09 02 02 08 40 09 02 03 08 21 09 02 04 28 01 09 02 05 28 01 09 02 06 35 E6 35 E4 08 22 25 E0 05 01 09 02 A1 01 85 02 09 01 A1 00 05 09 19 01 29 08 15 00 25 01 95 08 75 01 81 02 05 01 09 30 09 31 09 38 15 81 25 7F 75 08 95 03 81 06 C0 C0 05 01 09 06 A1 01 85 01 75 01 95 08 05 07 19 E0 29 E7 15 00 25 01 81 02 95 01 75 08 81 03 95 06 75 08 15 00 26 FF 00 05 07 19 00 29 FF 81 00 95 05 75 01 05 08 85 01 19 01 29 05 91 02 95 01 75 03 91 03 C0 05 01 09 80 A1 01 85 04 75 08 95 01 15 00 25 01 19 81 29 83 81 00 C0 05 0C 09 01 A1 01 85 06 15 00 25 01 75 01 95 17 0A 23 02 0A B1 01 09 30 0A 25 02 0A 21 02 09 CD 09 B8 09 B6 09 B5 09 E9 09 EA 09 E2 0A 94 01 0A 92 01 0A 83 01 0A 8A 01 0A 27 02 0A 24 02 0A 2A 02 0A 26 02 0A 96 01 09 B7 0A 82 01 81 02 95 01 75 01 81 03 C0 09 02 07 35 08 35 06 09 04 09 09 01 00 09 02 09 28 01 09 02 0A 28 01 09 02 0B 09 01 00 09 02 0C 09 1F 40 09 02 0D 28 01 09 02 0E 28 01 36 00 52 09 00 00 0A 00 01 00 01 09 00 01 35 03 19 12 00 09 00 04 35 0D 35 06 19 01 00 09 00 01 35 03 19 00 01 09 00 09 35 08 35 06 19 12 00 09 01 00 09 02 00 09 01 00 09 02 01 09 05 AC 09 02 02 09 02 2C 09 02 03 09 01 40 09 02 04 28 01 09 02 05 09 00 02 00")
    c = Container(
        pdu_id = 'SVC_SEARCH_ATTR_RSP',
        tid = 0,
        params = Container(
            attr_lists = Container(
                type_size = 'SEQ16',
                data = [
                    Container(
                        type_size = 'SEQ16',
                        data = [
                            Container(data = 0x0000, type_size = 'UINT16'),
                            Container(data = 0x10000, type_size = 'UINT32'),
                            Container(data = 0x0001, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(data = 'HID', type_size = 'UUID16'),
                                ],
                            ),
                            Container(data = 0x0004, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(
                                        type_size = 'SEQ8',
                                        data = [
                                            Container(data = 'L2CAP', type_size = 'UUID16'),
                                            Container(data = 0x0011, type_size = 'UINT16'),
                                        ],
                                    ),
                                    Container(
                                        type_size = 'SEQ8',
                                        data = [
                                            Container(data = 'HIDP', type_size = 'UUID16'),
                                        ],
                                    ),
                                ],
                            ),
                            Container(data = 0x0005, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(data = 'PUBLIC_BROWSE_GROUP', type_size = 'UUID16'),
                                ],
                            ),
                            Container(data = 0x0006, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(data = 0x656e, type_size = 'UINT16'),
                                    Container(data = 0x006a, type_size = 'UINT16'),
                                    Container(data = 0x0100, type_size = 'UINT16'),
                                ],
                            ),
                            Container(data = 0x0009, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(
                                        type_size = 'SEQ8',
                                        data = [
                                            Container(data = 'HID', type_size = 'UUID16'),
                                            Container(data = 0x0100, type_size = 'UINT16'),
                                        ],
                                    ),
                                ],
                            ),
                            Container(data = 0x000d, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(
                                        type_size = 'SEQ8',
                                        data = [
                                            Container(
                                                type_size = 'SEQ8',
                                                data = [
                                                    Container(data = 'L2CAP', type_size = 'UUID16'),
                                                    Container(data = 0x0013, type_size = 'UINT16'),
                                                ],
                                            ),
                                            Container(
                                                type_size = 'SEQ8',
                                                data = [
                                                    Container(data = 'HIDP', type_size = 'UUID16'),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            Container(data = 0x0100, type_size = 'UINT16'),
                            Container(data = 'Apple Wireless Keyboard', type_size = 'STR8'),
                            Container(data = 0x0101, type_size = 'UINT16'),
                            Container(data = 'Keyboard', type_size = 'STR8'),
                            Container(data = 0x0102, type_size = 'UINT16'),
                            Container(data = 'Apple Inc.', type_size = 'STR8'),
                            Container(data = 0x0201, type_size = 'UINT16'),
                            Container(data = 0x0111, type_size = 'UINT16'),
                            Container(data = 0x0202, type_size = 'UINT16'),
                            Container(data = 0x40, type_size = 'UINT8'),
                            Container(data = 0x0203, type_size = 'UINT16'),
                            Container(data = 0x21, type_size = 'UINT8'),
                            Container(data = 0x0204, type_size = 'UINT16'),
                            Container(data = True, type_size = 'BOOL'),
                            Container(data = 0x0205, type_size = 'UINT16'),
                            Container(data = True, type_size = 'BOOL'),
                            Container(data = 0x0206, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(
                                        type_size = 'SEQ8',
                                        data = [
                                            Container(data = 0x22, type_size = 'UINT8'),
                                            Container(
                                                type_size = 'STR8',
                                                data = "\x05\x01\t\x02\xa1\x01\x85\x02\t\x01\xa1\x00\x05\t\x19\x01)\x08\x15\x00%\x01\x95\x08u\x01\x81\x02\x05\x01\t0\t1\t8\x15\x81%\x7fu\x08\x95\x03\x81\x06\xc0\xc0\x05\x01\t\x06\xa1\x01\x85\x01u\x01\x95\x08\x05\x07\x19\xe0)\xe7\x15\x00%\x01\x81\x02\x95\x01u\x08\x81\x03\x95\x06u\x08\x15\x00&\xff\x00\x05\x07\x19\x00)\xff\x81\x00\x95\x05u\x01\x05\x08\x85\x01\x19\x01)\x05\x91\x02\x95\x01u\x03\x91\x03\xc0\x05\x01\t\x80\xa1\x01\x85\x04u\x08\x95\x01\x15\x00%\x01\x19\x81)\x83\x81\x00\xc0\x05\x0c\t\x01\xa1\x01\x85\x06\x15\x00%\x01u\x01\x95\x17\n#\x02\n\xb1\x01\t0\n%\x02\n!\x02\t\xcd\t\xb8\t\xb6\t\xb5\t\xe9\t\xea\t\xe2\n\x94\x01\n\x92\x01\n\x83\x01\n\x8a\x01\n'\x02\n$\x02\n*\x02\n&\x02\n\x96\x01\t\xb7\n\x82\x01\x81\x02\x95\x01u\x01\x81\x03\xc0",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            Container(data = 0x0207, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(
                                        type_size = 'SEQ8',
                                        data = [
                                            Container(data = 0x0409, type_size = 'UINT16'),
                                            Container(data = 0x0100, type_size = 'UINT16'),
                                        ],
                                    ),
                                ],
                            ),
                            Container(data = 0x0209, type_size = 'UINT16'),
                            Container(data = True, type_size = 'BOOL'),
                            Container(data = 0x020a, type_size = 'UINT16'),
                            Container(data = True, type_size = 'BOOL'),
                            Container(data = 0x020b, type_size = 'UINT16'),
                            Container(data = 0x0100, type_size = 'UINT16'),
                            Container(data = 0x020c, type_size = 'UINT16'),
                            Container(data = 0x1f40, type_size = 'UINT16'),
                            Container(data = 0x020d, type_size = 'UINT16'),
                            Container(data = True, type_size = 'BOOL'),
                            Container(data = 0x020e, type_size = 'UINT16'),
                            Container(data = True, type_size = 'BOOL'),
                        ],
                    ),
                    Container(
                        type_size = 'SEQ16',
                        data = [
                            Container(data = 0x0000, type_size = 'UINT16'),
                            Container(data = 0x10001, type_size = 'UINT32'),
                            Container(data = 0x0001, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(data = 'PNP_INFO', type_size = 'UUID16'),
                                ],
                            ),
                            Container(data = 0x0004, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(
                                        type_size = 'SEQ8',
                                        data = [
                                            Container(data = 'L2CAP', type_size = 'UUID16'),
                                            Container(data = 0x0001, type_size = 'UINT16'),
                                        ],
                                    ),
                                    Container(
                                        type_size = 'SEQ8',
                                        data = [
                                            Container(data = 'SDP', type_size = 'UUID16'),
                                        ],
                                    ),
                                ],
                            ),
                            Container(data = 0x0009, type_size = 'UINT16'),
                            Container(
                                type_size = 'SEQ8',
                                data = [
                                    Container(
                                        type_size = 'SEQ8',
                                        data = [
                                            Container(data = 'PNP_INFO', type_size = 'UUID16'),
                                            Container(data = 0x0100, type_size = 'UINT16'),
                                        ],
                                    ),
                                ],
                            ),
                            Container(data = 0x0200, type_size = 'UINT16'),
                            Container(data = 0x0100, type_size = 'UINT16'),
                            Container(data = 0x0201, type_size = 'UINT16'),
                            Container(data = 0x05ac, type_size = 'UINT16'),
                            Container(data = 0x0202, type_size = 'UINT16'),
                            Container(data = 0x022c, type_size = 'UINT16'),
                            Container(data = 0x0203, type_size = 'UINT16'),
                            Container(data = 0x0140, type_size = 'UINT16'),
                            Container(data = 0x0204, type_size = 'UINT16'),
                            Container(data = True, type_size = 'BOOL'),
                            Container(data = 0x0205, type_size = 'UINT16'),
                            Container(data = 0x0002, type_size = 'UINT16'),
                        ],
                    ),
                ],
            ),
            cont = '',
        ),
    )
    assert sdp.parse(b) == c, sdp.parse(b)
    assert sdp.build(c) == b
