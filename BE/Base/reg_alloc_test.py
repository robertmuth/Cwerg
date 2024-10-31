#!/bin/env python3

import io
import unittest
import heapq
from typing import List, Dict

from BE.Base import ir
from BE.Base import liveness
from BE.Base import opcode_tab as o
from BE.Base import serialize
from BE.Base import reg_alloc

O = o.Opcode.Lookup

LAC = 16
GPR_NOT_LAC = 1
GPR_LAC = LAC + GPR_NOT_LAC
FLT_NOT_LAC = 2
FLT_LAC = LAC + FLT_NOT_LAC

A32_REGS = ([ir.CpuReg(f"r{i}", i, GPR_NOT_LAC) for i in range(6)] +
            [ir.CpuReg(f"r12", 12, GPR_NOT_LAC), ir.CpuReg(f"r14", 14, GPR_NOT_LAC)] +
            [ir.CpuReg(f"r{i}", i, GPR_LAC) for i in range(6, 12)] +
            [ir.CpuReg(f"s{i}", i, FLT_NOT_LAC) for i in range(16)] +
            [ir.CpuReg(f"s{i}", i, FLT_LAC) for i in range(16, 32)])


NAMES_TO_REG = { r.name : r for r in A32_REGS}


def _DumpBblWithLineNumbers(bbl):
    lines = serialize.BblRenderToAsm(bbl)
    print(lines.pop(0))
    for n, l in enumerate(lines):
        print(f"{n:2d}", l)


def extract_lsb(x):
    for i in range(1000000):
        mask = 1 << i
        if (x & mask) != 0:
            return x & ~mask, i
    assert False


class TestRegPool(reg_alloc.RegPool):
    def __init__(self, regs: List[ir.CpuReg]):
        self.available: Dict[int, List[ir.CpuReg]] = {
            GPR_NOT_LAC: [],
            GPR_LAC: [],
            FLT_NOT_LAC: [],
            FLT_LAC: [],
        }
        for cpu_reg in regs:
            heapq.heappush(self.available[cpu_reg.kind], cpu_reg)

    def get_cpu_reg_family(self, kind: o.DK) -> int:
        return FLT_NOT_LAC if kind.flavor() is o.DK_FLAVOR_R else GPR_NOT_LAC

    def backtrack_reset(self, cpu_reg: ir.CpuReg):
        assert cpu_reg != ir.CPU_REG_SPILL
        heapq.heappush(self.available[cpu_reg.kind], cpu_reg)

    def give_back_available_reg(self, cpu_reg: ir.CpuReg):
        return self.backtrack_reset(cpu_reg)

    def get_available_reg(self, lr: liveness.LiveRange) -> ir.CpuReg:
        kind = self.get_cpu_reg_family(lr.reg.kind)
        if liveness.LiveRangeFlag.LAC in lr.flags:
            kind += LAC
        available = self.available[kind]
        if not available:
            return ir.CPU_REG_SPILL

        return heapq.heappop(available)


def MakeGenericCpuRegs(num_gpr_not_lac, num_gpr_lac=0, num_flt_not_lac=0, num_flt_lac=0):
    return ([ir.CpuReg(f"gn{i}", i, GPR_NOT_LAC) for i in range(num_gpr_not_lac)] +
            [ir.CpuReg(f"gl{i}", i, GPR_LAC) for i in range(num_gpr_lac)] +
            [ir.CpuReg(f"sn{i}", i, FLT_NOT_LAC) for i in range(num_flt_not_lac)] +
            [ir.CpuReg(f"sl{i}", i, FLT_LAC) for i in range(num_flt_lac)])


class TestRanges(unittest.TestCase):

    def testSimple(self):

        code = io.StringIO(r"""
.fun main NORMAL [U32 U32 U32 U32] = [U32 U32 U32 U32]

.bbl start
    poparg w:U32
    poparg x:U32
    poparg y:U32
    poparg z:U32

    pusharg z
    pusharg y
    pusharg x
    pusharg w
    ret
        """)

        unit = serialize.UnitParseFromAsm(code, False)
        fun = unit.fun_syms["main"]
        bbl = fun.bbls[0]

        _DumpBblWithLineNumbers(bbl)

        live_ranges = liveness.BblGetLiveRanges(bbl, fun, set(), True)
        live_ranges.sort()

        pool = TestRegPool(MakeGenericCpuRegs(4))
        reg_alloc.RegisterAssignerLinearScan(live_ranges, pool)
        for n, lr in enumerate(live_ranges):
            # print (lr)
            if not lr.uses:
                assert lr.cpu_reg.no == n, f"unexpected reg {lr}"

        live_ranges = liveness.BblGetLiveRanges(bbl, fun, set(), True)
        live_ranges.sort()
        pool = TestRegPool(MakeGenericCpuRegs(3))
        reg_alloc.RegisterAssignerLinearScan(live_ranges, pool)
        for n, lr in enumerate(live_ranges):
            # print (lr)
            if not lr.uses:
                if n <= 2:
                    assert lr.cpu_reg.no == n
                else:
                    assert lr.cpu_reg == ir.CPU_REG_SPILL, f"unexpected reg {lr}"

    # def testSimple2(self):
    #     code = io.StringIO(r"""
    # LR BB -  0 PRE_ALLOC def:pos:U64@r11
    # LR BB - 16 PRE_ALLOC def:val:U32@r6
    # LR BB - AB PRE_ALLOC def:fd:S32@r10
    # LR  0 -  2 def:$5_aab:U64
    # LR  2 - AB PRE_ALLOC def:%U64_2:U64@r9
    # LR  3 - AB PRE_ALLOC def:pos:U64@r11
    # LR  4 -  6 def:$3_imm_U32:U32
    # LR  6 -  7 PRE_ALLOC def:$rdx_U32:U32@r7
    # LR  7 -  8 def:%U32_3:U32
    # LR  8 - 10 def:$6_aab:U32
    # LR 10 - 11 def:%U32_4:U32
    # LR 11 - 14 def:%S8_5:S8
    # LR 12 - 14 def:$1_base:A64
    # LR 13 - NU def:$9_st:S64
    # LR 15 - 17 def:$4_imm_U32:U32
    # LR 17 - NU PRE_ALLOC def:$rdx_U32:U32@r7
    # LR 18 - AB PRE_ALLOC def:%U32_8:U32@r8
    # LR 19 - AB PRE_ALLOC def:val:U32@r6
    #         """)
    #
    #     live_ranges = liveness.ParseLiveRanges(code, NAMES_TO_REG)
    #     live_ranges.sort()
    #
    #     pool = TestRegPool(MakeGenericCpuRegs(6))
    #     def log(lr, s):
    #         print (lr, s)
    #
    #     reg_alloc.RegisterAssignerLinearScan(live_ranges, pool, log)
    #     print ("@@@@@@ AFTER")
    #     for n, lr in enumerate(live_ranges):
    #         print (lr)


    def testBacktrack(self):
        # this is a good example for linear scan producing pretty bad assignments
        code = io.StringIO(r"""
.fun main NORMAL [U32 U32 U32 U32] = [U32 U32 U32 U32]

.bbl start
    poparg w:U32
    poparg x:U32
    poparg y:U32
    poparg z:U32

    mov a:U32 1
    mov b:U32 2
    mov c:U32 3
    mov d:U32 4

    cmpeq e:U32 a b c d

    pusharg z
    pusharg y
    pusharg x
    pusharg w
    ret
        """)

        unit = serialize.UnitParseFromAsm(code, False)
        fun = unit.fun_syms["main"]
        bbl = fun.bbls[0]

        _DumpBblWithLineNumbers(bbl)

        live_ranges = liveness.BblGetLiveRanges(bbl, fun, set(), True)
        live_ranges.sort()

        pool = TestRegPool(MakeGenericCpuRegs(4))
        reg_alloc.RegisterAssignerLinearScan(live_ranges, pool)
        for n, lr in enumerate(live_ranges):
            # print (lr)
            if not lr.uses:
                if n <= 3:
                    assert lr.cpu_reg.no == n
                else:
                    assert lr.cpu_reg is ir.CPU_REG_SPILL, f"unexpected reg {lr}"

        live_ranges = liveness.BblGetLiveRanges(bbl, fun, set(), True)
        live_ranges.sort()
        pool = TestRegPool(MakeGenericCpuRegs(8))
        reg_alloc.RegisterAssignerLinearScanFancy(live_ranges, pool, False)
        for n, lr in enumerate(live_ranges):
            # print (lr)
            assert lr.cpu_reg != ir.CPU_REG_SPILL, f"unexpected reg {lr}"


if __name__ == '__main__':
    unittest.main()
