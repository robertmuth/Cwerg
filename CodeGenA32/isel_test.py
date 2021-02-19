#!/usr/bin/python3

import unittest

from CodeGenA32 import isel_tab
from Base import ir
from Base import opcode_tab as o


class TestRanges(unittest.TestCase):
    def testMov(self):
        for kind in [o.DK.S32, o.DK.U32, o.DK.A32, o.DK.F32]:
            ins = ir.Ins(o.MOV, [ir.Reg(name="0", kind=kind), ir.Reg(name="1", kind=kind)])
            assert isel_tab.FindMatchingPattern(ins) is not None


if __name__ == '__main__':
    unittest.main()
