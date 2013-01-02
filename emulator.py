from construct import Container
from bt_lib.sdp import sdp

class Device(object):
    def __init__(self, name, bdaddr):
        self.name = name
        self.bdaddr = [int(bdaddr.split(":")[i], 16) for i in [1, 0, 3, 2, 5, 4]]

class Adapter(object):
    def __init__(self, name, bdaddr):
        self.name = name
        self.bdaddr = [int(bdaddr.split(":")[i], 16) for i in [1, 0, 3, 2, 5, 4]]
        self.devices = []
        self.connections = {}
        self.cid_table = {}
        self.last_l2cap_cmd_ident = 0

    def add_device(self, device):
        self.devices.append(device)

    def process_command(self, packet):
        ocf = packet.opcode.ocf

        def cmd_complete(rparams):
            return Container(
                packet_indicator = 'EVENT',
                packet = Container(
                    evt = 'CMD_COMPLETE',
                    params = Container(
                        opcode = packet.opcode,
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
                        opcode = packet.opcode,
                    )
                )
            )

        c = []
        if ocf == "READ_LOCAL_FEATURES":
            c.append(cmd_complete(Container(status = 0,
                features = [164, 8, 0, 192, 88, 30, 123, 131],
            )))
        elif ocf == "READ_LOCAL_VERSION":
            c.append(cmd_complete(Container(status = 0,
                hci_ver = 6,
                hci_rev = 0,
                lmp_subver = 0,
                lmp_ver = 6,
                manufacturer = 63,
            )))
        elif ocf == "READ_BD_ADDR":
            c.append(cmd_complete(Container(status = 0,
                bdaddr = self.bdaddr,
            )))
        elif ocf == "READ_BUFFER_SIZE":
            c.append(cmd_complete(Container(status = 0,
                acl_mtu = 192,
                acl_max_pkt = 1,
                sco_max_pkt = 0,
                sco_mtu = 0,
            )))
        elif ocf == "READ_CLASS_OF_DEV":
            c.append(cmd_complete(Container(status = 0,
                dev_class = [0, 0, 0],
            )))
        elif ocf == "READ_LOCAL_NAME":
            c.append(cmd_complete(Container(status = 0,
                name = self.name,
            )))
        elif ocf == "READ_VOICE_SETTING":
            c.append(cmd_complete(Container(status = 0,
                voice_setting = 0x0000,
            )))
        elif ocf == "SET_EVENT_FLT":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "WRITE_CONN_ACCEPT_TIMEOUT":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "DELETE_STORED_LINK_KEY":
            c.append(cmd_complete(Container(status = 0,
                num_keys = 0,
            )))
        elif ocf == "LE_READ_BUFFER_SIZE":
            c.append(cmd_complete(Container(status = 0,
                pkt_len = 0x00c0,
                max_pkt = 0x01,
            )))
        elif ocf == "LE_READ_ADVERTISING_CHANNEL_TX_POWER":
            c.append(cmd_complete(Container(status = 0,
                level = 0,
            )))
        elif ocf == "SET_EVENT_MASK":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "LE_SET_EVENT_MASK":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "READ_LOCAL_COMMANDS":
            c.append(cmd_complete(Container(status = 0,
                commands = [0] * 64,
            )))
        elif ocf == "WRITE_SIMPLE_PAIRING_MODE":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "WRITE_INQUIRY_MODE":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "READ_INQ_RESPONSE_TX_POWER_LEVEL":
            c.append(cmd_complete(Container(status = 0,
                level = 0,
            )))
        elif ocf == "READ_LOCAL_EXT_FEATURES":
            assert packet.params.page_num == 1
            c.append(cmd_complete(Container(status = 0,
                page_num = 1,
                max_page_num = 1,
                features = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            )))
        elif ocf == "WRITE_LE_HOST_SUPPORTED":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "LE_SET_ADVERTISING_DATA":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "WRITE_SCAN_ENABLE":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "WRITE_CLASS_OF_DEV":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "CHANGE_LOCAL_NAME":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "WRITE_EXT_INQUIRY_RESPONSE":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "RESET":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "LE_SET_SCAN_PARAMETERS":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "LE_SET_SCAN_ENABLE":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "INQUIRY":
            c.append(cmd_status(0))
            for d in self.devices:
                c.append(Container(
                    packet_indicator = "EVENT",
                    packet = Container(
                        evt = "INQUIRY_RESULT",
                        params = Container(
                            num_rsp = 1,
                            bdaddr = d.bdaddr,
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
        elif ocf == "INQUIRY_CANCEL":
            c.append(cmd_complete(Container(status = 0)))
        elif ocf == "CREATE_CONN":
            dev, = filter(lambda d: d.bdaddr == packet.params.bdaddr, self.devices)
            assert dev not in self.connections.values()
            handle = max(self.connections.keys()) + 1 if self.connections else 0x0001
            self.connections[handle] = dev
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "CONN_COMPLETE",
                    params = Container(
                        status = 0,
                        handle = handle,
                        bdaddr = packet.params.bdaddr,
                        link_type = 0x01,
                        encr_mode = 0x00,
                    )
                )
            ))
        elif ocf == "DISCONNECT":
            del self.connections[packet.params.handle]
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "DISCONN_COMPLETE",
                    params = Container(
                        status = 0,
                        handle = packet.params.handle,
                        reason = 0x16, # Connection Terminated By Local Host
                    )
                )
            ))
        elif ocf == "READ_REMOTE_FEATURES":
            assert self.connections.get(packet.params.handle)
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "READ_REMOTE_FEATURES_COMPLETE",
                    params = Container(
                        status = 0,
                        handle = packet.params.handle,
                        features = [0xa4, 0x08, 0x00, 0xc0, 0x58, 0x1e, 0x7b, 0x83],
                    )
                )
            ))
        elif ocf == "READ_REMOTE_EXT_FEATURES":
            assert self.connections.get(packet.params.handle)
            assert packet.params.page_num == 1
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "READ_REMOTE_EXT_FEATURES_COMPLETE",
                    params = Container(
                        status = 0,
                        handle = packet.params.handle,
                        page_num = 1,
                        max_page_num = 1,
                        features = [0x00] * 8,
                    )
                )
            ))
        elif ocf == "REMOTE_NAME_REQ":
            dev, = filter(lambda d: d.bdaddr == packet.params.bdaddr, self.devices)
            c.append(cmd_status(0))
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "REMOTE_NAME_REQ_COMPLETE",
                    params = Container(
                        status = 0,
                        bdaddr = dev.bdaddr,
                        name = dev.name,
                    )
                )
            ))
        elif ocf == "AUTH_REQUESTED":
            assert self.connections.get(packet.params.handle)
            c.append(cmd_status(0))
            # assume not in SSP mode
            c.append(Container(
                packet_indicator = "EVENT",
                packet = Container(
                    evt = "AUTH_COMPLETE",
                    params = Container(
                        status = 0,
                        handle = packet.params.handle,
                    )
                )
            ))
        else:
            raise NotImplementedError, "Unsupported packet: %s" % d

        return c

    def new_l2cap_cmd_ident(self):
        if self.last_l2cap_cmd_ident == 255:
            print("WARNING: recycling L2CAP command ident")
            self.last_l2cap_cmd_ident = 0

        self.last_l2cap_cmd_ident += 1

        return self.last_l2cap_cmd_ident

    def process_acl_data(self, packet):
        assert self.connections.get(packet.header.handle)
        c = []
        if packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'INFO_REQ' and \
                packet.data.data.data.type == 'FEAT_MASK':
            c.append(Container(
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
            ))
        elif packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'INFO_REQ' and \
                packet.data.data.data.type == 'FIXED_CHAN':
            c.append(Container(
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
            ))
        elif packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'CONN_REQ':
            self.cid_table[packet.data.data.data.scid] = packet.data.data.data.psm
            c.append(Container(
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
            ))
        elif packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'DISCONN_REQ':
            del self.cid_table[packet.data.data.data.scid]
            c.append(Container(
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
            ))
        elif packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'CONF_REQ':
            c.append(Container(
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
                                l2cap_conf_opt = [
                                    Container(type = 'MTU', data = 672),
                                ],
                            ),
                        ),
                    )
                )
            ))
            c.append(Container(
                packet_indicator = 'ACLDATA',
                packet = Container(
                    header = Container(
                        handle = packet.header.handle,
                        flags = 'START',
                    ),
                    data = Container(
                        cid = 'SIGNALING',
                        data = Container(
                            ident = self.new_l2cap_cmd_ident(),
                            code = 'CONF_REQ',
                            data = Container(
                                # arbitrarily set DCID == SCID
                                dcid = packet.data.data.data.dcid,
                                flags = 0x0000,
                                l2cap_conf_opt = [
                                    Container(type = 'MTU', data = 672),
                                ],
                            ),
                        ),
                    )
                )
            ))
        elif packet.data.cid == 'SIGNALING' and \
                packet.data.data.code == 'CONF_RSP':
            print("DEBUG:", packet)
        elif self.cid_table.get(packet.data.cid):
            psm = self.cid_table[packet.data.cid]
            if psm == 'SDP':
                # SDP
                c.append(self.process_sdp(packet))
            else:
                raise NotImplementedError, "Unsupported PSM: %s" % psm
        else:
            raise NotImplementedError, "Unsupported ACL packet: %s" % packet

        comp_pkt_evt = Container(
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

        return c + len(c) * [comp_pkt_evt]

    def process_sdp(self, packet):
        UINT8 = lambda d: Container(data = d, type_size = 'UINT8')
        UINT16 = lambda d: Container(data = d, type_size = 'UINT16')
        UINT32 = lambda d: Container(data = d, type_size = 'UINT32')
        UUID16 = lambda d: Container(data = d, type_size = 'UUID16')
        SEQ8 = lambda *d: Container(data = list(d), type_size = 'SEQ8')
        SEQ16 = lambda *d: Container(data = list(d), type_size = 'SEQ16')
        STR8 = lambda d: Container(data = d, type_size = 'STR8')
        BOOL = lambda d: Container(data = d, type_size = 'BOOL')

        p = sdp.parse(packet.data.data)
        if p.pdu_id == "SVC_SEARCH_ATTR_REQ" and \
                p.params.pattern == SEQ8(UUID16("L2CAP")) and \
                p.params.attr_list == SEQ8(UINT32(0x0000ffff)):
            data = sdp.build(Container(
                pdu_id = 'SVC_SEARCH_ATTR_RSP',
                tid = p.tid,
                params = Container(
                    attr_lists = SEQ16(
                        SEQ16(
                            UINT16(0x0000),
                                UINT32(0x10000),
                            UINT16(0x0001),
                                SEQ8(UUID16('HID')),
                            UINT16(0x0004),
                                SEQ8(
                                    SEQ8(UUID16('L2CAP'), UINT16(0x0011)),
                                    SEQ8(UUID16('HIDP')),
                                ),
                            UINT16(0x0005),
                                SEQ8(UUID16('PUBLIC_BROWSE_GROUP')),
                            UINT16(0x0006),
                                SEQ8(
                                    UINT16(0x656e),
                                    UINT16(0x006a),
                                    UINT16(0x0100),
                                ),
                            UINT16(0x0009),
                                SEQ8(
                                    SEQ8(UUID16('HID'), UINT16(0x0100)),
                                ),
                            UINT16(0x000d),
                                SEQ8(
                                    SEQ8(
                                        SEQ8(UUID16('L2CAP'), UINT16(0x0013)),
                                        SEQ8(UUID16('HIDP')),
                                    ),
                                ),
                            UINT16(0x0100),
                                STR8('Apple Wireless Keyboard'),
                            UINT16(0x0101),
                                STR8('Keyboard'),
                            UINT16(0x0102),
                                STR8('Apple Inc.'),
                            UINT16(0x0201),
                                UINT16(0x0111),
                            UINT16(0x0202),
                                UINT8(0x40),
                            UINT16(0x0203),
                                UINT8(0x21),
                            UINT16(0x0204),
                                BOOL(True),
                            UINT16(0x0205),
                                BOOL(True),
                            UINT16(0x0206),
                                SEQ8(
                                    SEQ8(
                                        UINT8(0x22),
                                        STR8("\x05\x01\t\x02\xa1\x01\x85\x02\t\x01\xa1\x00\x05\t\x19\x01)\x08\x15\x00%\x01\x95\x08u\x01\x81\x02\x05\x01\t0\t1\t8\x15\x81%\x7fu\x08\x95\x03\x81\x06\xc0\xc0\x05\x01\t\x06\xa1\x01\x85\x01u\x01\x95\x08\x05\x07\x19\xe0)\xe7\x15\x00%\x01\x81\x02\x95\x01u\x08\x81\x03\x95\x06u\x08\x15\x00&\xff\x00\x05\x07\x19\x00)\xff\x81\x00\x95\x05u\x01\x05\x08\x85\x01\x19\x01)\x05\x91\x02\x95\x01u\x03\x91\x03\xc0\x05\x01\t\x80\xa1\x01\x85\x04u\x08\x95\x01\x15\x00%\x01\x19\x81)\x83\x81\x00\xc0\x05\x0c\t\x01\xa1\x01\x85\x06\x15\x00%\x01u\x01\x95\x17\n#\x02\n\xb1\x01\t0\n%\x02\n!\x02\t\xcd\t\xb8\t\xb6\t\xb5\t\xe9\t\xea\t\xe2\n\x94\x01\n\x92\x01\n\x83\x01\n\x8a\x01\n'\x02\n$\x02\n*\x02\n&\x02\n\x96\x01\t\xb7\n\x82\x01\x81\x02\x95\x01u\x01\x81\x03\xc0"),
                                    ),
                                ),
                            UINT16(0x0207),
                                SEQ8(
                                    SEQ8(UINT16(0x0409), UINT16(0x0100)),
                                ),
                            UINT16(0x0209),
                                BOOL(True),
                            UINT16(0x020a),
                                BOOL(True),
                            UINT16(0x020b),
                                UINT16(0x0100),
                            UINT16(0x020c),
                                UINT16(0x1f40),
                            UINT16(0x020d),
                                BOOL(True),
                            UINT16(0x020e),
                                BOOL(True),
                        ),
                        SEQ16(
                            UINT16(0x0000),
                                UINT32(0x10001),
                            UINT16(0x0001),
                                SEQ8(UUID16('PNP_INFO')),
                            UINT16(0x0004),
                                SEQ8(
                                    SEQ8(UUID16('L2CAP'), UINT16(0x0001)),
                                    SEQ8(UUID16('SDP')),
                                ),
                            UINT16(0x0009),
                                SEQ8(
                                    SEQ8(UUID16('PNP_INFO'), UINT16(0x0100)),
                                ),
                            UINT16(0x0200),
                                UINT16(0x0100),
                            UINT16(0x0201),
                                UINT16(0x05ac),
                            UINT16(0x0202),
                                UINT16(0x022c),
                            UINT16(0x0203),
                                UINT16(0x0140),
                            UINT16(0x0204),
                                BOOL(True),
                            UINT16(0x0205),
                                UINT16(0x0002),
                        ),
                    ),
                    cont = '',
                ),
            ))
        elif p.pdu_id == "SVC_SEARCH_ATTR_REQ" and \
                p.params.pattern == SEQ8(UUID16("PNP_INFO")) and \
                p.params.attr_list == SEQ8(UINT32(0x0000ffff)):
            data = sdp.build(Container(
                pdu_id = 'SVC_SEARCH_ATTR_RSP',
                tid = p.tid,
                params = Container(
                    attr_lists = SEQ16(
                        SEQ16(
                            UINT16(0x0000),
                                UINT32(0x10001),
                            UINT16(0x0001),
                                SEQ8(UUID16('PNP_INFO')),
                            UINT16(0x0004),
                                SEQ8(
                                    SEQ8(UUID16('L2CAP'), UINT16(0x0001)),
                                    SEQ8(UUID16('SDP')),
                                ),
                            UINT16(0x0009),
                                SEQ8(
                                    SEQ8(UUID16('PNP_INFO'), UINT16(0x0100)),
                                ),
                            UINT16(0x0200),
                                UINT16(0x100),
                            UINT16(0x201),
                                UINT16(0x5ac),
                            UINT16(0x0202),
                                UINT16(0x22c),
                            UINT16(0x0203),
                                UINT16(0x0140),
                            UINT16(0x0204),
                                BOOL(True),
                            UINT16(0x205),
                                UINT16(0x0002),
                        ),
                    ),
                    cont = '',
                ),
            ))
        else:
            raise NotImplementedError, "Unsupported SDP packet: %s" % p

        # Build ACL payload
        return Container(
            packet_indicator = 'ACLDATA',
            packet = Container(
                header = Container(
                    handle = packet.header.handle,
                    flags = 'START',
                ),
                data = Container(
                    cid = packet.data.cid,
                    data = data,
                )
            )
        )
