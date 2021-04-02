"""
Convert ARM32 instruction into human readable form suitable to
be processed by an assembler.
"""

from typing import List, Tuple

import CpuA32.opcode_tab as a32
from Elf import enum_tab



def _Merge(*name_lists):
    out = {}
    for nl in name_lists:
        for n, name in enumerate(nl):
            x = out.get(name)
            if x is None:
                out[name] = n
            else:
                assert x == n, f"conflict {n} vs {x} for {name}"
    return out


_PRED_NAMES_MAP = _Merge([p.name for p in a32.PRED])

_REG_NAMES_MAP = _Merge([p.name for p in a32.REG],
                        [f"r{i}" for i in range(16)],
                        [p.name for p in a32.DREG],
                        [p.name for p in a32.SREG])

_SHIFT_NAMES_MAP = _Merge([p.name for p in a32.SHIFT])


def SymbolizeOperandOfficial(opcode: a32.Opcode, operand, ok: a32.OK) -> str:
    """Convert an operand in integer form as found in  arm.Ins to a string

    The result tries to mimic the official notation.
    """
    if ok is a32.OK.REG_LINK:
        return "lr"
    elif ok in a32.FIELDS_SREG:
        return a32.SREG(operand).name
    elif ok in a32.FIELDS_DREG:
        return a32.DREG(operand).name
    elif ok is a32.OK.REG_0_3 and a32.OPC_FLAG.ADDR_DEC in opcode.classes:
        return "-" + a32.REG(operand).name
    elif ok in a32.FIELDS_REG:
        return a32.REG(operand).name
    elif ok is a32.OK.SHIFT_MODE_5_6:
        return a32.SHIFT(operand).name
    elif ok in {a32.OK.IMM_0_7_TIMES_4, a32.OK.IMM_0_11, a32.OK.IMM_0_3_8_11}:
        if a32.OPC_FLAG.ADDR_DEC in opcode.classes:
            return f"#-{operand}"
        else:
            return f"#{operand}"
    elif ok in a32.FIELDS_IMM:
        return f"#{operand}"
    elif ok is a32.OK.PRED_28_31:
        return a32.PRED(operand).name
    elif ok is a32.OK.REGLIST_0_15:
        reg_mask = operand
        regs = [a32.REG(x).name for x in range(16) if reg_mask & (1 << x)]
        expr = "{%s}" % (",".join(regs))
        return expr
    elif ok is a32.OK.REG_RANGE_0_7 or ok is a32.OK.REG_RANGE_1_7:
        return f"#{operand}"
    else:
        assert False, f"OK:{ok} OP:{operand}"


def _EmitReloc(ins: a32.Ins, pos: int) -> str:
    if ins.reloc_kind == enum_tab.RELOC_TYPE_ARM.JUMP24:
        assert ins.is_local_sym, f"expected local symbol"
        return f"expr:jump24:{ins.reloc_symbol}"
    elif ins.reloc_kind == enum_tab.RELOC_TYPE_ARM.MOVT_ABS:
        loc = "loc_" if ins.is_local_sym else ""
        offset = "" if ins.operands[pos] == 0 else f":{ins.operands[pos]}"
        return f"expr:{loc}movt_abs:{ins.reloc_symbol}{offset}"
    elif ins.reloc_kind == enum_tab.RELOC_TYPE_ARM.MOVW_ABS_NC:
        loc = "loc_" if ins.is_local_sym else ""
        offset = "" if ins.operands[pos] == 0 else f":{ins.operands[pos]}"
        return f"expr:{loc}movw_abs_nc:{ins.reloc_symbol}{offset}"
    elif ins.reloc_kind == enum_tab.RELOC_TYPE_ARM.CALL:
        return f"expr:call:{ins.reloc_symbol}"
    else:
        assert False


def SymbolizeOperand(ok: a32.OK, value: int) -> str:
    """Convert an operand in integer form as found in  arm.Ins to a string

    (This does not handle relocation expressions.)
    """
    if ok == a32.OK.PRED_28_31:
        return a32.PRED(value).name
    elif ok in a32.FIELDS_REG:
        return a32.REG(value).name
    elif ok in a32.FIELDS_DREG:
        return a32.DREG(value).name
    elif ok in a32.FIELDS_SREG:
        return a32.SREG(value).name
    elif ok in a32.FIELDS_IMM:
        return f"{value}"
    elif ok in a32.FIELDS_SHIFT:
        return a32.SHIFT(value).name
    elif ok is a32.OK.REG_RANGE_0_7 or ok is a32.OK.REG_RANGE_1_7:
        return f"regrange:{value}"
    elif ok is a32.OK.REGLIST_0_15:
        return f"reglist:0x{value:04x}"
    else:
        assert False, f"unsupported field {ok}"
        return ""


def UnsymbolizeOperand(o: str, ok: a32.OK) -> int:
    """Convert a symbolized operand  into an int suitable for arm.Ins

    This does not handle relocation expressions.
    """
    if ok is a32.OK.SHIFT_MODE_5_6:
        return _SHIFT_NAMES_MAP[o]
    elif ok is a32.OK.PRED_28_31:
        return _PRED_NAMES_MAP[o]
    x = _REG_NAMES_MAP.get(o)
    if x is not None:
        return x
    elif ":" in o:
        tag, val = o.split(":")
        return int(val, 0)
    else:
        # must be a number
        return int(o, 0)


_RELOC_KIND_MAP = {
    # these relocations imply that the symbol is local
    "jump24": enum_tab.RELOC_TYPE_ARM.JUMP24,
    # these relocations imply that the symbol is local
    # unless prefixed with `loc_`
    "abs32": enum_tab.RELOC_TYPE_ARM.ABS32,
    "call": enum_tab.RELOC_TYPE_ARM.CALL,
    "movw_abs_nc": enum_tab.RELOC_TYPE_ARM.MOVW_ABS_NC,
    "movt_abs": enum_tab.RELOC_TYPE_ARM.MOVT_ABS,
}


def InsSymbolize(ins: a32.Ins) -> Tuple[str, List[str]]:
    """Convert all the operands in an arm.Ins to strings including relocs
    """
    ops = []
    for pos, (field, value) in enumerate(zip(ins.opcode.fields, ins.operands)):
        if field in a32.FIELDS_IMM and ins.reloc_kind != 0 and ins.reloc_pos == pos:
            ops.append(_EmitReloc(ins, pos))
        else:
            ops.append(SymbolizeOperand(field, value))

    return ins.opcode.NameForEnum(), ops


def InsFromSymbolized(mnemonic, token: List[str]) -> a32.Ins:
    """Takes textual form of an A32 instruction (in systematic notation) and parses it into a Ins

     * Supports relocatable expressions
     * Adds missing "al" predicate if necessary
     Example input:
     "add_regimm", ["r4", "r4", "r0", "lsl", "0"]
     """
    opcode: a32.Opcode = a32.Opcode.name_to_opcode[mnemonic]
    if opcode.HasPred() and len(token) == len(opcode.fields) - 1:
        token = ["al"] + token
    ins = a32.Ins(opcode)
    for pos, (t, ok) in enumerate(zip(token, opcode.fields)):
        if t.startswith("expr:"):
            # expr strings have the form expr:<rel-kind>:<symbol>:<addend>, e.g.:
            #   expr:movw_abs_nc:string_pointers:5
            #   expr:call:putchar
            rel_token = t.split(":")
            if len(rel_token) == 3:
                rel_token.append("0")
            if rel_token[1] == "jump24":
                ins.is_local_sym = True
            if rel_token[1].startswith("loc_"):
                ins.is_local_sym = True
                rel_token[1] = rel_token[1][4:]
            ins.reloc_kind = _RELOC_KIND_MAP[rel_token[1]]
            ins.reloc_pos = pos
            ins.reloc_symbol = rel_token[2]
            ins.operands.append(int(rel_token[3], 0))
        else:
            ins.operands.append(UnsymbolizeOperand(t, ok))
    return ins
