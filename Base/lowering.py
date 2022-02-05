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

from Base import cfg
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


def InsEliminateImmediateViaMov(ins: ir.Ins, pos: int, fun: ir.Fun) -> ir.Ins:
    """Rewrite instruction with an immediate as mov of the immediate

    mul z = a 666
    becomes
    mov scratch = 666
    mul z = a scratch

    This is useful if the target architecture does not support immediate
    for that instruction, or the immediate is too large.

    This optimization is run rather late and may already see machine registers.
    Ideally, the generated mov instruction hould be iselectable by the target architecture or
    else another pass may be necessary.
    """
    # support of PUSHARG would require additional work because they need to stay consecutive
    assert ins.opcode is not o.PUSHARG
    const = ins.operands[pos]
    assert isinstance(const, ir.Const)
    reg = fun.GetScratchReg(const.kind, "imm", True)
    ins.operands[pos] = reg
    return ir.Ins(o.MOV, [reg, const])


def InsEliminateImmediateViaMem(ins: ir.Ins, pos: int, fun: ir.Fun, unit: ir.Unit, addr_kind: o.DK,
                                offset_kind: o.DK) -> List[ir.Ins]:
    """Rewrite instruction with an immediate as load of the immediate


    This is useful if the target architecture does not support immediate
    for that instruction, or the immediate is too large.

    This optimization is run rather late and may already see machine registers.
    """
    # support of PUSHARG would require additional work because they need to stay consecutive
    assert ins.opcode is not o.PUSHARG
    const = ins.operands[pos]
    mem = unit.FindOrAddConstMem(const)
    tmp_addr = fun.GetScratchReg(addr_kind, "mem_const_addr", True)
    lea_ins = ir.Ins(o.LEA_MEM, [tmp_addr, mem, ir.Const(offset_kind, 0)])
    tmp = fun.GetScratchReg(const.kind, "mem_const", True)
    ld_ins = ir.Ins(o.LD, [tmp, tmp_addr, ir.Const(offset_kind, 0)])
    ins.operands[pos] = tmp
    return [lea_ins, ld_ins]


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

    if ins.opcode is not o.REM:
        return None
    ops = ins.operands
    out = []
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


def InsEliminateCmp(ins: ir.Ins, bbl: ir.Bbl, fun: ir.Fun):
    """Rewrites cmpXX a, b, c, x, y instructions like so:
    canonicalization ensures that a != c
    mov z b
    bXX skip, x, y
      mov z c
    .bbl skip
      mov a z

    TODO: This is very coarse
    """
    assert ins.opcode.kind is o.OPC_KIND.CMP
    bbl_skip = cfg.BblSplitBeforeFixEdges(
        bbl, ins, fun, cfg.NewDerivedBblName(bbl.name, "_split", fun))

    bbl_prev = cfg.BblSplitBeforeFixEdges(
        bbl_skip, ins, fun, cfg.NewDerivedBblName(bbl.name, "_split", fun))

    assert not bbl_skip.inss
    assert bbl_prev.inss[-1] is ins
    assert bbl_prev.edge_out == [bbl_skip]
    assert bbl_skip.edge_in == [bbl_prev]
    assert bbl_skip.edge_out == [bbl]
    assert bbl.edge_in == [bbl_skip]

    reg = fun.GetScratchReg(ins.operands[0].kind, "cmp", False)

    del bbl_prev.inss[-1]
    ops = ins.operands
    bbl_prev.inss.append(ir.Ins(o.MOV, [reg, ops[1]]))
    bbl_prev.inss.append(ir.Ins(o.BEQ if ins.opcode == o.CMPEQ else o.BLT, [ops[3], ops[4], bbl]))
    bbl_skip.inss.append(ir.Ins(o.MOV, [reg, ops[2]]))
    bbl.inss.insert(0, ir.Ins(o.MOV, [ops[0], reg]))
    bbl_prev.edge_out.append(bbl)
    bbl.edge_in.append(bbl_prev)


def FunEliminateCmp(fun: ir.Fun) -> int:
    for bbl in fun.bbls[:]:  # not we are updating the list while iterating over it
        for ins in bbl.inss[:]:
            if ins.opcode.kind is o.OPC_KIND.CMP:
                InsEliminateCmp(ins, bbl, fun)


def _InsEliminateCopySign(ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    """Rewrites copysign instructions like so:
    z = copysign a  b
    aa = int(a) & 0x7f...f
    bb = int(b) & 0x80...0
    z = flt(aa | bb)
    """

    if ins.opcode is not o.COPYSIGN:
        return None
    ops = ins.operands
    out = []
    if ops[0].kind == o.DK.F32:
        kind = o.DK.U32
        sign = 1 << 31
    else:
        kind = o.DK.U64
        sign = 1 << 63
    mask = sign - 1

    tmp_src1 = fun.GetScratchReg(kind, "elim_copysign1", False)
    out.append(ir.Ins(o.BITCAST, [tmp_src1, ops[1]]))
    out.append(ir.Ins(o.AND, [tmp_src1, tmp_src1, ir.Const(kind, mask)]))
    #
    tmp_src2 = fun.GetScratchReg(kind, "elim_copysign2", False)
    out.append(ir.Ins(o.BITCAST, [tmp_src2, ops[2]]))
    out.append(ir.Ins(o.AND, [tmp_src2, tmp_src2, ir.Const(kind, sign)]))
    #
    out.append(ir.Ins(o.OR, [tmp_src1, tmp_src1, tmp_src2]))
    out.append(ir.Ins(o.BITCAST, [ops[0], tmp_src1]))
    return out


def FunEliminateCopySign(fun: ir.Fun) -> int:
    assert ir.FUN_FLAG.STACK_FINALIZED not in fun.flags
    return ir.FunGenericRewrite(fun, _InsEliminateCopySign)


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
        # TODO: maybe reverse the order so that we can tell that ops[0] holds a stack
        # location
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

     Note: this function may add local registers which does not affect liveness or use-def chains

     st.mem ->  lea.mem + st   # st offset will be zero or register which should be iselectable
     ld.mem -> lea.mem + ld    # ld offset will be zero or register which should be iselectable
     lea.mem (with reg offset) -> lea.mem (zero offset) + lea
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
    elif opc is o.LEA_MEM and isinstance(ops[2], ir.Reg):
        scratch_reg = fun.GetScratchReg(base_kind, "base", False)
        # TODO: maybe reverse the order so that we can tell that ops[0] holds a mem location
        lea = ir.Ins(o.LEA_MEM, [scratch_reg, ops[1], ir.Const(offset_kind, 0)])
        ins.Init(o.LEA, [ops[0], scratch_reg, ops[2]])
        return [lea, ins]
    else:
        return None


def FunEliminateMemLoadStore(fun: ir.Fun, base_kind: o.DK, offset_kind: o.DK) -> int:
    # assert ir.FUN_FLAG.STACK_FINALIZED not in fun.flags
    return ir.FunGenericRewrite(
        fun, _InsEliminateMemLoadStore, base_kind=base_kind, offset_kind=offset_kind)


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

      The invariant we are maintaining is this one:
      if reg a gets widened into reg b with bitwidth(a) = w then
      the lower w bits of reg b will always contain the same data as reg a would have.
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
            changed = False
            for n, reg in enumerate(ops):
                if isinstance(reg, ir.Const) and reg.kind is narrow_kind:
                    if kind is o.OPC_KIND.ST and n == 2:
                        continue
                    ops[n] = ir.Const(wide_kind, reg.value)
                    changed = True
                if isinstance(reg, ir.Reg) and reg in narrow_regs:
                    changed = True
            if not changed:
                inss.append(ins)
                continue
            kind = ins.opcode.kind
            if ins.opcode is o.SHL or ins.opcode is o.SHR:
                # deal with the shift amount which is subject to an implicit modulo "bitwidth -1"
                # by changing the width of the reg - we lose this information
                tmp_reg = fun.GetScratchReg(wide_kind, "tricky", False)
                inss.append(ir.Ins(o.AND, [tmp_reg, ops[2], ir.Const(wide_kind, narrow_kind.bitwidth() - 1)]))
                ops[2] = tmp_reg
                if ins.opcode is o.SHR and isinstance(ops[1], ir.Reg):
                    # for SHR we also need to make sure the new high order bits are correct
                    tmp_reg = fun.GetScratchReg(narrow_kind, "narrowed", True)
                    inss.append(ir.Ins(o.CONV, [tmp_reg, ops[1]]))
                    # the implicit understanding is that this will become nop or a move and not modify the
                    # high-order bit we just set in the previous instruction
                    inss.append(ir.Ins(o.CONV, [ops[1], tmp_reg]))
                inss.append(ins)
            elif ins.opcode is o.CNTLZ:
                inss.append(ins)
                excess = wide_kind.bitwidth() - narrow_kind.bitwidth()
                inss.append(ir.Ins(o.SUB, [ops[0], ops[0], ir.Const(wide_kind, excess)]))
            elif ins.opcode is o.CNTTZ:
                inss.append(ins)
                inss.append(ir.Ins(o.CMPLT, [ops[0], ops[0],
                                             ir.Const(wide_kind, narrow_kind.bitwidth()),
                                             ops[0], ir.Const(wide_kind, narrow_kind.bitwidth())]))
            elif kind is o.OPC_KIND.LD and ops[0] in narrow_regs:
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
            elif ins.opcode is o.CONV:
                tmp_reg = fun.GetScratchReg(narrow_kind, "narrowed", True)
                inss.append(ir.Ins(o.CONV, [tmp_reg, ops[1]]))
                inss.append(ir.Ins(o.CONV, [ops[0], tmp_reg]))
            else:
                inss.append(ins)

        count += len(inss) - len(bbl.inss)
        bbl.inss = inss
    return count


def _InsLimitShiftAmounts(
        ins: ir.Ins, fun: ir.Fun, width: int) -> Optional[List[ir.Ins]]:
    """This rewrite is usually applied as prep step by some backends
     to get rid of Stk operands.
     It allows the register allocator to see the scratch register but
     it will obscure the fact that a memory access is a stack access.

     Note, a stack address already implies a `sp+offset` addressing mode and risk
     ISAs do no usually support  `sp+offset+reg` addressing mode.
    """
    opc = ins.opcode
    ops = ins.operands
    if (opc is not o.SHL and opc is not o.SHR) or ops[0].kind.bitwidth() != width:
        return None
    amount = ops[2]
    if isinstance(amount, ir.Const):
        if 0 <= amount.value < width:
            return None
        else:
            ops[2] = ir.Const(amount.kind, amount.value % width)
            return ins
    else:
        tmp = fun.GetScratchReg(amount.kind, "shift", False)
        mask = ir.Ins(o.AND, [tmp, amount, ir.Const(amount.kind, width - 1)])
        ins.Init(opc, [ops[0], ops[1], tmp])
        return [mask, ins]


def FunLimitShiftAmounts(fun: ir.Fun, width: int):
    return ir.FunGenericRewrite(
        fun, _InsLimitShiftAmounts, width=width)


class PushPopInterface:
    """Used with FunPopargConversion and FunPushargConversion"""

    @classmethod
    def GetCpuRegsForInSignature(cls, kinds: List[o.DK]) -> List[ir.CpuReg]:
        assert False, "To be implemented by subclass"

    @classmethod
    def GetCpuRegsForOutSignature(cls, kinds: List[o.DK]) -> List[ir.CpuReg]:
        assert False, "To be implemented by subclass"


def _InsPopargConversion(ins: ir.Ins, fun: ir.Fun, iface: PushPopInterface,
                         params: List[ir.CpuReg]) -> Optional[List[ir.Ins]]:
    """
    This pass converts `poparg reg` -> `mov reg = arg_reg`

    it must used in a forward pass over the Bbl and will update `param`
    for use with the next Ins in the BBl. The initial value of `param`
    reflects the Fun's arguments.

    """
    if ins.opcode is o.POPARG:
        cpu_reg = params.pop(0)
        dst = ins.operands[0]
        # assert dst.kind == cpu_reg.kind
        reg = fun.FindOrAddCpuReg(cpu_reg, dst.kind)
        return [ir.Ins(o.MOV, [dst, reg])]

    assert not params, f"params {params} should be empty at ins {ins.opcode} {ins.operands}  in {fun.name}"

    if ins.opcode.is_call():
        callee: ir.Fun = cfg.InsCallee(ins)
        assert isinstance(callee, ir.Fun)
        params += iface.GetCpuRegsForOutSignature(callee.output_types)
    return None


def FunPopargConversion(fun: ir.Fun, iface: PushPopInterface):
    return ir.FunGenericRewrite(fun, _InsPopargConversion,
                                iface=iface,
                                params=iface.GetCpuRegsForInSignature(fun.input_types))


def _InsPushargConversionReverse(ins: ir.Ins, fun: ir.Fun,
                                 iface: PushPopInterface,
                                 params: List[ir.CpuReg]) -> Optional[
    List[ir.Ins]]:
    """
    This pass converts pusharg reg -> mov arg_reg = reg

    Note:
         * params is passed around between calls to this function
         * pusharg's always precede calls or returns
    """
    if ins.opcode is o.PUSHARG:
        cpu_reg = params.pop(0)
        src = ins.operands[0]
        reg = fun.FindOrAddCpuReg(cpu_reg, src.kind)
        return [ir.Ins(o.MOV, [reg, src])]
    assert not params, f"params {params} should be empty at ins {ins} {ins.operands}"
    if ins.opcode.is_call():
        callee: ir.Fun = cfg.InsCallee(ins)
        assert isinstance(callee, ir.Fun)
        params += iface.GetCpuRegsForInSignature(callee.input_types)
    elif ins.opcode is o.RET:
        params += iface.GetCpuRegsForOutSignature(fun.output_types)
    return None


def FunPushargConversion(fun: ir.Fun, iface: PushPopInterface):
    return ir.FunGenericRewriteReverse(fun, _InsPushargConversionReverse,
                                       iface=iface, params=[])
