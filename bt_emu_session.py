#!/usr/bin/python
import os
import struct
import dbus
import dbus.mainloop.glib
from gi.repository import GLib, GObject

local_name = "vmprecise-0"

# Common packets
packets = {
    # < HCI Command: Reset (0x03|0x0003) plen 0
    "\x01\x03\x0C\x00": "\x04\x0E\x04\x01\x03\x0C\x00",
    # < HCI Command: Read Local Supported Features (0x04|0x0003) plen 0
    "\x01\x03\x10\x00": "\x04\x0E\x0C\x01\x03\x10\x00\xA4\x08\x00\xC0\x58\x1E\x7B\x83",
    # < HCI Command: Read Local Version Information (0x04|0x0001) plen 0
    "\x01\x01\x10\x00": "\x04\x0E\x0C\x01\x01\x10\x00\x06\x00\x00\x06\x3F\x00\x00\x00",
    # < HCI Command: Read BD ADDR (0x04|0x0009) plen 0
    "\x01\x09\x10\x00": "\x04\x0E\x0A\x01\x09\x10\x00\xAF\xF0\xAF\xF0\xAF\xF0",
    # < HCI Command: Read Buffer Size (0x04|0x0005) plen 0
    "\x01\x05\x10\x00": "\x04\x0E\x0B\x01\x05\x10\x00\xC0\x00\x00\x01\x00\x00\x00",
    # < HCI Command: Read Class of Device (0x03|0x0023) plen 0
    "\x01\x23\x0C\x00": "\x04\x0E\x07\x01\x23\x0C\x00\x00\x00\x00",
    # < HCI Command: Read Local Name (0x03|0x0014) plen 0
    "\x01\x14\x0C\x00": "\x04\x0E\xFC\x01\x14\x0C\x00\x66\x6F\x61\x66" + "\x00" * 244,
    # < HCI Command: Read Voice Setting (0x03|0x0025) plen 0
    "\x01\x25\x0C\x00": "\x04\x0E\x06\x01\x25\x0C\x00\x00\x00",
    # < HCI Command: Set Event Filter (0x03|0x0005) plen 1
    "\x01\x05\x0C\x01\x00": "\x04\x0E\x04\x01\x05\x0C\x00",
    # < HCI Command: Write Connection Accept Timeout (0x03|0x0016) plen 2
    "\x01\x16\x0C\x02\x00\x7D": "\x04\x0E\x04\x01\x16\x0C\x00",
    # < HCI Command: Delete Stored Link Key (0x03|0x0012) plen 7
    "\x01\x12\x0C\x07\x00\x00\x00\x00\x00\x00\x01": "\x04\x0E\x06\x01\x12\x0C\x00\x00\x00",
    # < HCI Command: Set Event Mask (0x03|0x0001) plen 8
    "\x01\x01\x0C\x08\xFF\xFF\xFB\xFF\x07\xF8\xBF\x3D": "\x04\x0E\x04\x01\x01\x0C\x00",
    # < HCI Command: Read Local Supported Commands (0x04|0x0002) plen 0
    "\x01\x02\x10\x00": "\x04\x0E\x44\x01\x02\x10" + "\x00" * 65,
    # < HCI Command: Write Inquiry Mode (0x03|0x0045) plen 1
    "\x01\x45\x0C\x01\x02": "\x04\x0E\x04\x01\x45\x0C\x00",
    # < HCI Command: Read Inquiry Response TX Power Level (0x03|0x0058) plen 0
    "\x01\x58\x0C\x00": "\x04\x0E\x05\x01\x58\x0C\x00\x00",
    # < HCI Command: Read Local Extended Features (0x04|0x0004) plen 1
    "\x01\x04\x10\x01\x01": "\x04\x0E\x0E\x01\x04\x10\x00\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00",
}

# For latest kernel
packets.update({
    # < HCI Command: LE Read Buffer Size (0x08|0x0002) plen 0
    "\x01\x02\x20\x00": "\x04\x0E\x07\x01\x02\x20\x00\xC0\x00\x01",
    # < HCI Command: LE Read Advertising Channel TX Power (0x08|0x0007) plen 0
    "\x01\x07\x20\x00": "\x04\x0E\x05\x01\x07\x20\x00\x00",
    # < HCI Command: LE Set Event Mask (0x08|0x0001) plen 8
    "\x01\x01\x20\x08\x1F\x00\x00\x00\x00\x00\x00\x00": "\x04\x0E\x04\x01\x01\x20\x00",
    # < HCI Command: Write Extended Inquiry Response (0x03|0x0052) plen 241
    "\x01\x52\x0C\xF1" + "\x00" * 241: "\x04\x0E\x04\x01\x52\x0C\x00",
    # < HCI Command: LE Set Advertising Data (0x08|0x0008) plen 32
    "\x01\x08\x20\x20\x0C\x02\x01\x08\x02\x0A\x00\x05\x09\x66\x6F\x61\x66" + "\x00" * 19 : "\x04\x0E\x04\x01\x08\x20\x00",
})

# Uncategorized / Ubuntu precise
packets.update({
    # < HCI Command: Write Simple Pairing Mode (0x03|0x0056) plen 1
    "\x01\x56\x0C\x01\x01": "\x04\x0E\x04\x01\x56\x0C\x00",
    # < HCI Command: Write LE Host Supported (0x03|0x006d) plen 2
    "\x01\x6D\x0C\x02\x00\x00": "\x04\x0E\x04\x01\x6D\x0C\x00",
    # < HCI Command: Read Stored Link Key (0x03|0x000d) plen 7
    "\x01\x0D\x0C\x07\x00\x00\x00\x00\x00\x00\x01": "\x04\x0E\x08\x01\x0D\x0C\x00\x00\x00\x00\x00",
    # < HCI Command: Write Local Name (0x03|0x0013) plen 248
    "\x01\x13\x0C\xF8" + local_name + "\x00" * (248 - len(local_name)): "\x04\x0E\x04\x01\x13\x0C\x00",
    # < HCI Command: Write Default Link Policy Settings (0x02|0x000f) plen 2
    "\x01\x0F\x08\x02\x05\x00": "\x04\x0E\x04\x01\x0F\x08\x00",
    # < HCI Command: Write Class of Device (0x03|0x0024) plen 3
    "\x01\x24\x0C\x03\x00\x01\x6E": "\x04\x0E\x04\x01\x24\x0C\x00", 
    # < HCI Command: Write Scan Enable (0x03|0x001a) plen 1
    "\x01\x1A\x0C\x01\x02": "\x04\x0E\x04\x01\x1A\x0C\x00",
    # < HCI Command: Read Simple Pairing Mode (0x03|0x0055) plen 0
    "\x01\x55\x0C\x00": "\x04\x0E\x05\x01\x55\x0C\x00\x00",
    # < HCI Command: Write Scan Enable (0x03|0x001a) plen 1
    "\x01\x19\x0C\x00": "\x04\x0E\x05\x01\x19\x0C\x00\x02",
    # < HCI Command: Write Page Timeout (0x03|0x0018) plen 2
    "\x01\x18\x0C\x02\x00\x20": "\x04\x0E\x04\x01\x18\x0C\x00",
    # < HCI Command: Inquiry (0x01|0x0001) plen 5
    "\x01\x01\x04\x05\x33\x8B\x9E\x08\x00": ("\x04\x0F\x04\x00\x01\x01\x04",
        "\x04\x02\x0F\x01\x34\x12\x34\x12\x34\x12\x00\x00\x00\x00\x00\x00\x00\x00",
        "\x04\x01\x01\x00"),
    # < HCI Command: Inquiry Cancel (0x01|0x0002) plen 0
    "\x01\x02\x04\x00": "\x04\x0E\x04\x01\x02\x04\x00",
    # < HCI Command: Remote Name Request (0x01|0x0019) plen 10
    "\x01\x19\x04\x0A\x34\x12\x34\x12\x34\x12\x02\x00\x00\x00": ("\x04\x0F\x04\x00\x01\x19\x04",
        "\x04\x07\xFF\x00\x34\x12\x34\x12\x34\x12\x74\x65\x73\x74\x31\x32\x33\x34" + "\x00" * 240),
    # < HCI Command: Create Connection (0x01|0x0005) plen 13
    "\x01\x05\x04\x0D\x34\x12\x34\x12\x34\x12\x18\x00\x00\x00\x00\x80\x01": ("\x04\x0F\x04\x00\x01\x05\x04",
        "\x04\x03\x0B\x00\x01\x00\x34\x12\x34\x12\x34\x12\x01\x00"),
    # < HCI Command: Read Remote Supported Features (0x01|0x001b) plen 2
    "\x01\x1B\x04\x02\x01\x00": ("\x04\x0F\x04\x00\x01\x1B\x04",
        "\x04\x0B\x0B\x00\x01\x00\xA4\x08\x00\xC0\x58\x1E\x7B\x83"),
    # < HCI Command: Read Remote Extended Features (0x01|0x001c) plen 3
    "\x01\x1C\x04\x03\x01\x00\x01": ("\x04\x0F\x04\x00\x01\x1C\x04",
        "\x04\x23\x0D\x00\x01\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00"),
})

def read_data(fd, cb_condition):
    assert cb_condition == GLib.IO_IN
    buf = os.read(fd, 4096)
    transport = struct.unpack_from("B", buf, 0)[0]
    if transport == 0x01:
        # HCI Command packet
        plen = struct.unpack_from("B", buf, 3)[0]
        assert len(buf) >= plen + 4
        print("CMD: %s" % buf.encode("hex").upper())
        if packets.get(buf):
            if isinstance(packets[buf], tuple):
                for p in packets[buf]:
                    os.write(fd, p)
            else:
                os.write(fd, packets[buf])
        else:
            print("Unsupported HCI command")
            loop.quit()
            return False
    else:
        print("Unsupported transport: %#x" % transport)
        loop.quit()
        return False

    return True

def create_device_reply(device):
    print("New device (%s)" % device)

def create_device_error(error):
    print("Creating device failed: %s" % error)

def device_found(address, properties):
    assert address == "12:34:12:34:12:34"
    adapter.StopDiscovery()
    adapter.CreateDevice(address,
            reply_handler=create_device_reply,
            error_handler=create_device_error)

def adapter_added(adapter_path):
    global adapter
    adapter = dbus.Interface(bus.get_object("org.bluez", adapter_path), "org.bluez.Adapter")
    adapter.connect_to_signal("DeviceFound", device_found)
    adapter.StartDiscovery()

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.bluez.Manager")
    manager.connect_to_signal("AdapterAdded", adapter_added)
    loop = GObject.MainLoop()
    fd = os.open("/dev/vhci", os.O_RDWR | os.O_NONBLOCK)
    source = GLib.io_add_watch(fd, GLib.IO_IN, read_data)
    loop.run()
