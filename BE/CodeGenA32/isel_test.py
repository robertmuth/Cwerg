#!/bin/env python3

import unittest

from BE.CodeGenA32 import isel_tab
from BE.Base import ir
from IR import opcode_tab as o


class TestRanges(unittest.TestCase):
    def testMov(self):
        for kind in [o.DK.S32, o.DK.U32, o.DK.A32, o.DK.R32]:
            ins = ir.Ins(o.MOV, [ir.Reg(name="0", kind=kind), ir.Reg(name="1", kind=kind)])
            assert isel_tab.FindMatchingPattern(ins) is not None


if __name__ == '__main__':
    unittest.main()
