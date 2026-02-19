#!/bin/env python3


import io
import unittest

from BE.Base import cfg
from BE.Base import eval
from BE.Base import ir
from BE.Base import liveness
from IR import opcode_tab as o
from BE.Base import reaching_defs
from BE.Base import serialize


class TestConversion(unittest.TestCase):

    def testA(self):
        self.assertEqual(1000, eval.ConvertIntValue(
            o.DK.U32, ir.Const(o.DK.U16, 1000)).value)
        self.assertEqual(100, eval.ConvertIntValue(
            o.DK.U32, ir.Const(o.DK.U8, 100)).value)

        self.assertEqual(-1000, eval.ConvertIntValue(
            o.DK.S32, ir.Const(o.DK.S16, -1000)).value)
        self.assertEqual(-100, eval.ConvertIntValue(
            o.DK.S32, ir.Const(o.DK.S8, -100)).value)
        self.assertEqual(-127, eval.ConvertIntValue(
            o.DK.S32, ir.Const(o.DK.S8, -127)).value)

        self.assertEqual(24, eval.ConvertIntValue(
            o.DK.S8, ir.Const(o.DK.S32, -1000)).value)
        self.assertEqual(-20, eval.ConvertIntValue(
            o.DK.S8, ir.Const(o.DK.S32, -1300)).value)

        self.assertEqual(0xfffffc18, eval.ConvertIntValue(
            o.DK.U32, ir.Const(o.DK.S16, -1000)).value)
        self.assertEqual(0xfc18, eval.ConvertIntValue(
            o.DK.U16, ir.Const(o.DK.S16, -1000)).value)

        self.assertEqual(0xfffffc18, eval.ConvertIntValue(
            o.DK.U32, ir.Const(o.DK.S32, -1000)).value)
        self.assertEqual(-1000, eval.ConvertIntValue(
            o.DK.S32, ir.Const(o.DK.U32, 0xfffffc18)).value)

    def testBaseRegPropagation1(self):
        code = io.StringIO(r"""
 .mem COUNTER 4 RW
 .data 4 [0]

.fun foo NORMAL [] = []
    .stk array 4 4000
    .reg S32 x
    .reg U32 y
    .reg A32 counter

.bbl start
    lea.mem counter = COUNTER 0
    ld x = counter 0
    add x = x 1
    st counter 0 = x

    lea.mem counter = COUNTER 100
    ld x = counter 100
    add x = x 1
    st counter 300 = x

    mov y 666
    lea.mem counter = COUNTER 0
    ld x = counter y
    add x = x 1
    st counter y = x

    lea.stk counter = array 0
    ld x = counter 0
    add x = x 1
    st counter 0 = x

    lea.stk counter = array 100
    ld x = counter 100
    add x = x 1
    st counter 300 = x

    mov y 666
    lea.stk counter = array 0
    ld x = counter y
    add x = x 1
    st counter y = x

    ret
         """)

        unit = serialize.UnitParseFromAsm(code, False)
        fun = unit.fun_syms["foo"]
        bbl = fun.bbls[0]

        cfg.FunInitCFG(fun)
        liveness.FunComputeLivenessInfo(fun)
        reaching_defs.FunComputeReachingDefs(fun)
        reaching_defs.FunPropagateRegsAndConsts(fun)
        # reaching_defs.FunConstantFold(fun, True)
        reaching_defs.FunLoadStoreSimplify(fun)

        liveness.FunRemoveUselessInstructions(fun)
        # print("\n".join(serialize.FunRenderToAsm(fun)))
        # all ld/st were re-written
        for ins in bbl.inss:
            self.assertIn(ins.opcode.name, {
                "ret", "add", "ld.mem", "st.mem", "ld.stk", "st.stk"})

    def testBaseRegPropagation2(self):
        code = io.StringIO(r"""
.fun foo NORMAL [] = []
    .reg S32 x
    .reg U32 y
    .reg A32 a
    .reg A32 counter

.bbl start
    poparg counter
    poparg y

    lea a counter 666
    ld x = a 0
    mul x = x 777
    st a 334 = x

    lea a counter y
    ld x = a 0
    mul x = x 777
    st a 0 = x

    lea a counter y
    ld x = a 0
    mul x = x 777
    st a 0 = x

    mov a counter
    ld x = a 0
    mul x = x 777
    st a 334 = x

    ret
         """)

        unit = serialize.UnitParseFromAsm(code, False)
        fun = unit.fun_syms["foo"]
        bbl = fun.bbls[0]

        cfg.FunInitCFG(fun)
        liveness.FunComputeLivenessInfo(fun)
        reaching_defs.FunComputeReachingDefs(fun)
        reaching_defs.FunPropagateRegsAndConsts(fun)
        reaching_defs.FunLoadStoreSimplify(fun)
        liveness.FunRemoveUselessInstructions(fun)
        # print("\n".join(serialize.FunRenderToAsm(fun)))
        # all ld/st were re-written
        for ins in bbl.inss:
            self.assertIn(ins.opcode.name, {
                "ret", "mul", "poparg",
                "ld", "ld", "st", "st",
            })


    def testBaseRegPropagation3(self):
        code = io.StringIO(r"""
.mem parse_real/ParseError 8 RO
    .data 16 "\x00"


.fun parse_real/parse_r64_hex_helper NORMAL [] = [A64 U8 U64 A64]
.bbl entry  #  edge_out[br_join  entry_1]
    poparg s:A64
    poparg negative:U8
    poparg offset:U64
    poparg large_result:A64
    mov i:U64 offset
    ld n:U64 s 8
    mov length:U64 n
    mov c:U8 0
    blt offset n br_join
.bbl entry_1  #  #edge_in=1
    lea.mem lhsaddr:A64 = parse_real/ParseError 0
    ld copy:U64 lhsaddr 0
    st large_result 0 copy
    ld copy lhsaddr 8
    st large_result 8 copy
    ret
.bbl br_join  #  edge_out[end_of_input]  #edge_in=1
    ld pointer:A64 s 0
    lea new_base:A64 pointer offset
    ld c new_base 0
    mov deref:U8 c
    add i offset 1
    mov expr2:U64 i
    mov mant:U64 0
    mov exp_adjustments:S32 0
    mov exp:S32 0
.bbl end_of_input  #  edge_out[_]  #edge_in=1
    mov digits%1:U8 15
.bbl _  #  edge_out[_.1  br_join.1]  #edge_in=2
    beq c 48 br_join.1
.bbl br_join.1  #  edge_out[br_join.2  end_of_input.end]  #edge_in=1
    blt i n br_join.2
.bbl br_join.2  #  edge_out[_]  #edge_in=1
    ld pointer.1:A64 s 0
    lea new_base.1:A64 pointer.1 i
    ld c new_base.1 0
    mov deref.1:U8 c
    add i i 1
    mov expr2.1:U64 i
.bbl _.1  #  edge_out[_.1_1  br_failed_and]  #edge_in=2
    mov inl_arg:U8 c
    blt c 48 br_failed_and
.bbl _.1_1  #  edge_out[br_failed_and  br_failed_or]  #edge_in=1
    ble inl_arg 57 br_failed_or
.bbl br_failed_and  #  edge_out[br_f  br_failed_and_1]  #edge_in=2
    blt inl_arg 97 br_f
.bbl br_failed_and_1  #  edge_out[br_f  br_failed_or]  #edge_in=1
    blt 102:U8 inl_arg br_f
.bbl br_failed_or  #  edge_out[end_expr]  #edge_in=2
    mov expr:U64 1
.bbl br_f  #  edge_out[end_expr]  #edge_in=2
    ret
    """)

        unit = serialize.UnitParseFromAsm(code, False)
        fun = unit.fun_syms["parse_real/parse_r64_hex_helper"]
        bbl = fun.bbls[0]

        cfg.FunInitCFG(fun)
        liveness.FunComputeLivenessInfo(fun)
        reaching_defs.FunComputeReachingDefs(fun)
        reaching_defs.FunPropagateRegsAndConsts(fun)
        reaching_defs.FunLoadStoreSimplify(fun)
        liveness.FunRemoveUselessInstructions(fun)
        print("\n".join(serialize.FunRenderToAsm(fun)))


if __name__ == '__main__':
    unittest.main()
