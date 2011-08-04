from nose.tools import raises

from bt_lib.hci.commands import Command, Inquiry, Inquiry_Cancel

class FakeCommand(Command):
    ogf = 0x3f
    ocf = 0xffff
    rparams = [ ("xxx", 1) ]

@raises(ValueError)
def test_no_ogf_no_ocf():
    Command()

@raises(ValueError)
def test_invalid_payload():
    Command.from_payload("\x00")

@raises(ValueError)
def test_unknown_opcode():
    Command.from_payload("\x00\x00\x00")

@raises(ValueError)
def test_plen_mismatch():
    Command.from_payload("\x01\x04\x00")

@raises(ValueError)
def test_plen_mismatch2():
    Command.from_payload("\x01\x04\x01")

def test_attribute():
    c = Command.from_payload("010405338b9e0100".decode("hex"))
    assert c.LAP == "\x33\x8b\x9e"

@raises(AttributeError)
def test_attribute2():
    c = Command.from_payload("010405338b9e0100".decode("hex"))
    c.xxx

def test_inquiry():
    c = Inquiry(LAP="\x33\x8b\x9e", Inquiry_Length=1, Num_Responses=0)
    assert c.LAP == "\x33\x8b\x9e"
    assert c.Num_Responses == 0
    assert c.Inquiry_Length == 1
    assert c.payload.encode("hex") == "010405338b9e0100"

@raises(ValueError)
def test_inquiry_missing_parameter():
    Inquiry(LAP="\x33\x8b\x9e")

def test_inquiry_cancel():
    c = Inquiry_Cancel()
    e = c.command_complete(Status=0xff)
    assert e.Status == 0xff
    assert e.payload.encode("hex") == "0e04010204ff"

@raises(ValueError)
def test_cmd_complete_non_keyword():
    c = FakeCommand()
    c.command_complete("xxx")

@raises(ValueError)
def test_cmd_complete_missing_parameter():
    c = FakeCommand()
    c.command_complete()

def test_no_format():
    c = FakeCommand()
    e = c.command_complete(xxx="\xff")
    assert e.xxx == "\xff"
