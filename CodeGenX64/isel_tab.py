#!/usr/bin/python3

"""Code Generation (Instruction Selection) for x86-64
"""

import collections
from typing import List, Dict, Any, Set, Optional
import enum

from Base import ir
from Base import opcode_tab as o
from CodeGenA64 import regs
import CpuX64.opcode_tab as x64
from Elf import enum_tab
from Util import cgen


@enum.unique
class C(enum.IntEnum):
    """Curbs/Constraints - describes constraints on the immediate values involved in patterns

    Used to determine if a pattern is a suitable match for a Cwerg IR instruction
    """
    INVALID = 0
    ZERO = 1
    ANY = 2
    REG = 3
    SP_REG = 4
    SIMM8 = 5
    SIMM16 = 6
    SIMM32 = 7
    SIMM64 = 8
    UIMM8 = 9
    UIMM16 = 10
    UIMM32 = 11
    UIMM64 = 12


class F(enum.Enum):
    """Fixed params"""
    NO_INDEX = 4
    NO_BASE = 5
    SP = 4
    RIP = 0


@enum.unique
class P(enum.Enum):
    """Placeholder/Parameter in X64 instruction template for stuff that needs to be derived
    for the Cwerg instructions"""
    invalid = 0
    reg01 = 1
    reg0 = 2
    reg1 = 3
    reg2 = 4
    reg3 = 5
    reg4 = 6
    #
    num0 = 10
    num1 = 11
    num2 = 12
    num3 = 13
    num4 = 14
    #
    spill01 = 20
    spill0 = 21
    spill1 = 22
    spill2 = 23
    stk1_offset2 = 24
    stk1 = 25
    #
    bbl0 = 30
    bbl2 = 31
    #
    mem1_num2_prel = 40
    fun1_prel = 41
    jtb1_prel = 42


_OP_TO_RELOC_KIND = {
    P.bbl0: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.bbl2: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.fun1_prel: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.mem1_num2_prel: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.jtb1_prel: enum_tab.RELOC_TYPE_X86_64.PC32,
}


def _HandleReloc(cpuins: x64.Ins, pos: int, ins: ir.Ins, op: P):
    assert not cpuins.has_reloc(), f"{cpuins.reloc_kind}"
    if op is P.bbl2:
        bbl = ins.operands[2]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, bbl.name)
    elif op is P.bbl0:
        bbl = ins.operands[0]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, bbl.name)
    elif op is P.fun1_prel:
        fun = ins.operands[1]
        assert isinstance(fun, ir.Fun), f"{ins} {fun}"
        assert fun.kind is not o.FUN_KIND.EXTERN, f"undefined fun: {fun.name}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], False, pos, fun.name)
    elif op is P.mem1_num2_prel:
        mem = ins.operands[1]
        assert isinstance(mem, ir.Mem), f"{ins} {mem}"
        assert mem.kind is not o.MEM_KIND.EXTERN, f"undefined fun: {mem.name}"
        num = ins.operands[2]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        assert cpuins.operands[pos] == 0
        cpuins.operands[pos] = num.value
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], False, pos, mem.name)
    elif op is P.jtb1_prel:
        jtb = ins.operands[1]
        assert isinstance(jtb, ir.Jtb), f"{ins} {jtb}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, jtb.name)
    else:
        assert False


def _ExtractTmplArgOp(ins: ir.Ins, arg: P, ctx: regs.EmitContext) -> int:
    ops = ins.operands
    if arg is P.reg01:
        assert ops[0] == ops[1]
        reg = ops[0]
        assert isinstance(reg, ir.Reg)
        assert reg.HasCpuReg()
        return reg.cpu_reg.no
    if arg is P.reg2:
        reg = ops[2]
        assert isinstance(reg, ir.Reg)
        assert reg.HasCpuReg()
        return reg.cpu_reg.no
    elif arg is P.num2:
        assert isinstance(ops[2], ir.Const)
        return ops[2].value
    else:
        assert False, f"could not extract op for {ins} {ins.operands} {arg}"


class InsTmpl:
    """Represents a template for an A32 instructions

    The idea is to "explode" each IR instruction into a list of these.

    The template args will be converted into A32 instruction operands by
    substituting data derived from the IR instruction operands as needed.

    args: a list of registers/constants/placeholders all values must be run through EncodeOperand
    """

    def __init__(self, opcode_name: str, args: List[Any]):
        opcode: x64.Opcode = x64.Opcode.OpcodesByName[opcode_name]
        assert args is not None
        assert len(args) == len(opcode.fields), f"num arg mismatch for {opcode_name}"
        for op in args:
            assert isinstance(op, (int, P, F)), (
                f"unknown op {op} for {opcode.name} {args}")
        self.opcode = opcode
        self.args: List[Any] = args

    def MakeInsFromTmpl(self, ins: Optional[ir.Ins], ctx: regs.EmitContext) -> x64.Ins:
        out = x64.Ins(self.opcode)
        for n, arg in enumerate(self.args):
            if type(arg) == int:
                val = arg
            elif isinstance(arg, F):
                val = arg.value
            elif isinstance(arg, P):
                val = _ExtractTmplArgOp(ins, arg, ctx)
            else:
                assert False, f"unknown param {repr(arg)}"

            assert isinstance(val, int), f"expected int {val}"
            out.operands.append(val)
            # note: this may alter the value we just appended
            if arg in _OP_TO_RELOC_KIND:
                _HandleReloc(out, n, ins, arg)
        return out


_ALLOWED_OPERAND_TYPES_REG = {
    o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64,
    o.DK.U32, o.DK.S32,
    o.DK.U8, o.DK.S8,
    o.DK.U16, o.DK.S16,
    o.DK.F32, o.DK.F64,
}


class Pattern:
    """
    See ../Docs/instruction_selection.md
    """
    # groups all the patterns for a given opcode number together
    Table: Dict[int, List["Pattern"]] = collections.defaultdict(list)

    def __init__(self, opcode: o.Opcode, type_constraints: List[o.DK],
                 op_curbs: List[C], emit: List[InsTmpl]):
        # the template, usually contains ArmIns except for the nop1 pattern
        self.emit = emit
        # how to fill the template params
        assert len(type_constraints) == len(
            opcode.operand_kinds), f"{opcode.name} {type_constraints} {opcode.operand_kinds}"
        assert len(type_constraints) == len(op_curbs)
        self.type_constraints = type_constraints
        self.opcode = opcode
        self.op_curbs = op_curbs
        for type_constr, op_constr, kind in zip(type_constraints, op_curbs,
                                                opcode.operand_kinds):
            if kind is o.OP_KIND.REG:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert op_constr in {C.REG, C.SP_REG}
            elif kind is o.OP_KIND.CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert op_constr in {}
            elif kind is o.OP_KIND.REG_OR_CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
            else:
                assert type_constr is o.DK.INVALID
                assert op_constr is C.INVALID, f"bad pattern for {opcode}"

        # we put all the patterns for given IR opcode into the same bucket
        Pattern.Table[opcode.no].append(self)

    def MatchesTypeCurbs(self, ins: ir.Ins) -> bool:
        for type_constr, op in zip(self.type_constraints, ins.operands):
            if type_constr is o.DK.INVALID:
                continue
            if isinstance(op, ir.Reg):
                if op.kind != type_constr:
                    return False
            elif isinstance(op, ir.Const):
                if op.kind != type_constr:
                    return False
            else:
                assert False
        return True

    def MatchesOpCurbs(self, ins: ir.Ins) -> bool:
        """
        """
        for pos, (op_curb, op) in enumerate(zip(self.op_curbs, ins.operands)):
            if op_curb is C.INVALID:
                assert not isinstance(ir.Const, ir.Reg)
            elif op_curb is C.REG:
                if not isinstance(op, ir.Reg):
                    return False
                if isinstance(op.cpu_reg, ir.StackSlot):
                    return False
            elif op_curb is C.SP_REG:
                if not isinstance(op, ir.Reg):
                    return False
                if not isinstance(op.cpu_reg, ir.StackSlot):
                    return False
            elif op_curb in {C.SIMM8, C.SIMM16,
                             C.SIMM32, C.SIMM64}:
                assert isinstance(op, ir.Const)
                if op_curb is C.SIMM8:
                    if (1 << 7) <= op.value or op.value < -(1 << 7):
                        return False
                elif op_curb is C.SIMM16:
                    if (1 << 15) <= op.value or op.value < -(1 << 15):
                        return False
                elif op_curb is C.SIMM32:
                    if (1 << 31) <= op.value or op.value < -(1 << 31):
                        return False
                elif op_curb is C.SIMM64:
                    if (1 << 63) <= op.value or op.value < -(1 << 63):
                        return False
        return True

    def __str__(self):
        types = [x.name for x in self.type_constraints]
        curbs = [x.name for x in self.op_curbs]
        return f"PATTERN {self.opcode.name} [{' '.join(types)}] [{' '.join(curbs)}]"


_KIND_TO_IMM = {
    o.DK.U8: C.UIMM8,
    o.DK.S8: C.SIMM8,
    o.DK.U16: C.UIMM16,
    o.DK.S16: C.SIMM16,
    o.DK.U32: C.UIMM32,
    o.DK.S32: C.SIMM32,
    o.DK.U64: C.SIMM32,  # not a typo
    o.DK.S64: C.SIMM32,  # not a typo
}

OPCODES_REQUIRING_SPECIAL_HANDLING = {
    o.RET
}


def InitAluInt():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        bw = kind1.bitwidth()
        iw = 32 if bw == 64 else bw
        for opc, x64_opc in [(o.AND, "and"),
                             (o.XOR, "xor"),
                             (o.ADD, "add"),
                             (o.OR, "or"),
                             (o.SUB, "sub")]:
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, C.REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mr",
                             [P.reg01, P.reg2])])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, C.REG],
                    [InsTmpl(f"{x64_opc}_{bw}_mbis32_r",
                             [F.SP, F.NO_INDEX,
                              P.spill01, 0, P.reg2])])
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mbis32",
                             [P.reg01, F.SP, F.NO_INDEX,
                              P.spill2, 0])])
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, _KIND_TO_IMM[kind1]],
                    [InsTmpl(f"{x64_opc}_{bw}_mr_imm{iw}", [P.reg01, P.num2])])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, _KIND_TO_IMM[kind1]],
                    [InsTmpl(f"{x64_opc}_{bw}_mbis32_imm{iw}",
                             [F.SP, F.NO_INDEX,
                              P.spill01, 0, P.num2])])


def InitAluFlt():
    for kind1, suffix in [(o.DK.F32, "s"), (o.DK.F64, "d")]:
        for opc, x64_opc in [(o.ADD, "adds"),
                             (o.SUB, "subs"),
                             (o.MUL, "muls"),
                             (o.DIV, "divs")]:
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, C.REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mx",
                             [P.reg01, P.reg2])])
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mbis32",
                             [P.reg01, F.SP, F.NO_INDEX,
                              P.spill2, 0])])

        for opc, x64_opc in [(o.SQRT, "sqrts")]:
            Pattern(opc, [kind1] * 2,
                    [C.REG, C.REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mx", [P.reg0, P.reg1])])
            Pattern(opc, [kind1] * 2,
                    [C.REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mbis32",
                             [P.reg0, F.SP, F.NO_INDEX, P.spill1, 0])])


# http://unixwiz.net/techtips/x86-jumps.html
def _GetJmp(dk: o.DK, opc):
    if opc is o.BEQ:
        return "je"
    elif opc is o.BNE:
        return "jne"
    elif opc is o.BLT:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jl"
        else:
            return "jb"
    elif opc is o.BLE:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jle"
        else:
            return "jbe"


def _GetJmpSwp(dk: o.DK, opc):
    if opc is o.BEQ:
        return "je"
    elif opc is o.BNE:
        return "jne"
    elif opc is o.BLT:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jg"
        else:
            return "ja"
    elif opc is o.BLE:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jge"
        else:
            return "jae"


def InitCondBraInt():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        bw = kind1.bitwidth()
        iw = 32 if bw == 64 else bw
        for opc in [o.BEQ, o.BNE, o.BLT, o.BLE]:
            x64_jmp = _GetJmp(kind1, opc)
            x64_jmp_swp = _GetJmpSwp(kind1, opc)
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, C.REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_r_mr", [P.reg0, P.reg1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.SP_REG, C.REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mbis32_r",
                             [F.SP, F.NO_INDEX, P.spill0, 0, P.reg2]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, C.SP_REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_r_mbis32",
                             [P.reg0, F.SP, F.NO_INDEX, P.spill1, 0]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            #
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, _KIND_TO_IMM[kind1], C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mr_imm{iw}", [P.reg0, P.num1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.SP_REG, _KIND_TO_IMM[kind1], C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mbis32_imm{iw}",
                             [F.SP, F.NO_INDEX, P.spill0, 0, P.num1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            #
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [_KIND_TO_IMM[kind1], C.REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mr_imm{iw}", [P.reg1, P.num0]),
                     InsTmpl(f"{x64_jmp_swp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [_KIND_TO_IMM[kind1], C.SP_REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mbis32_imm{iw}",
                             [F.SP, F.NO_INDEX, P.spill1, 0, P.num0]),
                     InsTmpl(f"{x64_jmp_swp}_32", [P.bbl2])])


_EXTEND_TO_64bit = {
    o.DK.U8: "movzx_64_8_r_mr",
    o.DK.S8: "movsx_64_8_r_mr",
    o.DK.U16: "movzx_64_16_r_mr",
    o.DK.S16: "movsx_64_16_r_mr",
    o.DK.U32: "mov_32_mr_r",
    o.DK.S32: "movsxd_64_r_mr",
}


def ExtendRegTo64Bit(reg, dk: o.DK) -> List[InsTmpl]:
    x64_opc = _EXTEND_TO_64bit.get(dk)
    if not x64_opc:
        return []
    return [InsTmpl(x64_opc, [reg, reg])]


def InitLea():
    Pattern(o.LEA_FUN, [o.DK.C64, o.DK.INVALID],
            [C.REG, C.INVALID],
            [InsTmpl("lea_64_r_mpc32", [P.reg0, F.RIP, P.fun1_prel])])

    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        Pattern(o.LEA_MEM, [o.DK.A64, o.DK.INVALID, kind1],
                [C.REG, C.INVALID, C.SIMM64],
                [InsTmpl("lea_64_r_mpc32", [P.reg0, F.RIP, P.mem1_num2_prel])])

        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.REG, C.INVALID, C.SIMM32],
                [InsTmpl("lea_64_r_mbis32", [P.reg0, F.SP, F.NO_INDEX, 0,
                                             P.stk1_offset2])])
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.REG, C.INVALID, C.REG],
                ExtendRegTo64Bit(P.reg2, kind1) +
                [InsTmpl("lea_64_r_mbis32", [P.reg0, P.reg2, F.SP, 0, P.stk1])])

        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.REG, C.REG, C.SIMM32],
                [InsTmpl("lea_64_r_mbis32", [P.reg0, P.reg1, F.NO_INDEX, 0,
                                             P.num2])])


def FindMatchingPattern(ins: ir.Ins) -> Optional[Pattern]:
    """Returns the best pattern matching `ins` or None

    This can only be called AFTER the stack has been finalized
    """
    patterns = Pattern.Table[ins.opcode.no]
    # print(f"@@ {ins} {ins.operands}")
    for p in patterns:
        # print(f"@@ trying pattern {p}")
        if p.MatchesTypeCurbs(ins) and p.MatchesOpCurbs(ins):
            return p
    # assert False, f"Could not find a matching patterns for {ins}. tried:\n{patterns}"
    return None


InitAluInt()
InitAluFlt()
InitCondBraInt()
InitLea()


def _DumpCodeSelTable():
    count = 0
    for i in range(256):
        patterns = Pattern.Table.get(i)
        if patterns is None: continue
        count += len(patterns)
        opcode = o.Opcode.TableByNo[i]
        print(f"{opcode.name} [{' '.join([k.name for k in opcode.operand_kinds])}] patters={len(patterns)}")
        for pat in patterns:
            type_constraints = [x.name if x != o.DK.INVALID else '*' for x in pat.type_constraints]
            op_constraints = [x.name if x else '*' for x in pat.op_curbs]

            print(f"  [{' '.join(type_constraints)}]  [{' '.join(op_constraints)}]")
            for tmpl in pat.emit:
                ops = [str(x) if isinstance(x, int) else x.name for x in tmpl.args]
                print(f"    {tmpl.opcode.name} [{' '.join(ops)}]")
        print()
    print(f"Total patterns {count}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        assert False
        if sys.argv[1] == "documentation":
            pass
        elif sys.argv[1] == "gen_h":
            cgen.ReplaceContent(_EmitCodeH, sys.stdin, sys.stdout)
        elif sys.argv[1] == "gen_c":
            cgen.ReplaceContent(_EmitCodeC, sys.stdin, sys.stdout)

    else:
        _DumpCodeSelTable()
