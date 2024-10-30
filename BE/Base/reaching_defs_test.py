#!/bin/env python3


import io
import unittest

from BE.Base import cfg
from BE.Base import eval
from BE.Base import ir
from BE.Base import liveness
from BE.Base import opcode_tab as o
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
    .reg S32 [x]
    .reg U32 [y] 
    .reg A32 [counter] 

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
        reaching_defs.FunPropagateConsts(fun)
        # reaching_defs.FunConstantFold(fun, True)
        reaching_defs.FunLoadStoreSimplify(fun)

        liveness.FunRemoveUselessInstructions(fun)
        print("\n".join(serialize.FunRenderToAsm(fun)))
        # all ld/st were re-written
        for ins in bbl.inss:
            self.assertIn(ins.opcode.name, {
                "ret", "add", "ld.mem", "st.mem", "ld.stk", "st.stk"})

    def testBaseRegPropagation2(self):
        code = io.StringIO(r"""
.fun foo NORMAL [] = []
    .reg S32 [x]
    .reg U32 [y]
    .reg A32 [a counter] 

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
        reaching_defs.FunPropagateConsts(fun)
        reaching_defs.FunLoadStoreSimplify(fun)
        liveness.FunRemoveUselessInstructions(fun)
        print("\n".join(serialize.FunRenderToAsm(fun)))
        # all ld/st were re-written
        for ins in bbl.inss:
            self.assertIn(ins.opcode.name, {
                "ret", "mul", "poparg",
                "ld", "ld", "st", "st",
            })


if __name__ == '__main__':
    unittest.main()
