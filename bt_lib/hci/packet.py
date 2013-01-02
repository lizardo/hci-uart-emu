from construct import *
from bt_lib.construct_helpers import *

# Link Control (OGF 0x01)

link_ctl_commands = Enum(BitField("ocf", 10),
    INQUIRY = 0x0001,
    INQUIRY_CANCEL = 0x0002,
    CREATE_CONN = 0x0005,
    DISCONNECT = 0x0006,
    AUTH_REQUESTED = 0x0011,
    REMOTE_NAME_REQ = 0x0019,
    READ_REMOTE_FEATURES = 0x001b,
    READ_REMOTE_EXT_FEATURES = 0x001c,
)

inquiry_cp = Struct("inquiry_cp",
    Array(3, ULInt8("lap")),
    ULInt8("length"),
    ULInt8("num_rsp"),
)

inquiry_cancel_rp = Struct("inquiry_cancel_rp",
    ULInt8("status"),
)

create_conn_cp = Struct("create_conn_cp",
    Array(6, ULInt8("bdaddr")),
    ULInt16("pkt_type"),
    ULInt8("pscan_rep_mode"),
    ULInt8("reserved"),
    ULInt16("clock_offset"),
    ULInt8("role_switch"),
)

disconnect_cp = Struct("disconnect_cp",
    ULInt16("handle"),
    ULInt8("reason"),
)

auth_requested_cp = Struct("auth_requested_cp",
    ULInt16("handle"),
)

remote_name_req_cp = Struct("remote_name_req_cp",
    Array(6, ULInt8("bdaddr")),
    ULInt8("pscan_rep_mode"),
    ULInt8("reserved"),
    ULInt16("clock_offset"),
)

read_remote_features_cp = Struct("read_remote_features_cp",
    ULInt16("handle"),
)

read_remote_ext_features_cp = Struct("read_remote_ext_features_cp",
    ULInt16("handle"),
    ULInt8("page_num"),
)

# Controller & Baseband (OGF 0x03)

host_ctl_commands = Enum(BitField("ocf", 10),
    SET_EVENT_MASK = 0x0001,
    RESET = 0x0003,
    SET_EVENT_FLT = 0x0005,
    DELETE_STORED_LINK_KEY = 0x0012,
    CHANGE_LOCAL_NAME = 0x0013,
    READ_LOCAL_NAME = 0x0014,
    WRITE_CONN_ACCEPT_TIMEOUT = 0x0016,
    WRITE_SCAN_ENABLE = 0x001a,
    READ_CLASS_OF_DEV = 0x0023,
    WRITE_CLASS_OF_DEV = 0x0024,
    READ_VOICE_SETTING = 0x0025,
    WRITE_INQUIRY_MODE = 0x0045,
    WRITE_EXT_INQUIRY_RESPONSE = 0x0052,
    WRITE_SIMPLE_PAIRING_MODE = 0x0056,
    READ_INQ_RESPONSE_TX_POWER_LEVEL = 0x0058,
    WRITE_LE_HOST_SUPPORTED = 0x006d,
)

set_event_mask_cp = Struct("set_event_mask_cp",
    Array(8, ULInt8("mask")),
)

set_event_mask_rp = Struct("set_event_mask_rp",
    ULInt8("status"),
)

reset_rp = Struct("reset_rp",
    ULInt8("status"),
)

set_event_flt_cp = Struct("set_event_flt_cp",
    Enum(ULInt8("flt_type"),
        CLEAR_ALL = 0x00,
        INQ_RESULT = 0x01,
        CONN_SETUP = 0x02,
    ),
    FixedIf(lambda ctx: ctx.flt_type != "CLEAR_ALL",
        Switch("cond_type", lambda ctx: ctx.flt_type,
            {
                "INQ_RESULT": Enum(ULInt8("cond_type"),
                    RETURN_ALL = 0x00,
                    RETURN_CLASS = 0x01,
                    RETURN_BDADDR = 0x02,
                ),
                "CONN_SETUP": Enum(ULInt8("cond_type"),
                    ALLOW_ALL = 0x00,
                    ALLOW_CLASS = 0x01,
                    ALLOW_BDADDR = 0x02,
                ),
            }
        ),
    ),
    FixedIf(lambda ctx: ctx.flt_type != "CLEAR_ALL",
        Switch("condition", lambda ctx: ctx.cond_type,
            {
                "RETURN_ALL": Pass,
                "RETURN_CLASS": Struct("cond_class",
                    Array(3, ULInt8("dev_class")),
                    Array(3, ULInt8("dev_class_mask")),
                ),
                "RETURN_BDADDR": Array(6, ULInt8("bdaddr")),
                "ALLOW_ALL": ULInt8("auto_accept_flag"),
                "ALLOW_CLASS": Struct("cond_class",
                    Array(3, ULInt8("dev_class")),
                    Array(3, ULInt8("dev_class_mask")),
                    ULInt8("auto_accept_flag"),
                ),
                "ALLOW_BDADDR": Struct("cond_bdaddr",
                    Array(6, ULInt8("bdaddr")),
                    ULInt8("auto_accept_flag"),
                ),
            }
        ),
    ),
)

set_event_flt_rp = Struct("set_event_flt_rp",
    ULInt8("status"),
)

delete_stored_link_key_cp = Struct("delete_stored_link_key_cp",
    Array(6, ULInt8("bdaddr")),
    ULInt8("delete_all"),
)

delete_stored_link_key_rp = Struct("delete_stored_link_key_rp",
    ULInt8("status"),
    ULInt16("num_keys"),
)

HCI_MAX_NAME_LENGTH = 248

change_local_name_cp = Struct("change_local_name_cp",
    String("name", HCI_MAX_NAME_LENGTH, padchar="\x00"),
)

change_local_name_rp = Struct("change_local_name_rp",
    ULInt8("status"),
)

read_local_name_rp = Struct("read_local_name_rp",
    ULInt8("status"),
    String("name", HCI_MAX_NAME_LENGTH, padchar="\x00"),
)

write_conn_accept_timeout_cp = Struct("write_conn_accept_timeout_cp",
    ULInt16("timeout"),
)

write_conn_accept_timeout_rp = Struct("write_conn_accept_timeout_rp",
    ULInt8("status"),
)

write_scan_enable_cp = Struct("write_scan_enable_cp",
    ULInt8("enable"),
)

write_scan_enable_rp = Struct("write_scan_enable_rp",
    ULInt8("status"),
)

read_class_of_dev_rp = Struct("read_class_of_dev_rp",
    ULInt8("status"),
    Array(3, ULInt8("dev_class")),
)

write_class_of_dev_cp = Struct("write_class_of_dev_cp",
    Array(3, ULInt8("dev_class")),
)

write_class_of_dev_rp = Struct("write_class_of_dev_rp",
    ULInt8("status"),
)

read_voice_setting_rp = Struct("read_voice_setting_rp",
    ULInt8("status"),
    ULInt16("voice_setting"),
)

write_inquiry_mode_cp = Struct("write_inquiry_mode_cp",
    ULInt8("mode"),
)

write_inquiry_mode_rp = Struct("write_inquiry_mode_rp",
    ULInt8("status"),
)

HCI_MAX_EIR_LENGTH = 240

write_ext_inquiry_response_cp = Struct("write_ext_inquiry_response_cp",
    ULInt8("fec"),
    Array(HCI_MAX_EIR_LENGTH, ULInt8("data")),
)

write_ext_inquiry_response_rp = Struct("write_ext_inquiry_response_rp",
    ULInt8("status"),
)

write_simple_pairing_mode_cp = Struct("write_simple_pairing_mode_cp",
    ULInt8("mode"),
)

write_simple_pairing_mode_rp = Struct("write_simple_pairing_mode_rp",
    ULInt8("status"),
)

read_inq_response_tx_power_level_rp = Struct("read_inq_response_tx_power_level_rp",
    ULInt8("status"),
    SLInt8("level"),
)

write_le_host_supported_cp = Struct("write_le_host_supported_cp",
    ULInt8("le"),
    ULInt8("simul"),
)

write_le_host_supported_rp = Struct("write_le_host_supported_rp",
    ULInt8("status"),
)

# Informational Parameters (OGF 0x04)

info_param_commands = Enum(BitField("ocf", 10),
    READ_LOCAL_VERSION = 0x0001,
    READ_LOCAL_COMMANDS = 0x0002,
    READ_LOCAL_FEATURES = 0x0003,
    READ_LOCAL_EXT_FEATURES = 0x0004,
    READ_BUFFER_SIZE = 0x0005,
    READ_BD_ADDR = 0x0009,
)

read_local_version_rp = Struct("read_local_version_rp",
    ULInt8("status"),
    ULInt8("hci_ver"),
    ULInt16("hci_rev"),
    ULInt8("lmp_ver"),
    ULInt16("manufacturer"),
    ULInt16("lmp_subver"),
)

read_local_commands_rp = Struct("read_local_commands_rp",
    ULInt8("status"),
    Array(64, ULInt8("commands")),
)

read_local_features_rp = Struct("read_local_features_rp",
    ULInt8("status"),
    Array(8, ULInt8("features")),
)

read_local_ext_features_cp = Struct("read_local_ext_features_cp",
    ULInt8("page_num"),
)

read_local_ext_features_rp = Struct("read_local_ext_features_rp",
    ULInt8("status"),
    ULInt8("page_num"),
    ULInt8("max_page_num"),
    Array(8, ULInt8("features")),
)

read_buffer_size_rp = Struct("read_buffer_size_rp",
    ULInt8("status"),
    ULInt16("acl_mtu"),
    ULInt8("sco_mtu"),
    ULInt16("acl_max_pkt"),
    ULInt16("sco_max_pkt"),
)

read_bd_addr_rp = Struct("read_bd_addr_rp",
    ULInt8("status"),
    Array(6, ULInt8("bdaddr")),
)

# LE Controller (OGF 0x08)

le_ctl_commands = Enum(BitField("ocf", 10),
    LE_SET_EVENT_MASK = 0x0001,
    LE_READ_BUFFER_SIZE = 0x0002,
    LE_READ_ADVERTISING_CHANNEL_TX_POWER = 0x0007,
    LE_SET_ADVERTISING_DATA = 0x0008,
    LE_SET_SCAN_PARAMETERS = 0x000b,
    LE_SET_SCAN_ENABLE = 0x000c,
)

le_set_event_mask_cp = Struct("le_set_event_mask_cp",
    Array(8, ULInt8("mask")),
)

le_set_event_mask_rp = Struct("le_set_event_mask_rp",
    ULInt8("status"),
)

le_read_buffer_size_rp = Struct("le_read_buffer_size_rp",
    ULInt8("status"),
    ULInt16("pkt_len"),
    ULInt8("max_pkt"),
)

le_read_advertising_channel_tx_power_rp = Struct("le_read_advertising_channel_tx_power_rp",
    ULInt8("status"),
    SLInt8("level"),
)

le_set_advertising_data_cp = Struct("le_set_advertising_data_cp",
    ULInt8("length"),
    Array(31, ULInt8("data")),
)

le_set_advertising_data_rp = Struct("le_set_advertising_data_rp",
    ULInt8("status"),
)

le_set_scan_parameters_cp = Struct("le_set_scan_parameters_cp",
    ULInt8("type"),
    ULInt16("interval"),
    ULInt16("window"),
    ULInt8("own_bdaddr_type"),
    ULInt8("filter"),
)

le_set_scan_parameters_rp = Struct("le_set_scan_parameters_rp",
    ULInt8("status"),
)

le_set_scan_enable_cp = Struct("le_set_scan_enable_cp",
    ULInt8("enable"),
    ULInt8("filter_dup"),
)

le_set_scan_enable_rp = Struct("le_set_scan_enable_rp",
    ULInt8("status"),
)

# Commands

Opcode = TunnelAdapter(
    SwapAdapter(Bytes("opcode", 2)),
    EmbeddedBitStruct(
        Enum(BitField("ogf", 6),
            LINK_CTL = 0x01,
            LINK_POLICY = 0x02,
            HOST_CTL = 0x03,
            INFO_PARAM = 0x04,
            STATUS_PARAM = 0x05,
            LE_CTL = 0x08,
        ),
        Switch("ocf", lambda ctx: ctx.ogf,
            {
                "LINK_CTL": link_ctl_commands,
                "HOST_CTL": host_ctl_commands,
                "INFO_PARAM": info_param_commands,
                "LE_CTL": le_ctl_commands,
            }
        ),
    )
)

command = Struct("command",
    Opcode,
    PLenAdapter(Sequence("params",
        ULInt8("plen"),
        Switch("pdata", lambda ctx: ctx._.opcode.ocf,
            {
                # Link Control (OGF 0x01)
                "INQUIRY": inquiry_cp,
                "INQUIRY_CANCEL": Pass,
                "CREATE_CONN": create_conn_cp,
                "DISCONNECT": disconnect_cp,
                "AUTH_REQUESTED": auth_requested_cp,
                "REMOTE_NAME_REQ": remote_name_req_cp,
                "READ_REMOTE_FEATURES": read_remote_features_cp,
                "READ_REMOTE_EXT_FEATURES": read_remote_ext_features_cp,
                # Controller & Baseband (OGF 0x03)
                "SET_EVENT_MASK": set_event_mask_cp,
                "RESET": Pass,
                "SET_EVENT_FLT": set_event_flt_cp,
                "DELETE_STORED_LINK_KEY": delete_stored_link_key_cp,
                "CHANGE_LOCAL_NAME": change_local_name_cp,
                "READ_LOCAL_NAME": Pass,
                "WRITE_CONN_ACCEPT_TIMEOUT": write_conn_accept_timeout_cp,
                "WRITE_SCAN_ENABLE": write_scan_enable_cp,
                "READ_CLASS_OF_DEV": Pass,
                "WRITE_CLASS_OF_DEV": write_class_of_dev_cp,
                "READ_VOICE_SETTING": Pass,
                "WRITE_INQUIRY_MODE": write_inquiry_mode_cp,
                "WRITE_EXT_INQUIRY_RESPONSE": write_ext_inquiry_response_cp,
                "WRITE_SIMPLE_PAIRING_MODE": write_simple_pairing_mode_cp,
                "READ_INQ_RESPONSE_TX_POWER_LEVEL": Pass,
                "WRITE_LE_HOST_SUPPORTED": write_le_host_supported_cp,
                # Informational Parameters (OGF 0x04)
                "READ_LOCAL_VERSION": Pass,
                "READ_LOCAL_COMMANDS": Pass,
                "READ_LOCAL_FEATURES": Pass,
                "READ_LOCAL_EXT_FEATURES": read_local_ext_features_cp,
                "READ_BUFFER_SIZE": Pass,
                "READ_BD_ADDR": Pass,
                # LE Controller (OGF 0x08)
                "LE_SET_EVENT_MASK": le_set_event_mask_cp,
                "LE_READ_BUFFER_SIZE": Pass,
                "LE_READ_ADVERTISING_CHANNEL_TX_POWER": Pass,
                "LE_SET_ADVERTISING_DATA": le_set_advertising_data_cp,
                "LE_SET_SCAN_PARAMETERS": le_set_scan_parameters_cp,
                "LE_SET_SCAN_ENABLE": le_set_scan_enable_cp,
            }
        ),
    )),
)

# Events

evt_inquiry_complete = Struct("evt_inquiry_complete",
    ULInt8("status"),
)

# FIXME: allow multiple responses
evt_inquiry_result = Struct("evt_inquiry_result",
    ULInt8("num_rsp"),
    Array(6, ULInt8("bdaddr")),
    ULInt8("pscan_rep_mode"),
    ULInt8("reserved1"),
    ULInt8("reserved2"),
    Array(3, ULInt8("dev_class")),
    ULInt16("clock_offset"),
)

evt_conn_complete = Struct("evt_conn_complete",
    ULInt8("status"),
    ULInt16("handle"),
    Array(6, ULInt8("bdaddr")),
    ULInt8("link_type"),
    ULInt8("encr_mode"),
)

evt_disconn_complete = Struct("evt_disconn_complete",
    ULInt8("status"),
    ULInt16("handle"),
    ULInt8("reason"),
)

evt_auth_complete = Struct("evt_auth_complete",
    ULInt8("status"),
    ULInt16("handle"),
)

evt_remote_name_req_complete = Struct("evt_remote_name_req_complete",
    ULInt8("status"),
    Array(6, ULInt8("bdaddr")),
    String("name", HCI_MAX_NAME_LENGTH, padchar="\x00"),
)

evt_read_remote_features_complete = Struct("evt_read_remote_features_complete",
    ULInt8("status"),
    ULInt16("handle"),
    Array(8, ULInt8("features")),
)

evt_cmd_complete = Struct("evt_cmd_complete",
    ULInt8("ncmd"),
    Opcode,
    FixedSwitch("rparams", lambda ctx: ctx.opcode.ocf,
        {
            # Link Control (OGF 0x01)
            "INQUIRY_CANCEL": inquiry_cancel_rp,
            # Controller & Baseband (OGF 0x03)
            "SET_EVENT_MASK": set_event_mask_rp,
            "RESET": reset_rp,
            "SET_EVENT_FLT": set_event_flt_rp,
            "DELETE_STORED_LINK_KEY": delete_stored_link_key_rp,
            "CHANGE_LOCAL_NAME": change_local_name_rp,
            "READ_LOCAL_NAME": read_local_name_rp,
            "WRITE_CONN_ACCEPT_TIMEOUT": write_conn_accept_timeout_rp,
            "WRITE_SCAN_ENABLE": write_scan_enable_rp,
            "READ_CLASS_OF_DEV": read_class_of_dev_rp,
            "WRITE_CLASS_OF_DEV": write_class_of_dev_rp,
            "READ_VOICE_SETTING": read_voice_setting_rp,
            "WRITE_INQUIRY_MODE": write_inquiry_mode_rp,
            "WRITE_EXT_INQUIRY_RESPONSE": write_ext_inquiry_response_rp,
            "WRITE_SIMPLE_PAIRING_MODE": write_simple_pairing_mode_rp,
            "READ_INQ_RESPONSE_TX_POWER_LEVEL": read_inq_response_tx_power_level_rp,
            "WRITE_LE_HOST_SUPPORTED": write_le_host_supported_rp,
            # Informational Parameters (OGF 0x04)
            "READ_LOCAL_VERSION": read_local_version_rp,
            "READ_LOCAL_COMMANDS": read_local_commands_rp,
            "READ_LOCAL_FEATURES": read_local_features_rp,
            "READ_LOCAL_EXT_FEATURES": read_local_ext_features_rp,
            "READ_BUFFER_SIZE": read_buffer_size_rp,
            "READ_BD_ADDR": read_bd_addr_rp,
            # LE Controller (OGF 0x08)
            "LE_SET_EVENT_MASK": le_set_event_mask_rp,
            "LE_READ_BUFFER_SIZE": le_read_buffer_size_rp,
            "LE_READ_ADVERTISING_CHANNEL_TX_POWER": le_read_advertising_channel_tx_power_rp,
            "LE_SET_ADVERTISING_DATA": le_set_advertising_data_rp,
            "LE_SET_SCAN_PARAMETERS": le_set_scan_parameters_rp,
            "LE_SET_SCAN_ENABLE": le_set_scan_enable_rp,
        }
    ),
)

evt_cmd_status = Struct("evt_cmd_status",
    ULInt8("status"),
    ULInt8("ncmd"),
    Opcode,
)

evt_num_comp_pkts = Struct("evt_num_comp_pkts",
    ULInt8("num_handles"),
    ULInt16("handle"),
    ULInt16("count"),
)

evt_read_remote_ext_features_complete = Struct("evt_read_remote_ext_features_complete",
    ULInt8("status"),
    ULInt16("handle"),
    ULInt8("page_num"),
    ULInt8("max_page_num"),
    Array(8, ULInt8("features")),
)

event = Struct("event",
    Enum(ULInt8("evt"),
        INQUIRY_COMPLETE = 0x01,
        INQUIRY_RESULT = 0x02,
        CONN_COMPLETE = 0x03,
        DISCONN_COMPLETE = 0x05,
        AUTH_COMPLETE = 0x06,
        REMOTE_NAME_REQ_COMPLETE = 0x07,
        READ_REMOTE_FEATURES_COMPLETE = 0x0b,
        CMD_COMPLETE = 0x0e,
        CMD_STATUS = 0x0f,
        NUM_COMP_PKTS = 0x13,
        READ_REMOTE_EXT_FEATURES_COMPLETE = 0x23,
    ),
    PLenAdapter(Sequence("params",
        ULInt8("plen"),
        Switch("pdata", lambda ctx: ctx._.evt,
            {
                "INQUIRY_COMPLETE": evt_inquiry_complete,
                "INQUIRY_RESULT": evt_inquiry_result,
                "CONN_COMPLETE": evt_conn_complete,
                "DISCONN_COMPLETE": evt_disconn_complete,
                "AUTH_COMPLETE": evt_auth_complete,
                "REMOTE_NAME_REQ_COMPLETE": evt_remote_name_req_complete,
                "READ_REMOTE_FEATURES_COMPLETE": evt_read_remote_features_complete,
                "CMD_COMPLETE": evt_cmd_complete,
                "CMD_STATUS": evt_cmd_status,
                "NUM_COMP_PKTS": evt_num_comp_pkts,
                "READ_REMOTE_EXT_FEATURES_COMPLETE": evt_read_remote_ext_features_complete,
            }
        ),
    )),
)
