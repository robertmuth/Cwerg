#!/usr/bin/python3

"""The file contains helpers for lowering code

Lowering refers to local rewrites that affect individual instruction
with the purpose of making code generation easier or improve
the performance of code.

Examples:
    * classical strength reductions, replaces complex instructions by
      simple ones (mul x = a 8  -> shl x = a 3)
    * emulate an instruction not directly supported by the target
      instruction set with sequence of equivalent instructions
"""

from typing import List, Optional

from Base import ir
from Base import opcode_tab as o

# nop means that the result of the operation is equal to src1
_OPC_NOP_IF_SRC2_IS_ZERO = {
    o.ADD, o.SUB, o.SHL, o.SHR, o.OR, o.XOR, o.LEA,
}  # ROTL

_OPC_NOP_IF_SRC1_IS_ZERO = {o.ADD, o.OR, o.XOR}

_OPC_NOP_IF_SRC2_IS_ONE = {o.MUL, o.DIV}

_OPC_NOP_IF_SRC1_IS_ONE = {o.MUL}


def _InsIsNop2(ins: ir.Ins) -> bool:
    opc = ins.opcode
    ops = ins.operands
    if len(ops) >= 2 and isinstance(ops[1], ir.Const):
        return (opc in _OPC_NOP_IF_SRC1_IS_ZERO and ops[1].IsZero() or
                opc in _OPC_NOP_IF_SRC1_IS_ONE and ops[1].IsOne())
    return False


def _InsIsNop1(ins: ir.Ins) -> bool:
    opc = ins.opcode
    ops = ins.operands
    if len(ops) >= 3 and isinstance(ops[2], ir.Const):
        return (opc in _OPC_NOP_IF_SRC2_IS_ZERO and ops[2].IsZero() or
                opc in _OPC_NOP_IF_SRC2_IS_ONE and ops[2].IsOne())

    return False


_OPC_ZERO_IF_OPS_SAME = {o.XOR, o.SUB}

_OPC_ZERO_IF_SRC1_IS_ZERO = {o.SHL, o.SHR, o.MUL}  # ROTL

_OPC_ZERO_IF_SRC2_IS_ZERO = {o.MUL}


def _InsIsZero(ins: ir.Ins):
    opc = ins.opcode
    ops = ins.operands
    return (opc in _OPC_ZERO_IF_OPS_SAME and ops[1] == ops[2] or
            opc in _OPC_ZERO_IF_SRC1_IS_ZERO and isinstance(ops[1], ir.Const)
            and ops[1].IsZero() or
            opc in _OPC_ZERO_IF_SRC2_IS_ZERO and isinstance(ops[2], ir.Const)
            and ops[2].IsZero())


def _InsStrengthReduction(
        ins: ir.Ins, _fun: ir.Fun) -> Optional[List[ir.Ins]]:
    """Miscellaneous standard strength reduction rewrites
    TODO
    """
    opc = ins.opcode
    ops = ins.operands
    if _InsIsNop1(ins):
        ops.pop(2)
        ins.operand_defs.pop(2)
        return [ins.Init(o.MOV, ops)]
    elif _InsIsNop2(ins):
        ops.pop(1)
        ins.operand_defs.pop(1)
        return [ins.Init(o.MOV, ops)]
    elif _InsIsZero(ins):
        ins.Init(o.MOV, [ops[0], ir.Const(ops[0].kind, 0)])
        return [ins]
    elif (opc is o.MUL and ops[0].IsIntReg() and isinstance(ops[2], ir.Const) and
          ops[2].IsIntPowerOfTwo()):
        shift = ops[2].IntBinaryLog()
        ins.Init(o.SHL, [ops[0], ops[1], ir.Const(ops[0].kind, shift)])
        return [ins]
    elif (opc is o.MUL and ops[0].IsIntReg() and isinstance(ops[1], ir.Const) and
          ops[1].IsIntPowerOfTwo()):
        shift = ops[1].IntBinaryLog()
        # TODO: orig_operand update
        ins.Init(o.SHL, [ops[0], ops[2], ir.Const(ops[0].kind, shift)])
        return [ins]
    # TODO: DIV for unsigned int

    return None


def FunStrengthReduction(fun: ir.Fun) -> int:
    return ir.FunGenericRewrite(fun, _InsStrengthReduction)


def _InsMoveElimination(ins: ir.Ins, _fun: ir.Fun) -> Optional[List[ir.Ins]]:
    if ins.opcode not in {o.MOV, o.CONV}:
        return None
    if ins.operands[0] == ins.operands[1]:
        return []
    return None


def FunMoveElimination(fun: ir.Fun) -> int:
    return ir.FunGenericRewrite(fun, _InsMoveElimination)


def InsEliminateImmediate(ins: ir.Ins, pos: int, fun: ir.Fun) -> ir.Ins:
    """Rewrite instruction with an immediate as load of the immediate
    followed by a pure register version of that instruction, e.g.

    mul z = a 666
    becomes
    mov scratch = 666
    mul z = a scratch

    This is useful if the target architecture does not support immediate
    for that instruction, or the immediate is too large.

    This optimization is run rather late and may already see machine
    registers like the sp.
    Hence we are careful to use and update ins.orig_operand
    """
    const = ins.operands[pos]
    assert isinstance(const, ir.Const)
    reg = fun.GetScratchReg(const.kind, "imm", True)
    ins.operands[pos] = reg
    return ir.Ins(o.MOV, [reg, const])


def _InsEliminateRem(
        ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    """Rewrites modulo instructions like so:
    z = a % b
    becomes
    z = a // b
    z = z * b
    z = a - z
    TODO: double check that this works out for corner-cases
    """
    ops = ins.operands
    out = []
    if ins.opcode is not o.REM:
        return None
    tmp_reg1 = fun.GetScratchReg(ops[0].kind, "elim_rem1", True)
    out.append(ir.Ins(o.DIV, [tmp_reg1, ops[1], ops[2]]))
    # NOTE: this implementation for floating mod may have precision issues.
    if ops[0].kind.flavor() is o.DK_FLAVOR_F:
        tmp_reg3 = fun.GetScratchReg(ops[0].kind, "elim_rem3", True)
        out.append(ir.Ins(o.TRUNC, [tmp_reg3, tmp_reg1]))
        tmp_reg1 = tmp_reg3
    tmp_reg2 = fun.GetScratchReg(ops[0].kind, "elim_rem2", True)
    out.append(ir.Ins(o.MUL, [tmp_reg2, tmp_reg1, ops[2]]))
    out.append(ir.Ins(o.SUB, [ops[0], ops[1], tmp_reg2]))
    return out


def FunEliminateRem(fun: ir.Fun) -> int:
    assert ir.FUN_FLAG.STACK_FINALIZED not in fun.flags
    return ir.FunGenericRewrite(fun, _InsEliminateRem)


def _InsEliminateStkLoadStoreWithRegOffset(
        ins: ir.Ins, fun: ir.Fun, base_kind: o.DK, offset_kind: o.DK) -> Optional[List[ir.Ins]]:
    """This rewrite is usually applied as prep step by some backends
     to get rid of Stk operands.
     It allows the register allocator to see the scratch register but
     it will obscure the fact that a memory access is a stack access.

     Note, a stack address already implies a `sp+offset` addressing mode and risk
     ISAs do no usually support  `sp+offset+reg` addressing mode.
    """
    opc = ins.opcode
    ops = ins.operands
    if opc is o.ST_STK and isinstance(ops[1], ir.Reg):
        scratch_reg = fun.GetScratchReg(base_kind, "base", False)
        lea = ir.Ins(o.LEA_STK, [scratch_reg, ops[0], ir.Const(offset_kind, 0)])
        ins.Init(o.ST, [scratch_reg, ops[1], ops[2]])
        return [lea, ins]
    elif opc is o.LD_STK and isinstance(ops[2], ir.Reg):
        scratch_reg = fun.GetScratchReg(base_kind, "base", False)
        lea = ir.Ins(o.LEA_STK, [scratch_reg, ops[1], ir.Const(offset_kind, 0)])
        ins.Init(o.LD, [ops[0], scratch_reg, ops[2]])
        return [lea, ins]
    elif opc is o.LEA_STK and isinstance(ops[2], ir.Reg):
        scratch_reg = fun.GetScratchReg(base_kind, "base", False)
        lea = ir.Ins(o.LEA_STK, [scratch_reg, ops[1], ir.Const(offset_kind, 0)])
        ins.Init(o.LEA, [ops[0], scratch_reg, ops[2]])
        return [lea, ins]
    else:
        return None


def FunEliminateStkLoadStoreWithRegOffset(fun: ir.Fun, base_kind: o.DK, offset_kind: o.DK) -> int:
    assert ir.FUN_FLAG.STACK_FINALIZED not in fun.flags
    return ir.FunGenericRewrite(
        fun, _InsEliminateStkLoadStoreWithRegOffset, base_kind=base_kind, offset_kind=offset_kind)


def _InsEliminateMemLoadStore(
        ins: ir.Ins, fun: ir.Fun, base_kind: o.DK, offset_kind: o.DK) -> Optional[List[ir.Ins]]:
    """This rewrite is usually applied as prep step by some backends
     to get rid of Mem operands.
     It allows the register allocator to see the scratch register but
     it will obscure the fact that a ld/st is from a static location.

     Note: this function may add local registers which does not affect liveness or use-deg chains
    """
    opc = ins.opcode
    ops = ins.operands
    if opc is o.ST_MEM:
        st_offset = ops[1]
        lea_offset = ir.Const(offset_kind, 0)
        if isinstance(st_offset, ir.Const):
            st_offset, lea_offset = lea_offset, st_offset
        scratch_reg = fun.GetScratchReg(base_kind, "base", False)
        lea = ir.Ins(o.LEA_MEM, [scratch_reg, ops[0], lea_offset])
        ins.Init(o.ST, [scratch_reg, st_offset, ops[2]])
        return [lea, ins]
    elif opc is o.LD_MEM:
        ld_offset = ops[2]
        lea_offset = ir.Const(offset_kind, 0)
        if isinstance(ld_offset, ir.Const):
            ld_offset, lea_offset = lea_offset, ld_offset
        scratch_reg = fun.GetScratchReg(base_kind, "base", False)
        # TODO: should the Zero Offset stay with the ld op?
        lea = ir.Ins(o.LEA_MEM, [scratch_reg, ops[1], lea_offset])
        ins.Init(o.LD, [ops[0], scratch_reg, ld_offset])
        return [lea, ins]
    else:
        return None


def FunEliminateMemLoadStore(fun: ir.Fun, base_kind: o.DK, offset_kind: o.DK) -> int:
    # assert ir.FUN_FLAG.STACK_FINALIZED not in fun.flags
    return ir.FunGenericRewrite(
        fun, _InsEliminateMemLoadStore, base_kind=base_kind, offset_kind=offset_kind)


def _InsEliminateImmediateStores(ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    """RISC architectures typically do not allow immediates to be stored directly

    TODO: maybe allow zero immediates
    """
    opc = ins.opcode
    ops = ins.operands
    if opc in {o.ST_MEM, o.ST, o.ST_STK} and isinstance(ops[2], ir.Const):
        scratch_reg = fun.GetScratchReg(ops[2].kind, "st_imm", False)
        mov = ir.Ins(o.MOV, [scratch_reg, ops[2]])
        ops[2] = scratch_reg
        return [mov, ins]
    else:
        return None


def FunEliminateImmediateStores(fun: ir.Fun) -> int:
    return ir.FunGenericRewrite(fun, _InsEliminateImmediateStores)


def FunRegWidthWidening(fun: ir.Fun, narrow_kind: o.DK, wide_kind: o.DK):
    """
    Change the type of all register (and constants) of type src_kind into dst_kind.
    Add compensation code where necessary.
    dst_kind must be wider than src_kind.

    This is useful for target architectures that do not support operations
    for all operand widths.

    Note, this also widens input and output regs. So this must run
      for all functions including prototypes

      TODO: double check if we are doing the right thing with o.CONV
      TODO: there are more subtle bugs. For example
              mul x:U8  = 43 * 47    (= 229)
              div y:u8  = x   13      (= 17)
            whereas:
              mul x:U16  = 43 * 47    (= 2021)
              div y:u16  = x   13      (= 155)

      Other problematic operations: rem, popcnt, ...
      """
    assert ir.FUN_FLAG.STACK_FINALIZED not in fun.flags
    fun.input_types = [wide_kind if x == narrow_kind else x for x in fun.input_types]
    fun.output_types = [wide_kind if x == narrow_kind else x for x in fun.output_types]

    assert narrow_kind.flavor() == wide_kind.flavor()
    assert narrow_kind.bitwidth() < wide_kind.bitwidth()
    narrow_regs = {reg for reg in fun.reg_syms.values()
                   if reg.kind == narrow_kind}

    for reg in narrow_regs:
        reg.kind = wide_kind

    count = 0
    for bbl in fun.bbls:
        inss = []

        for ins in bbl.inss:
            ops = ins.operands
            kind = ins.opcode.kind

            for n, reg in enumerate(ops):
                if n == 2 and kind is o.OPC_KIND.ST or n == 0 and kind is o.OPC_KIND.LD:
                    continue
                if isinstance(reg, ir.Const) and reg.kind is narrow_kind:
                    # if ins.opcode.constraints[n] == o.TC.OFFSET:
                    #    continue
                    ops[n] = ir.Const(wide_kind, reg.value)
            kind = ins.opcode.kind
            if kind is o.OPC_KIND.LD and ops[0] in narrow_regs:
                inss.append(ins)
                tmp_reg = fun.GetScratchReg(narrow_kind, "narrowed", True)
                inss.append(ir.Ins(o.CONV, [ops[0], tmp_reg]))
                ops[0] = tmp_reg
            elif (kind is o.OPC_KIND.ST and
                  isinstance(ops[2], ir.Reg) and ops[2] in narrow_regs):
                tmp_reg = fun.GetScratchReg(narrow_kind, "narrowed", True)
                inss.append(ir.Ins(o.CONV, [tmp_reg, ops[2]]))
                inss.append(ins)
                ops[2] = tmp_reg
            else:
                inss.append(ins)

        count += len(inss) - len(bbl.inss)
        bbl.inss = inss
    return count


def _InsMoveImmediatesToMemory(
        ins: ir.Ins, fun: ir.Fun, unit: ir.Unit, kind: o.DK) -> Optional[List[ir.Ins]]:
    inss = []
    for n, op in enumerate(ins.operands):
        if isinstance(op, ir.Const) and op.kind is kind:
            mem = unit.FindOrAddConstMem(op)
            tmp = fun.GetScratchReg(kind, "mem_const", True)
            # TODO: pass the offset kind as a parameter
            inss.append(ir.Ins(o.LD_MEM, [tmp, mem, ir.Const(o.DK.U32, 0)]))
            ins.operands[n] = tmp
    if inss:
        return inss + [ins]
    return None


def FunMoveImmediatesToMemory(fun: ir.Fun, unit: ir.Unit, kind: o.DK) -> int:
    return ir.FunGenericRewrite(fun, _InsMoveImmediatesToMemory, unit=unit, kind=kind)
