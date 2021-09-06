"""This file contains helpers related to the CFG (Control Flow Graph)"""
# (c) Robert Muth - see LICENSE for more info

from typing import List, Tuple, Set

from Base import ir
from Base import opcode_tab as o

_OPCODE_BRANCH_INVERSION = {  #
    o.BNE: (o.BEQ, False),
    o.BEQ: (o.BNE, False),
    o.BLE: (o.BLT, True),
    o.BLT: (o.BLE, True),
}


def InsCallee(ins: ir.Ins) -> ir.Fun:
    opc = ins.opcode
    if opc is o.SYSCALL or opc is o.BSR:
        assert isinstance(ins.operands[0], ir.Fun)
        return ins.operands[0]
    elif opc is o.JSR:
        assert isinstance(ins.operands[1], ir.Fun)
        return ins.operands[1]
    else:
        assert False, f"not a call instruction: {ins}"


def NewDerivedBblName(orig_name: str, suffix: str, fun: ir.Fun) -> str:
    for i in range(1, 100000):
        cand = f"{orig_name}{suffix}{i}"
        if cand not in fun.bbl_syms:
            return cand
    assert False


# TODO: we should reject code that triggers this
def _BblRemoveUnreachableIns(bbl: ir.Bbl):
    n = 0
    for n, ins in enumerate(bbl.inss):
        if ins.opcode.kind in {o.OPC_KIND.RET, o.OPC_KIND.BRA}:
            break
    if n != len(bbl.inss):
        bbl.inss = bbl.inss[:n + 1]


def _BblFindSubRanges(bbl: ir.Bbl) -> List[Tuple[int, int]]:
    """Find control flow changing instructions in the middle of a bbl"""
    out: List[Tuple[int, int]] = []
    last = 0
    for n, ins in enumerate(bbl.inss[:-1]):
        if ins.opcode.is_bbl_terminator():
            out.append((last, n + 1))
            last = n + 1
    out.append((last, len(bbl.inss)))
    return out


def FunSplitBbls(fun: ir.Fun):
    """split bbls and remove dead code after 'ret'"""
    for bbl in fun.bbl_syms.values():
        assert not bbl.forward_declared, f"bbl referenced but not defined {bbl}"

    bbls = []
    for bbl in fun.bbls:
        _BblRemoveUnreachableIns(bbl)
        ranges = _BblFindSubRanges(bbl)
        # print ("@@@@ ranges", ranges)
        inss = bbl.inss
        for start, end in ranges:
            new_bbl = bbl
            if start != 0:
                new_bbl = ir.Bbl(NewDerivedBblName(bbl.name, "_", fun))
                fun.bbl_syms[bbl.name] = bbl
            new_bbl.inss = inss[start:end]
            bbls.append(new_bbl)
            fun.bbl_syms[new_bbl.name] = new_bbl
    fun.bbls = bbls


def FunInitCFG(fun: ir.Fun):
    """
    Initializes the bbl.edge_in and bbl.edge_out fields

    Also cleans up unreachable code at the end
    """
    # add edges. note: order is not guaranteed
    fall_through: ir.Bbl = ir.BBL_INVALID
    for bbl in fun.bbls:
        if fall_through is not ir.BBL_INVALID:
            fall_through.AddEdgeOut(bbl)
            fall_through = ir.BBL_INVALID
        if not bbl.inss:
            fall_through = bbl
        else:
            last_ins: ir.Ins = bbl.inss[-1]
            last_ins_kind = last_ins.opcode.kind
            if last_ins_kind == o.OPC_KIND.RET:
                pass
            elif last_ins_kind in {o.OPC_KIND.BRA}:
                bbl.AddEdgeOut(last_ins.operands[0])
            elif last_ins_kind is o.OPC_KIND.COND_BRA:
                bbl.AddEdgeOut(last_ins.operands[2])
                fall_through = bbl
            elif last_ins_kind == o.OPC_KIND.SWITCH:
                jtb = last_ins.operands[1]
                bbl.AddEdgeOut(jtb.def_bbl)
                for succ in jtb.bbl_tab.values():
                    bbl.AddEdgeOut(succ)
            else:  # includes BSR/JSR
                fall_through = bbl

    # Cwerg may generate an unreachable fallthrough bbl at the end of the function
    # Note that _BblRemoveUnreachableIns will (hopefully) remove branches to this code
    # TODO: we should reject code that triggers this
    if fall_through is not ir.BBL_INVALID:
        last_bbl = fun.bbls[-1]
        assert not last_bbl.inss, f"garbage bbl not empty in {fun.name}"
        del fun.bbl_syms[last_bbl.name]
        fun.bbls.pop(-1)


def FunRemoveUnconditionalBranches(fun: ir.Fun):
    """
    Removes unconditional branches.

    This only works after FunInitCFG because

    Sort of inverse to FunAddUnconditionalBranches
    """
    for bbl in fun.bbls:
        inss = bbl.inss
        if not inss:
            continue
        last_ins_kind = inss[-1].opcode.kind
        if last_ins_kind == o.OPC_KIND.BRA:
            inss.pop(-1)
    fun.flags |= ir.FUN_FLAG.CFG_NOT_LINEAR


def InsFlipCondBra(ins: ir.Ins, old_target: ir.Bbl, new_target: ir.Bbl):
    assert ins.operands[2] == old_target
    ins.operands[2] = new_target
    ins.opcode, must_flip = _OPCODE_BRANCH_INVERSION[ins.opcode]
    if must_flip:
        ir.InsSwapOps(ins, 0, 1)


def InsMaybePatchNewSuccessor(last_ins: ir.Ins, old_succ: ir.Bbl,
                              new_succ: ir.Bbl):
    """ forward out going edges in ins from old_succ to new_succ

    Does not change edges just the bbls in instructions and jtbs
    """

    last_ins_kind = last_ins.opcode.kind
    if last_ins_kind is o.OPC_KIND.BRA:
        if last_ins.operands[0] == old_succ:
            last_ins.operands[0] = new_succ
            return True
        else:
            return False
    elif last_ins_kind is o.OPC_KIND.COND_BRA:
        if last_ins.operands[2] == old_succ:
            last_ins.operands[2] = new_succ
            return True
        else:
            return False
    elif last_ins_kind == o.OPC_KIND.SWITCH:
        jtb = last_ins.operands[1]
        assert isinstance(jtb, ir.Jtb)
        if jtb.def_bbl == old_succ:
            jtb.def_bbl = new_succ
        for k, v in jtb.bbl_tab.items():
            if v == old_succ:
                jtb.bbl_tab[k] = new_succ
        return True
    else:
        return False


def FunRemoveEmptyBbls(fun: ir.Fun) -> int:
    keep = []
    for bbl in fun.bbls:
        if bbl.inss:
            keep.append(bbl)
            continue
        succ = bbl.edge_out[0]
        if succ == bbl:
            # we have to keep infinite loop
            keep.append(bbl)
            continue
        # print ("BBL -DELETE", bbl.name)
        # print("IN",  bbl.edge_in)
        # print ("OUT", bbl.edge_out)
        del fun.bbl_syms[bbl.name]
        # assert bbl != fun.bbls[0], f"attempt to delete first bbl in fun {fun.name}"
        assert len(bbl.edge_out) == 1, bbl
        succ = bbl.edge_out[0]
        bbl.DelEdgeOut(succ)
        # We need to clone the edge list since we have destructive updates
        # but while we are at it let's also process every predecessor only once
        unique_preds: Set[str] = set(pred.name for pred in bbl.edge_in)
        for pred_name in unique_preds:
            pred = fun.bbl_syms[pred_name]
            inss = pred.inss
            if inss:
                InsMaybePatchNewSuccessor(inss[-1], bbl,
                                          succ)  # patch ins/jtb
            pred.ReplaceEdgeOut(bbl, succ)  # patch edg

    discarded = len(fun.bbls) - len(keep)
    fun.bbls = keep
    return discarded


def FunRemoveUnreachableBbls(fun: ir.Fun) -> int:
    reachable = set()
    stack: List[ir.Bbl] = [fun.bbls[0]]
    while stack:
        curr = stack.pop(-1)
        if curr.name in reachable:
            continue
        reachable.add(curr.name)
        stack += curr.edge_out

    discarded = len(fun.bbls) - len(reachable)
    for bbl in fun.bbls:
        if bbl.name in reachable:
            continue
        for succ in bbl.edge_out:
            succ.edge_in.remove(bbl)
    fun.bbls = [bbl for bbl in fun.bbls if bbl.name in reachable]
    fun.bbl_syms = {bbl.name: bbl for bbl in fun.bbls}
    return discarded


def FunAddUnconditionalBranches(fun: ir.Fun):
    """Re-insert necessary unconditional branches

    sort of inverse of FunRemoveUnconditionalBranches
    """
    bbls = []
    for n, bbl in enumerate(fun.bbls):
        bbls.append(bbl)
        if bbl.inss and not bbl.inss[-1].opcode.has_fallthrough():
            continue
        if len(bbl.edge_out) == 1:
            assert len(fun.bbls) > n
            succ = bbl.edge_out[0]
            if n + 1 == len(fun.bbls) or fun.bbls[n + 1] != succ:
                bbl.inss.append(ir.Ins(o.BRA, [succ]))
            continue

        assert len(bbl.edge_out) == 2
        cond_bra = bbl.inss[-1]
        assert cond_bra.opcode.kind is o.OPC_KIND.COND_BRA, (
            f"not a cond bra: {cond_bra}  bbl: {bbl}")
        target = cond_bra.operands[2]
        other = bbl.edge_out[0] if target == bbl.edge_out[1] else bbl.edge_out[
            1]
        succ = fun.bbls[n + 1]
        if succ in bbl.edge_out:
            # target == other can happen if the cond_bra is pointless
            if target == succ and target != other:
                InsFlipCondBra(cond_bra, target, other)
            continue
        else:
            bbl_bra = ir.Bbl(NewDerivedBblName(bbl.name, "bra", fun))
            bbl_bra.inss.append(ir.Ins(o.BRA, [other]))
            fun.bbl_syms[bbl_bra.name] = bbl_bra
            # forward fallthrough to new bbl
            if bbl.inss:
                InsMaybePatchNewSuccessor(bbl.inss[-1], other, bbl_bra)
            bbl.ReplaceEdgeOut(other, bbl_bra)
            bbl_bra.AddEdgeOut(other)
            bbls.append(bbl_bra)
    fun.bbls = bbls
    fun.flags &= ~ir.FUN_FLAG.CFG_NOT_LINEAR
