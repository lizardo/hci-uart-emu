from nose.tools import raises

from bt_lib.hci.events import Event, CommandComplete

class FakeEvent(Event):
    evcode = 0xff
    params = [ ("xxx", 1) ]

@raises(ValueError)
def test_no_evcode():
    Event()

@raises(ValueError)
def test_invalid_payload():
    Event.from_payload("\x00")

@raises(ValueError)
def test_unknown_evcode():
    Event.from_payload("\x00\x00")

@raises(ValueError)
def test_plen_mismatch():
    Event.from_payload("\x01\x01")

@raises(ValueError)
def test_plen_mismatch2():
    Event.from_payload("\x01\x00")

def test_attribute():
    e = Event.from_payload("0e03010104".decode("hex"))
    assert e.Command_Opcode == 0x0401

@raises(AttributeError)
def test_attribute2():
    e = Event.from_payload("0e03010104".decode("hex"))
    e.xxx

@raises(ValueError)
def test_missing_parameter():
    CommandComplete(Num_HCI_Command_Packets=1)

def test_no_format():
    e = FakeEvent(xxx="\xff")
    assert e.xxx == "\xff"
