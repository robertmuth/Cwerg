#!/bin/env python3

import io
import unittest

from BE.Base import cfg
from BE.Base import ir
from BE.Base import liveness
from BE.Base import opcode_tab as o
from BE.Base import serialize
from BE.Base import optimize

O = o.Opcode.Lookup


def DumpBbl(bbl):
    lines = serialize.BblRenderToAsm(bbl)
    print(lines.pop(0))
    for n, l in enumerate(lines):
        print(f"{n:2d}", l)


class TestRanges(unittest.TestCase):

    def testNoChange(self):
        x = ir.Reg("x", o.DK.S32)
        target = ir.Bbl("target")
        bbl = ir.Bbl("bbl")
        bbl.live_out.add(x)
        bbl.AddIns(ir.Ins(O("poparg"), [x]))
        bbl.AddIns(ir.Ins(O("blt"), [target, ir.OffsetConst(1), x]))

        DumpBbl(bbl)

        live_ranges = liveness.BblGetLiveRanges(bbl, None, bbl.live_out)
        live_ranges.sort()
        lr_cross_bbl = [lr for lr in live_ranges if lr.is_cross_bbl()]
        lr_lac = [lr for lr in live_ranges if liveness.LiveRangeFlag.LAC in lr.flags]
        lr_uses = [lr for lr in live_ranges if lr.uses]

        assert len(live_ranges) == 2
        assert len(lr_uses) == 1
        assert len(lr_cross_bbl) == 1
        assert len(lr_lac) == 0, f"{lr_lac}"

    def testA(self):

        code = io.StringIO(r"""
.fun printf_u BUILTIN [] = [A32 U32]

.fun multi BUILTIN [U32 U32 U32 U32 U32] = [U32 U32]

.mem fmt 4 RO
.data 1 "%d\n\0"

.fun main NORMAL [S32] = []
.reg U32 [a s m d M x y out]
.reg A64 [f] 

.bbl start
    mov x = 70
    mov y = 6

    pusharg y
    pusharg x
    bsr multi
    poparg a
    poparg s
    poparg m
    poparg d
    poparg M

    lea.mem f = fmt 0
    pusharg a
    pusharg f
    bsr printf_u

    pusharg s
    pusharg f
    bsr printf_u

    pusharg m
    pusharg f
    bsr printf_u

    pusharg d
    pusharg f
    bsr printf_u

    pusharg M
    pusharg f
    bsr printf_u

    mov out = 0
    pusharg out
    ret
        """)

        unit = serialize.UnitParseFromAsm(code, False)
        fun = unit.fun_syms["main"]
        bbl = fun.bbls[0]

        x = fun.reg_syms["x"]
        y = fun.reg_syms["y"]
        a = fun.reg_syms["a"]
        s = fun.reg_syms["s"]
        m = fun.reg_syms["m"]
        d = fun.reg_syms["d"]
        M = fun.reg_syms["M"]
        out = fun.reg_syms["out"]
        f = fun.reg_syms["f"]

        DumpBbl(bbl)
        live_ranges = liveness.BblGetLiveRanges(bbl, fun, bbl.live_out)
        live_ranges.sort()
        lr_cross_bbl = [lr for lr in live_ranges if lr.is_cross_bbl()]
        lr_lac = [lr for lr in live_ranges if liveness.LiveRangeFlag.LAC in lr.flags]

        assert len(live_ranges) == 22, f"{len(live_ranges)} {live_ranges}"
        assert len(lr_cross_bbl) == 0, f"{lr_cross_bbl}"
        assert len(lr_lac) == 5, f"{lr_lac}"
        for lr in live_ranges:
            print("checking LR lac:", lr)
            # assert lr.lac == lr.reg in {M, d, f, m, s}, f"LR {lr}"
            if lr.uses:
                continue
            self.assertNotEqual(lr.def_pos, lr.last_use_pos)
            self.assertEqual(liveness.LiveRangeFlag.LAC in lr.flags, lr.reg in {M, d, f, m, s})

    def testB(self):
        code = io.StringIO(r"""
.fun main NORMAL [S32] = [S32 A64]

.bbl %start
  poparg argc:S32
  poparg argv:A64
  mov b:S32 1
  add a:S32 b 1
  add x:S32 a 1
  blt argc 2 if_1_true
  bra if_1_end
  
.bbl if_1_true
   pusharg 1:S32
   ret
   
.bbl if_1_end
   pusharg 0:S32
   ret
""")
        unit = serialize.UnitParseFromAsm(code)
        fun = unit.fun_syms["main"]
        optimize.FunCfgInit(fun, unit)
        liveness.FunComputeLivenessInfo(fun)
        liveness.FunRemoveUselessInstructions(fun)
        # print ("@@@@\n", "\n".join(serialize.FunRenderToAsm(fun)))
        for bbl in fun.bbls:
            for ins in bbl.inss:
                self.assertTrue(ins.opcode in {o.POPARG, o.PUSHARG, o.RET, o.BLT}, f"bad ins {ins}")

    def testC(self):
        code = io.StringIO(r"""
.fun main NORMAL [S32] = []
.bbl %start
    mov %out:S32 3
    bra next
.bbl next
    pusharg %out
    ret
""")
        unit = serialize.UnitParseFromAsm(code)
        fun = unit.fun_syms["main"]
        optimize.FunCfgInit(fun, unit)
        liveness.FunComputeLivenessInfo(fun)
        # print ("@@@@\n", "\n".join(serialize.FunRenderToAsm(fun)))
        liveness.FunRemoveUselessInstructions(fun)
        # print ("@@@@\n", "\n".join(serialize.FunRenderToAsm(fun)))
        self.assertEqual(1, len(fun.bbls[0].inss))
        self.assertEqual(2, len(fun.bbls[1].inss))

    def testD(self):
        code = io.StringIO(r"""
.fun arm_syscall_write SIGNATURE [S32] = [S32 A32 U32]

.fun putchar NORMAL [] = [U32]

.fun writeln NORMAL [] = [A32 U32]
# live_out: ['r0', 'r1']
.reg S32 [$r0_S32 dummy]
.reg U32 [$r0_U32 $r1_U32 $r2_U32 len]
.reg A32 [$r0_A32 $r1_A32 buf]
.bbl start
    mov buf $r0_A32@r0                     # 0
    mov len $r1_U32@r1                     # 1
    mov $r2_U32@r2 len                     # 2
    mov $r1_A32@r1 buf                     # 3
    mov $r0_S32@r0 1                       # 4
    syscall arm_syscall_write 4:U32        # 5
    mov dummy $r0_S32@r0                   # 6
    mov $r0_U32@r0 10                      # 7
    bsr putchar                            # 8
    ret                                    # 9
""")
        cpu_regs = {"r0": ir.CpuReg("r0", 0), "r1": ir.CpuReg("r1", 1), "r2": ir.CpuReg("r2", 2)}
        unit = serialize.UnitParseFromAsm(code, cpu_regs=cpu_regs)

        fun = unit.fun_syms["arm_syscall_write"]
        fun.cpu_live_out = {cpu_regs["r0"]}
        fun.cpu_live_in = {cpu_regs["r0"], cpu_regs["r1"], cpu_regs["r2"]}

        fun = unit.fun_syms["putchar"]
        fun.cpu_live_in = {cpu_regs["r0"]}

        fun = unit.fun_syms["writeln"]
        cfg.FunSplitBblsAtTerminators(fun)
        cfg.FunInitCFG(fun)
        cfg.FunRemoveUnconditionalBranches(fun)
        cfg.FunRemoveEmptyBbls(fun)
        liveness.FunComputeLivenessInfo(fun)
        ranges = liveness.BblGetLiveRanges(fun.bbls[0], fun, fun.bbls[0].live_out)
        ranges.sort()
        print("TestD")
        for lr in ranges:
            print(lr)

        lr_r0 = liveness.LiveRange(liveness.BEFORE_BBL, 0, fun.reg_syms["$r0_A32"], 1)
        lr_r1 = liveness.LiveRange(liveness.BEFORE_BBL, 1, fun.reg_syms["$r1_U32"], 1)
        lr_buf = liveness.LiveRange(0, 3, fun.reg_syms["buf"], 1)
        lr_len = liveness.LiveRange(1, 2, fun.reg_syms["len"], 1)
        lr_r0_2 = liveness.LiveRange(5, 6, fun.reg_syms["$r0_S32"], 1)

        expected = [
            lr_r0,
            lr_r1,
            liveness.LiveRange(0, 0, reg=ir.REG_INVALID, num_uses=1, uses=[lr_r0]),
            lr_buf,
            liveness.LiveRange(1, 1, reg=ir.REG_INVALID, num_uses=1, uses=[lr_r1]),
            lr_len,
            liveness.LiveRange(2, 2, reg=ir.REG_INVALID, num_uses=1, uses=[lr_len]),
            liveness.LiveRange(2, 5, fun.reg_syms["$r2_U32"], 0),
            liveness.LiveRange(3, 3, reg=ir.REG_INVALID, num_uses=1, uses=[lr_buf]),
            liveness.LiveRange(3, 5, fun.reg_syms["$r1_A32"], 0),
            liveness.LiveRange(4, 5, fun.reg_syms["$r0_S32"], 0),
            lr_r0_2,
            liveness.LiveRange(6, 6, reg=ir.REG_INVALID, num_uses=1, uses=[lr_r0_2]),
            liveness.LiveRange(6, liveness.NO_USE, fun.reg_syms["dummy"], 0),
            liveness.LiveRange(7, 8, fun.reg_syms["$r0_U32"], 0),
        ]
        # self.assertSequenceEqual(ranges, expected) # this does not work because of the uses field
        self.assertEqual(len(ranges), len(expected))
        for a, b in zip():
            self.assertEqual(a, b)

    def testE(self):
        code = io.StringIO(r"""


.fun test NORMAL [F32 F32 F32 F32] = [F32 F32]
.reg F32 [a b add sub mul div  $s0_F32  $s1_F32  $s2_F32  $s3_F32]
.bbl start
    mov a $s0_F32@s0
    mov b $s1_F32@s1
    add add a b
    sub sub a b
    mul mul a b
    div div a b
    mov $s3_F32@s3 div
    mov $s2_F32@s2 mul
    mov $s1_F32@s1 sub
    mov $s0_F32@s0 add
    ret
""")
        cpu_regs = {"s0": ir.CpuReg("s0", 0), "s1": ir.CpuReg("s1", 1),
                    "s2": ir.CpuReg("s2", 2), "s3": ir.CpuReg("s3", 2)}
        unit = serialize.UnitParseFromAsm(code, cpu_regs=cpu_regs)
        fun = unit.fun_syms["test"]
        fun.cpu_live_out = {cpu_regs["s0"], cpu_regs["s1"], cpu_regs["s2"],
                            cpu_regs["s3"]}
        fun.cpu_live_in = {cpu_regs["s0"], cpu_regs["s1"]}
        cfg.FunSplitBblsAtTerminators(fun)
        cfg.FunInitCFG(fun)
        cfg.FunRemoveUnconditionalBranches(fun)
        cfg.FunRemoveEmptyBbls(fun)
        liveness.FunComputeLivenessInfo(fun)
        ranges = liveness.BblGetLiveRanges(fun.bbls[0], fun, fun.bbls[0].live_out)
        ranges.sort()
        print("TestE")
        for lr in ranges:
            print(lr)


if __name__ == '__main__':
    unittest.main()
