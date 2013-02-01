pkt_indicator = (
    (1, "HCI Command"),
    (2, "ACL Data"),
    (3, "SCO Data"),
    (4, "HCI Event"),
)

ogf_list = (
    (1, "Link Control Commands"),
    (2, "Link Policy Commands"),
    (3, "Controller & Baseband Commands"),
    (4, "Informational Parameters"),
    (5, "Status Parameters"),
    (6, "Testing Commands"),
    (8, "LE Controller Commands"),
)

ocf = {}

ocf[1] = (
    (0x01, "Inquiry"),
    (0x02, "Inquiry Cancel"),
    (0x03, "Periodic Inquiry Mode"),
    (0x04, "Exit Periodic Inquiry Mode"),
    (0x05, "Create Connection"),
    (0x06, "Disconnect"),
    (0x07, "Add SCO Connection"),
    (0x08, "Create Connection Cancel"),
    (0x09, "Accept Connection Request"),
    (0x0a, "Reject Connection Request"),
    (0x0b, "Link Key Request Reply"),
    (0x0c, "Link Key Request Negative Reply"),
    (0x0d, "PIN Code Request Reply"),
    (0x0e, "PIN Code Request Negative Reply"),
    (0x0f, "Change Connection Packet Type"),
    # 0x10 - reserved command
    (0x11, "Authentication Requested"),
    # 0x12 - reserved command
    (0x13, "Set Connection Encryption"),
    # 0x14 - reserved command
    (0x15, "Change Connection Link Key"),
    # 0x16 - reserved command
    (0x17, "Master Link Key"),
    # 0x18 - reserved command
    (0x19, "Remote Name Request"),
    (0x1a, "Remote Name Request Cancel"),
    (0x1b, "Read Remote Supported Features"),
    (0x1c, "Read Remote Extended Features"),
    (0x1d, "Read Remote Version Information"),
    # 0x1e - reserved command
    (0x1f, "Read Clock Offset"),
    (0x20, "Read LMP Handle"),
    # 0x21-0x27 - reserved commands
    (0x28, "Setup Synchronous Connection"),
    (0x29, "Accept Synchronous Connection"),
    (0x2a, "Reject Synchronous Connection"),
    (0x2b, "IO Capability Request Reply"),
    (0x2c, "User Confirmation Request Reply"),
    (0x2d, "User Confirmation Request Neg Reply"),
    (0x2e, "User Passkey Request Reply"),
    (0x2f, "User Passkey Request Negative Reply"),
    (0x30, "Remote OOB Data Request Reply"),
    # 0x31-0x32 - reserved commands
    (0x33, "Remote OOB Data Request Neg Reply"),
    (0x34, "IO Capability Request Negative Reply"),
    (0x35, "Create Physical Link"),
    (0x36, "Accept Physical Link"),
    (0x37, "Disconnect Physical Link"),
    (0x38, "Create Logical Link"),
    (0x39, "Accept Logical Link"),
    (0x3a, "Disconnect Logical Link"),
    (0x3b, "Logical Link Cancel"),
    (0x3c, "Flow Specifcation Modify"),
    (0x3d, "Enhanced Setup Synchronous Connection"),
    (0x3e, "Enhanced Accept Synchronous Connection"),
)

ocf[2] = (
    (0x01, "Holde Mode"),
    # 0x02 - reserved command
    (0x03, "Sniff Mode"),
    (0x04, "Exit Sniff Mode"),
    (0x05, "Park State"),
    (0x06, "Exit Park State"),
    (0x07, "QoS Setup"),
    # 0x08 - reserved command
    (0x09, "Role Discovery"),
    # 0x0a - reserved command
    (0x0b, "Switch Role"),
    (0x0c, "Read Link Policy Settings"),
    (0x0d, "Write Link Policy Settings"),
    (0x0e, "Read Default Link Policy Settings"),
    (0x0f, "Write Default Link Policy Settings"),
    (0x10, "Flow Specification"),
    (0x11, "Sniff Subrating"),
)

ocf[3] = (
    (0x01, "Set Event Mask"),
    # 0x02 - reserved command
    (0x03, "Reset"),
    # 0x04 - reserved command
    (0x05, "Set Event Filter"),
    # 0x06-0x07 - reserved commands
    (0x08, "Flush"),
    (0x09, "Read PIN Type"),
    (0x0a, "Write PIN Type"),
    (0x0b, "Create New Unit Key"),
    # 0x0c - reserved command
    (0x0d, "Read Stored Link Key"),
    # 0x0e-0x010 - reserved commands
    (0x11, "Write Stored Link Key"),
    (0x12, "Delete Stored Link Key"),
    (0x13, "Write Local Name"),
    (0x14, "Read Local Name"),
    (0x15, "Read Connection Accept Timeout"),
    (0x16, "Write Connection Accept Timeout"),
    (0x17, "Read Page Timeout"),
    (0x18, "Write Page Timeout"),
    (0x19, "Read Scan Enable"),
    (0x1a, "Write Scan Enable"),
    (0x1b, "Read Page Scan Activity"),
    (0x1c, "Write Page Scan Activity"),
    (0x1d, "Read Inquiry Scan Activity"),
    (0x1e, "Write Inquiry Scan Activity"),
    (0x1f, "Read Authentication Enable"),
    (0x20, "Write Authentication Enable"),
    (0x21, "Read Encryption Mode"),
    (0x22, "Write Encryption Mode"),
    (0x23, "Read Class of Device"),
    (0x24, "Write Class of Device"),
    (0x25, "Read Voice Setting"),
    (0x26, "Write Voice Setting"),
    (0x27, "Read Automatic Flush Timeout"),
    (0x28, "Write Automatic Flush Timeout"),
    (0x29, "Read Num Broadcast Retransmissions"),
    (0x2a, "Write Num Broadcast Retransmissions"),
    (0x2b, "Read Hold Mode Activity"),
    (0x2c, "Write Hold Mode Activity"),
    (0x2d, "Read Transmit Power Level"),
    (0x2e, "Read Sync Flow Control Enable"),
    (0x2f, "Write Sync Flow Control Enable"),
    # 0x30 - reserved command
    (0x31, "Set Host Controller To Host Flow"),
    # 0x32 - reserved command
    (0x33, "Host Buffer Size"),
    # 0x34 - reserved command
    (0x35, "Host Number of Completed Packets"),
    (0x36, "Read Link Supervision Timeout"),
    (0x37, "Write Link Supervision Timeout"),
    (0x38, "Read Number of Supported IAC"),
    (0x39, "Read Current IAC LAP"),
    (0x3a, "Write Current IAC LAP"),
    (0x3b, "Read Page Scan Period Mode"),
    (0x3c, "Write Page Scan Period Mode"),
    (0x3d, "Read Page Scan Mode"),
    (0x3e, "Write Page Scan Mode"),
    (0x3f, "Set AFH Host Channel Classification"),
    # 0x40-0x41 - reserved commands
    (0x42, "Read Inquiry Scan Type"),
    (0x43, "Write Inquiry Scan Type"),
    (0x44, "Read Inquiry Mode"),
    (0x45, "Write Inquiry Mode"),
    (0x46, "Read Page Scan Type"),
    (0x47, "Write Page Scan Type"),
    (0x48, "Read AFH Channel Assessment Mode"),
    (0x49, "Write AFH Channel Assessment Mode"),
    # 0x4a-0x50 - reserved commands
    (0x51, "Read Extended Inquiry Response"),
    (0x52, "Write Extended Inquiry Response"),
    (0x53, "Refresh Encryption Key"),
    # 0x54 - reserved command
    (0x55, "Read Simple Pairing Mode"),
    (0x56, "Write Simple Pairing Mode"),
    (0x57, "Read Local OOB Data"),
    (0x58, "Read Inquiry Response TX Power Level"),
    (0x59, "Write Inquiry Transmit Power Level"),
    (0x5a, "Read Default Erroneous Reporting"),
    (0x5b, "Write Default Erroneous Reporting"),
    # 0x5c-0x5e - reserved commands
    (0x5f, "Enhanced Flush"),
    (0x60, "Send Keypress Notification"),
    (0x61, "Read Logical Link Accept Timeout"),
    (0x62, "Write Logical Link Accept Timeout"),
    (0x63, "Set Event Mask Page 2"),
    (0x64, "Read Location Data"),
    (0x65, "Write Location Data"),
    (0x66, "Read Flow Control Mode"),
    (0x67, "Write Flow Control Mode"),
    (0x68, "Read Enhanced Transmit Power Level"),
    (0x69, "Read Best Effort Flush Timeout"),
    (0x6a, "Write Best Effort Flush Timeout"),
    (0x6b, "Short Range Mode"),
    (0x6c, "Read LE Host Supported"),
    (0x6d, "Write LE Host Supported"),
    (0x6e, "Set MWS Channel Parameters"),
    (0x6f, "Set External Fram Configuration"),
    (0x70, "Set MWS Signaling"),
    (0x71, "Set MWS Transport Layer"),
    (0x72, "Set MWS Scan Frequency Table"),
    (0x73, "Set MWS Pattern Configuration"),
)

ocf[4] = (
    (0x01, "Read Local Version Information"),
    (0x02, "Read Local Supported Commands"),
    (0x03, "Read Local Supported Features"),
    (0x04, "Read Local Extended Features"),
    (0x05, "Read Buffer Size"),
    # 0x06 - reserved command
    (0x07, "Read Country Code"),
    # 0x08 - reserved command
    (0x09, "Read BD ADDR"),
    (0x0a, "Read Data Block Size"),
    (0x0b, "Read Local Supported Codecs"),
)

ocf[5] = (
    (0x01, "Read Failed Contact Counter"),
    (0x02, "Reset Failed Contact Counter"),
    (0x03, "Read Link Quality"),
    # 0x04 - reserved command
    (0x05, "Read RSSI"),
    (0x06, "Read AFH Channel Map"),
    (0x07, "Read Clock"),
    (0x08, "Read Encryption Key Size"),
    (0x09, "Read Local AMP Info"),
    (0x0a, "Read Local AMP ASSOC"),
    (0x0b, "Write Remote AMP ASSOC"),
    (0x0c, "Get MWS Transport Layer Configuration"),
)

ocf[6] = (
    (0x01, "Read Loopback Mode"),
    (0x02, "Write Loopback Mode"),
    (0x03, "Enable Device Under Test Mode"),
    (0x04, "Write Simple Pairing Debug Mode"),
    # 0x05-0x06 - reserved commands
    (0x07, "Enable AMP Receiver Reports"),
    (0x08, "AMP Test End"),
    (0x09, "AMP Test"),
)

ocf[8] = (
    (0x01, "LE Set Event Mask"),
    (0x02, "LE Read Buffer Size"),
    (0x03, "LE Read Local Supported Features"),
    # 0x04 - reserved command
    (0x05, "LE Set Random Address"),
    (0x06, "LE Set Advertising Parameters"),
    (0x07, "LE Read Advertising Channel TX Power"),
    (0x08, "LE Set Advertising Data"),
    (0x09, "LE Set Scan Response Data"),
    (0x0a, "LE Set Advertise Enable"),
    (0x0b, "LE Set Scan Parameters"),
    (0x0c, "LE Set Scan Enable"),
    (0x0d, "LE Create Connection"),
    (0x0e, "LE Create Connection Cancel"),
    (0x0f, "LE Read White List Size"),
    (0x10, "LE Clear White List"),
    (0x11, "LE Add Device To White List"),
    (0x12, "LE Remove Device From White List"),
    (0x13, "LE Connection Update"),
    (0x14, "LE Set Host Channel Classification"),
    (0x15, "LE Read Channel Map"),
    (0x16, "LE Read Remote Used Features"),
    (0x17, "LE Encrypt"),
    (0x18, "LE Rand"),
    (0x19, "LE Start Encryption"),
    (0x1a, "LE Long Term Key Request Reply"),
    (0x1b, "LE Long Term Key Request Neg Reply"),
    (0x1c, "LE Read Supported States"),
    (0x1d, "LE Receiver Test"),
    (0x1e, "LE Transmitter Test"),
    (0x1f, "LE Test End"),
)
