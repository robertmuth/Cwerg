"""This file contains code for reaching definitions analysis
and optimization depending on it, e.g. constant propagation, etc."""

import dataclasses
from typing import Dict, Tuple, Any, Optional, List, Set

from BE.Base import ir
from IR import opcode_tab as o
from BE.Base import serialize
from BE.Base import eval


def FunCheckReachingDefs(fun: ir.Fun):
    for bbl in fun.bbls:
        for ins in bbl.inss:
            num_defs = ins.opcode.def_ops_count()
            for n, reg in enumerate(ins.operands):
                if n >= num_defs and isinstance(reg, ir.Reg):
                    assert isinstance(ins.operand_defs[n], (ir.Ins, ir.Bbl)), (
                        f"unexpected def in {ins} {ins.operands}  {ins.operand_defs}")
                else:
                    assert ins.operand_defs[n] is ir.INS_INVALID


def _InsConstantFold(
        ins: ir.Ins, bbl: ir.Bbl, _fun: ir.Fun,
        allow_conv_conversion: bool) -> Optional[List[ir.Ins]]:
    """
    Try combining the constant from ins_def with the instruction in ins

    Return 1 iff a change was made

    Note: None of the transformations must change the def register - otherwise
    the reaching_defs will be stale
    """

    ops = ins.operands
    kind = ins.opcode.kind
    if kind is o.OPC_KIND.COND_BRA:
        if not isinstance(ops[0], ir.Const) or not isinstance(ops[1], ir.Const):
            return None
        branch_taken = eval.EvaluatateCondBra(ins.opcode, ops[0], ops[1])
        target = ops[2]
        assert len(bbl.edge_out) == 2
        if branch_taken:
            succ_to_drop = bbl.edge_out[1] if bbl.edge_out[0] == target else \
                bbl.edge_out[0]
        else:
            succ_to_drop = target
        bbl.DelEdgeOut(succ_to_drop)
        return []
    elif kind is o.OPC_KIND.CMP:
        if not isinstance(ops[3], ir.Const) or not isinstance(ops[4], ir.Const):
            return None
        cmp_true = eval.EvaluatateCondBra(
            o.BEQ if ins.opcode is o.CMPEQ else o.BLT, ops[3], ops[4])
        if cmp_true:
            ins.Init(o.MOV, [ops[0], ops[1]], ins.is_only_def)
        else:
            ins.Init(o.MOV, [ops[0], ops[2]], ins.is_only_def)
    elif kind is o.OPC_KIND.ALU1:
        if not isinstance(ops[1], ir.Const):
            return None
        new_op = eval.EvaluatateALU1(ins.opcode, ops[1])
        ins.Init(o.MOV, [ops[0], new_op], ins.is_only_def)
        return [ins]
    elif kind is o.OPC_KIND.ALU:
        if not isinstance(ops[1], ir.Const) or not isinstance(ops[2], ir.Const):
            return None
        new_op = eval.EvaluatateALU(ins.opcode, ops[1], ops[2])
        ins.Init(o.MOV, [ops[0], new_op], ins.is_only_def)
        return [ins]
    elif ins.opcode is o.CONV:
        # TODO: this needs some  more thought generally but in
        # particular when we apply register widening
        # transformations, conv instructions end up being the only
        # ones with narrow width regs which simplifies
        # code generation. By allowing this to be converted into a
        # mov instruction we may leak the narrow register.
        if not allow_conv_conversion or not isinstance(ops[1], ir.Const):
            return None
        dst: ir.Reg = ops[0]
        src = ops[1]
        if not o.RegIsAddrInt(src.kind) or not o.RegIsAddrInt(dst.kind):
            return None
        new_val = eval.ConvertIntValue(dst.kind, src)
        ins.Init(o.MOV, [dst, new_val], ins.is_only_def)
        return [ins]
    else:
        return None


def FunConstantFold(fun: ir.Fun, allow_conv_conversion) -> int:
    """Relies solely on the ins.operand_def info"""
    return ir.FunGenericRewriteWithBbl(fun, _InsConstantFold,
                                       allow_conv_conversion=allow_conv_conversion)


def _CombinedOffset(ins: ir.Ins, base_ins: ir.Ins) -> Tuple[Any, Any]:
    """Returns the combine offset, where it was defined and its original type
     The second is relevant if the offset is a Reg and allows us
     to check that Reg's content is still available at the location
     using the combined offset.
     """
    off_pos = 1 if ins.opcode is o.ST else 2
    offset1 = ins.operands[off_pos]

    if base_ins.opcode is o.MOV:
        return offset1, ins.operand_defs[off_pos]
    if base_ins.opcode.kind != o.OPC_KIND.LEA:
        return None, None

    offset2 = base_ins.operands[2]

    if isinstance(offset1, ir.Const) and offset1.IsZero():
        return offset2, base_ins.operand_defs[2]
    if isinstance(offset2, ir.Const) and offset2.IsZero():
        return offset1, ins.operand_defs[off_pos]
    if isinstance(offset1, ir.Const) and isinstance(offset2, ir.Const):
        return eval.AddOffsets(offset1, offset2), None
    return None, None


_LOAD_STORE_BASE_REWRITE = {
    #  base         mem access ->  new mem access
    (o.LEA_MEM, o.LD): o.LD_MEM,
    (o.LEA_STK, o.LD): o.LD_STK,
    (o.LEA, o.LD): o.LD,
    (o.MOV, o.LD): o.LD,

    (o.LEA_MEM, o.ST): o.ST_MEM,
    (o.LEA_STK, o.ST): o.ST_STK,
    (o.LEA, o.ST): o.ST,
    (o.MOV, o.ST): o.ST,
    #
    (o.LEA_MEM, o.LEA): o.LEA_MEM,
    (o.LEA_STK, o.LEA): o.LEA_STK,
    (o.LEA, o.LEA): o.LEA,
    (o.MOV, o.LEA): o.LEA,
}


def _DefAvailable(op: Any, op_def: Any, bbl, def_map: ir.REG_DEF_MAP) -> bool:
    if isinstance(op, (ir.Const, ir.Mem, ir.Stk)):
        return True
    if isinstance(op_def, ir.Ins) and op_def.is_only_def:
        return True

    assert isinstance(op, ir.Reg), f"unexpected operand {op}"

    if def_map.get(op) is op_def:
        return True
    # we defined outside bbl and has not beem clobbered inside BBL
    if op_def is bbl and op not in def_map:
        return True

    return False


def _InsTryLoadStoreSimplify(ins: ir.Ins, bbl, defs: ir.REG_DEF_MAP) -> int:
    if ins.opcode not in {o.ST, o.LD, o.LEA}:
        return 0
    # do we have a suitable ins defining the base of the ld/st?
    base_pos = 0 if ins.opcode is o.ST else 1
    ins_base = ins.operand_defs[base_pos]

    if ins_base is ir.INS_INVALID or not isinstance(ins_base, ir.Ins):
        return 0

    new_opc = _LOAD_STORE_BASE_REWRITE.get((ins_base.opcode, ins.opcode))
    if new_opc is None:
        return 0

    # is the original base still available at the ld/st
    base_op = ins_base.operands[1]
    base_def = ins_base.operand_defs[1]
    if not _DefAvailable(base_op, base_def, bbl, defs):
        # print ("#base not avail ", base, base_def)
        return 0

    # can the new offset be determined and is it available
    offset, offset_def = _CombinedOffset(ins, ins_base)
    if offset is None or not _DefAvailable(offset, offset_def, bbl, defs):
        return 0

    if base_pos == 0:  # store
        new_defs = [base_def, offset_def, ins.operand_defs[2]]
        ins.Init(new_opc, [base_op, offset, ins.operands[2]], False)
        ins.operand_defs = new_defs
    else:
        new_defs = [ins.operand_defs[0], base_def, offset_def]
        assert base_pos == 1
        ins.Init(new_opc, [ins.operands[0], base_op, offset], ins.is_only_def)
        ins.operand_defs = new_defs
    # print("#>>>> ", serialize.InsRenderToAsm(ins))

    return 1


def _BblLoadStoreSimplify(bbl: ir.Bbl, _fun: ir.Fun) -> int:
    """

    Requires reaching definitions both per bbl and per ins
    """
    # we need to clone defs_in becasse we update the map as we iterate
    # through the bbl
    def_map: ir.REG_DEF_MAP = {}
    count = 0
    for ins in bbl.inss:
        if ins.opcode in {o.ST, o.LD, o.LEA}:
            count += _InsTryLoadStoreSimplify(ins, bbl, def_map)
        if ins.opcode.def_ops_count() > 0:
            def_reg = ins.operands[0]
            def_map[def_reg] = ins

    return count


def FunLoadStoreSimplify(fun: ir.Fun) -> int:
    return ir.FunGenericRewriteBbl(fun, _BblLoadStoreSimplify)


def _BblMergeMoveWithSrcDef(bbl: ir.Bbl, _fun: ir.Fun) -> int:
    """
    This transformation will make certain MOVs obsolete.

     op x = a b
     [stuff]
     mov y = x

     will become


     op y = a b
     mov x = y
     [stuff]
     [deleted]

    """
    last_def_pos: Dict[ir.Reg, int] = {}
    last_use_pos: Dict[ir.Reg, int] = {}
    inss: List[ir.Ins] = []

    def update_def_use(ins: ir.Ins, pos):
        num_defs = ins.opcode.def_ops_count()
        for n, op in enumerate(ins.operands):
            if not isinstance(op, ir.Reg):
                continue
            if n < num_defs:
                last_def_pos[op] = pos
            else:
                last_use_pos[op] = pos

    def is_suitable_mov(mov: ir.Ins) -> bool:
        ops = mov.operands
        if mov.opcode is not o.MOV or not isinstance(ops[1], ir.Reg) or ops[0] == ops[1]:
            return False
        src_def_pos = last_def_pos.get(ops[1], -1)
        if src_def_pos < 0:
            return False
        # avoid inserting MOVs inbetween POPARGs - this could be improved
        if len(inss) > src_def_pos + 1 and inss[src_def_pos + 1].opcode is o.POPARG:
            return False
        # no intervening use of ops[0]
        dst_def_pos = last_def_pos.get(ops[0], -1)
        if dst_def_pos > src_def_pos:
            return False
        dst_use_pos = last_use_pos.get(ops[0], -1)
        if dst_use_pos > src_def_pos:
            return False
        return True

    count = 0
    for ins in bbl.inss:

        if is_suitable_mov(ins):
            count += 1
            dst_reg, src_reg = ins.operands
            src_def_pos = last_def_pos[src_reg]
            ins_src_def = inss[src_def_pos]
            assert ins_src_def.operands[0] == src_reg
            ins_src_def.operands[0] = dst_reg
            last_def_pos[dst_reg] = src_def_pos
            ir.InsSwapOps(ins, 0, 1)
            inss.insert(src_def_pos + 1, ins)
            for pos in range(src_def_pos + 1, len(inss)):
                update_def_use(inss[pos], pos)
        else:
            update_def_use(ins, len(inss))
            inss.append(ins)

    bbl.inss = inss
    return count


def FunMergeMoveWithSrcDef(fun: ir.Fun) -> int:
    """ """
    return ir.FunGenericRewriteBbl(fun, _BblMergeMoveWithSrcDef)


def FunComputeReachingDefs(fun: ir.Fun):
    # Phase 1: build map
    defs: ir.REG_DEF_MAP = {}
    for bbl in fun.bbls:
        for ins in bbl.inss:
            if ins.opcode.def_ops_count() == 0:
                continue
            def_reg = ins.operands[0]
            assert isinstance(def_reg, ir.Reg)
            if def_reg in defs:
                defs[def_reg] = ir.INS_INVALID
            else:
                defs[def_reg] = ins

    # phase 2: fill in all the ins.operand_def fields
    # Note: we could do this for extended BBLs
    bbl_defs: ir.REG_DEF_MAP = {}
    for bbl in fun.bbls:
        bbl_defs.clear()
        for ins in bbl.inss:
            num_defs = ins.opcode.def_ops_count()
            for n, op in enumerate(ins.operands):
                if n < num_defs:
                    continue
                if not isinstance(op, ir.Reg):
                    ins.operand_defs[n] = ir.INS_INVALID
                    continue
                def_ins = defs.get(op)
                assert def_ins is not None, f"No defound for {ins} {op} in {bbl}"
                if def_ins is ir.INS_INVALID:
                    def_ins = bbl_defs.get(op, bbl)
                ins.operand_defs[n] = def_ins

            if num_defs == 0:
                ins.is_only_def = False  # does not really matter
            else:
                def_reg = ins.operands[0]
                ins.is_only_def = defs[def_reg] is not ir.INS_INVALID
                bbl_defs[def_reg] = ins


def _BblPropagateRegAndConstOperands(bbl: ir.Bbl, _fun: ir.Fun) -> int:
    """
    This transformation will make certain MOVs obsolete.

    Requires FunSimplifiedReachingDefs()
    """
    count = 0
    def_map: ir.REG_DEF_MAP = {}
    for ins in bbl.inss:
        num_defs = ins.opcode.def_ops_count()
        for n, mov in enumerate(ins.operand_defs):
            if n < num_defs:
                continue
            if not isinstance(mov, ir.Ins) or mov.opcode is not o.MOV:
                continue
            src_op = mov.operands[1]
            src_def = mov.operand_defs[1]
            assert mov.operands[0] == ins.operands[n]

            # we do not want to extend live ranges for allocated regs
            if isinstance(src_op, ir.Reg) and src_op.cpu_reg:
                continue
            # constant propagation is done by another pass
            if _DefAvailable(src_op, src_def, bbl, def_map):
                ins.operands[n] = src_op
                ins.operand_defs[n] = src_def
                count += 1

        if num_defs > 0:
            def_reg = ins.operands[0]
            def_map[def_reg] = ins

    return count


def FunPropagateRegsAndConsts(fun: ir.Fun) -> int:
    """Relies solely on the ins.operand_def info"""
    return ir.FunGenericRewriteBbl(fun, _BblPropagateRegAndConstOperands)


def FunMoveElimination(fun: ir.Fun) -> int:
    """backwards move elimination

    TODO: give example
    """
    count = 0
    for bbl in fun.bbls:
        for ins in bbl.inss:
            if ins.opcode is o.MOV and isinstance(ins.operands[1], ir.Reg):
                dst: ir.Reg = ins.operands[0]
                src: ir.Reg = ins.operands[1]
                if src.flags & ir.REG_FLAG.MULTI_DEF:
                    continue
                if src.flags & ir.REG_FLAG.MULTI_READ:
                    continue
                if src.flags & ir.REG_FLAG.LAC:
                    continue

                src_def = ins.operand_defs[1]
                if src_def == ir.INS_INVALID:
                    continue
                if not isinstance(src_def, ir.Ins):
                    continue
                # print (f"@@BEFORE {ins} {ins.operands}")
                # print ("\n".join(serialize.BblRenderToAsm(bbl)))
                # This will be taken care of by nop removal
                ins.operands[1] = dst
                # TODO: assumes at most one def per ins
                assert src_def.operands[0] == src
                src_def.operands[0] = dst
                # print ("@@AFTER")
                # print ("\n".join(serialize.BblRenderToAsm(bbl)))
                count += 1
                if count == 2:
                    return count
    return count
