from bt_lib.hci.transport import uart

def test():
    #HCI Command: Read Local Supported Features (0x04|0x0003) plen 0
    d = uart.parse("01031000".decode("hex"))
    assert d.packet_indicator == "COMMAND"
    assert d.packet.ogf == "INFO_PARAM"
    assert d.packet.ocf == "READ_LOCAL_FEATURES"
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
    assert d.packet.ogf == "HOST_CTL"
    assert d.packet.ocf == "READ_CLASS_OF_DEV"
    assert d.packet.plen == 0
