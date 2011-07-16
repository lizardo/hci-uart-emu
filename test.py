import unittest

from bt_lib.hci.commands import Command, Inquiry

class CommandTestCase(unittest.TestCase):
    def testCommand(self):
        self.assertRaises(ValueError, Command)
        self.assertRaises(ValueError, Command.from_payload, "\x00")
        self.assertRaises(ValueError, Command.from_payload, "\x00\x00\x00")
        self.assertRaises(ValueError, Command.from_payload, "\x01\x04\x00")
        self.assertRaises(ValueError, Command.from_payload, "\x01\x04\x01")

    def testInquiry(self):
        c = Inquiry(LAP="\x33\x8b\x9e", Inquiry_Length=1, Num_Responses=0)
        self.assertEquals(c.LAP, "\x33\x8b\x9e")
        self.assertEquals(c.Inquiry_Length, 1)
        self.assertEquals(c.Num_Responses, 0)
        self.assertRaises(AttributeError, getattr, c, "xxx")
        self.assertEquals(c.payload.encode("hex"), "010405338b9e0100")
        self.assertRaises(ValueError, Inquiry, "xxx")
        self.assertRaises(ValueError, Inquiry, LAP="\x33\x8b\x9e")

if __name__ == "__main__":
    unittest.main()
