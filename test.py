from bt_lib.hci.transport import uart
from construct import Container

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
