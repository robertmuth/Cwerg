from typing import List, Dict, Optional, Tuple

from Base import ir
from Base import opcode_tab as o
from Base import lowering
from Base import optimize

from CodeGenX64 import regs


def DumpBbl(bbl: ir.Bbl):
    print("\n".join(serialize.BblRenderToAsm(bbl)))


def DumpFun(reason: str, fun: ir.Fun):
    print("#" * 60)
    print(f"# {reason}", fun.name)
    print("#" * 60)
    print("\n".join(serialize.FunRenderToAsm(fun)))


_SUPPORTED_IN_ALL_WIDTHS = {
    o.ADD, o.SUB, o.XOR, o.AND, o.OR,
}


def IsOutOfBoundImmediate(op) -> bool:
    if not isinstance(op, ir.Const):
        return False
    if op.kind in {o.DK.S64, o.DK.A64, o.DK.F64}:
        return op.value < -(1 << 31) or (1 << 31) <= op.value
    elif op.kind is o.DK.U64:
        return (1 << 31) <= op.value
    elif op.kind is {o.DK.F64, o.DK.F32}:
        return True
    else:
        assert False


def _InsRewriteOutOfBoundsImmediates(
        ins: ir.Ins, fun: ir.Fun, unit: ir.Unit) -> Optional[List[ir.Ins]]:
    inss = []
    if ins.opcode.kind in {o.OPC_KIND.ALU, o.OPC_KIND.COND_BRA, o.OPC_KIND.ALU1}:
        for pos, op in enumerate(ins.operands):
            if IsOutOfBoundImmediate(op):
                if op.kind in {o.DK.F32, o.DK.F64}:
                    inss += lowering.InsEliminateImmediateViaMem(ins, pos, fun, unit,
                                                                 o.DK.A64, o.DK.U32)
                else:
                    inss.append(lowering.InsEliminateImmediateViaMov(ins, pos, fun))

    inss.append(ins)
    return inss


def _FunRewriteOutOfBoundsImmediates(fun: ir.Fun, unit: ir.Unit) -> int:
    return ir.FunGenericRewrite(fun, _InsRewriteOutOfBoundsImmediates, unit=unit)


def NeedsAABFromRewrite(ins: ir.Ins):
    if ins.opcode.kind not in {o.OPC_KIND.ALU, o.OPC_KIND.LEA}:
        return False
    if ins.operands[0] == ins.operands[1]:
        return False
    return True


def _InsRewriteIntoAABForm(
        ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:

    ops = ins.operands
    if not NeedsAABFromRewrite(ins):
        return []
    if o.OA.COMMUTATIVE in ins.opcode.attributes:
        ir.InsSwapOps(ins, 1, 2)
        return [ins]
    else:
        reg = fun.GetScratchReg(ins.operands[0].kind, "aab", False)
        return [ir.Ins(o.MOV, [reg, ops[1]]),
                ir.Ins(ins.opcode, [reg, reg, ops[2]]),
                ir.Ins(o.MOV, [ops[0], reg])]
    return [ir.Ins(o.MOV, [ops[0], ops[1]]),
            ir.Ins(ins.opcode, [ops[0], ops[0], ops[2]])]


def _FunRewriteIntoAABForm(fun: ir.Fun, unit: ir.Unit) -> int:
    """Bring instructions into A A B form (dst == src1). See README.md"""
    return ir.FunGenericRewrite(fun, _InsRewriteIntoAABForm)


def PhaseOptimize(fun: ir.Fun, unit: ir.Unit, opt_stats: Dict[str, int], fout):
    optimize.FunCfgInit(fun, unit)
    optimize.FunOptBasic(fun, opt_stats, allow_conv_conversion=True)


def PhaseLegalization(fun: ir.Fun, unit: ir.Unit, _opt_stats: Dict[str, int], fout):
    """
    Does a lot of the heavily lifting so that the instruction selector can remain
    simple and table driven.
    * lift almost all regs to 32bit width
    * rewrite Ins that cannot be expanded
    * rewrite immediates that cannot be expanded except stack offsets which are dealt with in
      another pass

    TODO: missing is a function to change calling signature so that
    """
    _FunRewriteIntoAABForm(fun, unit)


    fun.cpu_live_in = regs.GetCpuRegsForInSignature(fun.input_types)
    fun.cpu_live_out = regs.GetCpuRegsForOutSignature(fun.output_types)
    if fun.kind is not o.FUN_KIND.NORMAL:
        return

    # Getting rid of the pusharg/poparg now relieves us form having to pay to attention to  the
    # invariant that pushargs/popargs must be adjacent.
    regs.FunPushargConversion(fun)
    regs.FunPopargConversion(fun)

    # ARM has no mod instruction
    lowering.FunEliminateRem(fun)

    # A64 has not support for these addressing modes
    lowering.FunEliminateStkLoadStoreWithRegOffset(fun, base_kind=o.DK.A64,
                                                   offset_kind=o.DK.S32)

    # we cannot load/store directly from mem so expand the instruction to simpler
    # sequences
    lowering.FunEliminateMemLoadStore(fun, base_kind=o.DK.A64,
                                      offset_kind=o.DK.S32)

    canonicalize.FunCanonicalize(fun)
    # TODO: add a cfg linearization pass to improve control flow
    optimize.FunCfgExit(fun, unit)  # not this may affect immediates as it flips branches

    # Handle most overflowing immediates.
    # This excludes immediates related to stack offsets which have not been determined yet
    _FunRewriteOutOfBoundsImmediates(fun, unit)

    sanity.FunCheck(fun, None)
    # optimize.FunOptBasic(fun, opt_stats, allow_conv_conversion=False)
