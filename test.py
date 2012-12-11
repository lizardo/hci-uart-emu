from bt_lib.hci.transport import uart

def test():
    #HCI Command: Read Local Supported Features (0x04|0x0003) plen 0
    d = uart.parse("01031000".decode("hex"))
    assert d.packet_indicator == "COMMAND"
    assert d.packet.opcode.ogf == "INFO_PARAM"
    assert d.packet.opcode.ocf == "READ_LOCAL_FEATURES"
    assert d.packet.plen == 0

    # HCI Event: Command Complete (0x0e) plen 12
    #     Read Local Supported Features (0x04|0x0003) ncmd 1
    #     status 0x00
    #     Features: 0xa4 0x08 0x00 0xc0 0x58 0x1e 0x7b 0x83
    d = uart.parse("04 0E 0C 01 03 10 00 A4 08 00 C0 58 1E 7B 83".replace(" ","").decode("hex"))
    assert d.packet_indicator == "EVENT"
    assert d.packet.plen == 12
    assert d.packet.pdata.rparams.status == 0x00
    assert d.packet.pdata.rparams.features == [0xa4, 0x08, 0x00, 0xc0, 0x58, 0x1e, 0x7b, 0x83]

    # HCI Event: Command Complete (0x0e) plen 12
    #     Read Local Version Information (0x04|0x0001) ncmd 1
    #     status 0x00
    #     HCI Version: 4.0 (0x6) HCI Revision: 0x0
    #     LMP Version: 4.0 (0x6) LMP Subversion: 0x0
    #     Manufacturer: Bluetooth SIG, Inc (63)
    d = uart.parse("04 0E 0C 01 01 10 00 06 00 00 06 3F 00 00 00".replace(" ","").decode("hex"))
    assert d.packet_indicator == "EVENT"
    assert d.packet.plen == 12
    assert d.packet.pdata.rparams.status == 0x00
    assert d.packet.pdata.rparams.hci_ver == 0x06
    assert d.packet.pdata.rparams.hci_rev == 0x00
    assert d.packet.pdata.rparams.lmp_ver == 0x06
    assert d.packet.pdata.rparams.lmp_subver == 0x0000
    assert d.packet.pdata.rparams.manufacturer == 63

    # HCI Event: Command Complete (0x0e) plen 10
    #     Read BD ADDR (0x04|0x0009) ncmd 1
    #     status 0x00 bdaddr 00:AA:01:00:00:42
    d = uart.parse("04 0E 0A 01 09 10 00 42 00 00 01 AA 00".replace(" ","").decode("hex"))
    assert d.packet_indicator == "EVENT"
    assert d.packet.plen == 10
    assert d.packet.pdata.rparams.status == 0x00
    assert d.packet.pdata.rparams.bdaddr == [0x42, 0x00, 0x00, 0x01, 0xaa, 0x00]

    # HCI Command: Read Class of Device (0x03|0x0023) plen 0
    d = uart.parse("01 23 0C 00".replace(" ","").decode("hex"))
    assert d.packet_indicator == "COMMAND"
    assert d.packet.opcode.ogf == "HOST_CTL"
    assert d.packet.opcode.ocf == "READ_CLASS_OF_DEV"
    assert d.packet.plen == 0

    # HCI Command: Set Event Filter (0x03|0x0005) plen 1
    #     type 0 condition 0
    #     Clear all filters
    d = uart.parse("01 05 0C 01 00".replace(" ","").decode("hex"))
    assert d.packet_indicator == "COMMAND"
    assert d.packet.opcode.ogf == "HOST_CTL"
    assert d.packet.opcode.ocf == "SET_EVENT_FLT"
    assert d.packet.plen == 1
    assert d.packet.pdata.flt_type == "CLEAR_ALL"

    # HCI Command: Write Connection Accept Timeout (0x03|0x0016) plen 2
    #     timeout 32000
    d = uart.parse("01 16 0C 02 00 7D".replace(" ","").decode("hex"))
    assert d.packet_indicator == "COMMAND"
    assert d.packet.opcode.ogf == "HOST_CTL"
    assert d.packet.opcode.ocf == "WRITE_CONN_ACCEPT_TIMEOUT"
    assert d.packet.plen == 2
    assert d.packet.pdata.timeout == 32000

    # HCI Command: Delete Stored Link Key (0x03|0x0012) plen 7
    #     bdaddr 00:00:00:00:00:00 all 1
    d = uart.parse("01 12 0C 07 00 00 00 00 00 00 01".replace(" ","").decode("hex"))
    assert d.packet_indicator == "COMMAND"
    assert d.packet.opcode.ogf == "HOST_CTL"
    assert d.packet.opcode.ocf == "DELETE_STORED_LINK_KEY"
    assert d.packet.plen == 7
    assert d.packet.pdata.bdaddr == [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    assert d.packet.pdata.delete_all == 0x01

    # HCI Event: Command Complete (0x0e) plen 6
    #     Delete Stored Link Key (0x03|0x0012) ncmd 1
    #     status 0x00 deleted 0
    d = uart.parse("04 0E 06 01 12 0C 00 00 00".replace(" ","").decode("hex"))
    assert d.packet_indicator == "EVENT"
    assert d.packet.plen == 6
    assert d.packet.pdata.rparams.status == 0x00
    assert d.packet.pdata.rparams.num_keys == 0x0000
