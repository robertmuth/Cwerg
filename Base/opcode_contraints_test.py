#!/usr/bin/python3

"""
mov.r reg_s32 reg_u32
"""

import unittest

from Base import ir
from Base import sanity
from Base import opcode_tab as o

reg_s64 = ir.Reg("reg_s64", o.DK.S64)
reg_s32 = ir.Reg("reg_s32", o.DK.S32)
reg_s18 = ir.Reg("reg_s16", o.DK.S16)
reg_s8 = ir.Reg("reg_s8", o.DK.S8)

reg_u64 = ir.Reg("reg_u64", o.DK.U64)
reg_u32 = ir.Reg("reg_u32", o.DK.U32)
reg_u16 = ir.Reg("reg_u16", o.DK.U16)
reg_u8 = ir.Reg("reg_u8", o.DK.U8)

reg_a64 = ir.Reg("reg_a64", o.DK.A64)
reg_a32 = ir.Reg("reg_a32", o.DK.A32)

reg_c64 = ir.Reg("reg_c64", o.DK.C64)
reg_c32 = ir.Reg("reg_c32", o.DK.C32)


class TestRegState(unittest.TestCase):

    def testMov(self):
        mov = o.Opcode.Lookup("mov")
        ins = ir.Ins(mov, [reg_u32, reg_u32])
        sanity.InsCheckConstraints(ins)

        with self.assertRaises(sanity.ParseError):
            ins = ir.Ins(mov, [reg_s32, reg_u32])
            sanity.InsCheckConstraints(ins)

        with self.assertRaises(sanity.ParseError):
            ins = ir.Ins(mov, [reg_s32, reg_s8])
            sanity.InsCheckConstraints(ins)

    def testAdd(self):
        add = o.Opcode.Lookup("add")
        ins = ir.Ins(add, [reg_u32, reg_u32, reg_u32])
        sanity.InsCheckConstraints(ins)

        with self.assertRaises(sanity.ParseError):
            ins = ir.Ins(add, [reg_u32, reg_s32, reg_u32])
            sanity.InsCheckConstraints(ins)

        with self.assertRaises(sanity.ParseError):
            ins = ir.Ins(add, [reg_a32, reg_a32, reg_s32])
            sanity.InsCheckConstraints(ins)

        with self.assertRaises(sanity.ParseError):
            ins = ir.Ins(add, [reg_u32, reg_u32, reg_a32])
            sanity.InsCheckConstraints(ins)

        with self.assertRaises(sanity.ParseError):
            ins = ir.Ins(add, [reg_u32, reg_u32, reg_s32])
            sanity.InsCheckConstraints(ins)

        with self.assertRaises(sanity.ParseError):
            ins = ir.Ins(add, [reg_u32, reg_u32, reg_u16])
            sanity.InsCheckConstraints(ins)

    def testAdd2(self):
        ld = o.Opcode.Lookup("ld")
        ins = ir.Ins(ld, [reg_u32, reg_a32, reg_u32])
        sanity.InsCheckConstraints(ins)

        ins = ir.Ins(ld, [reg_u32, reg_a32, reg_u16])
        sanity.InsCheckConstraints(ins)

        ins = ir.Ins(ld, [reg_u32, reg_a32, reg_s32])
        sanity.InsCheckConstraints(ins)

        with self.assertRaises(sanity.ParseError):
            ins = ir.Ins(ld, [reg_u32, reg_u32, reg_u32])
            sanity.InsCheckConstraints(ins)

        with self.assertRaises(sanity.ParseError):
            ins = ir.Ins(ld, [reg_u32, reg_a32, reg_a32])
            sanity.InsCheckConstraints(ins)


if __name__ == '__main__':
    unittest.main()
