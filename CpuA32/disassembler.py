#!/usr/bin/python3

"""
Convert ARM32 instruction into human readable form suitable to
be processed by an assembler.
"""

import CpuA32.opcode_tab as arm
from Elf import enum_tab

from typing import List


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


PRED_NAMES_MAP = _Merge([p.name for p in arm.PRED])

REG_NAMES_MAP = _Merge([p.name for p in arm.REG],
                       [f"r{i}" for i in range(16)],
                       [p.name for p in arm.DREG],
                       [p.name for p in arm.SREG])

SHIFT_NAMES_MAP = _Merge([p.name for p in arm.SHIFT])


# render a single operand, e.g. and address like  `[r3, #-116]`
def RenderOperandStd(opcode: arm.Opcode, operand, ok) -> str:
    if ok is arm.OK.REG_LINK:
        return "lr"
    elif ok in arm.FIELDS_SREG:
        return arm.SREG(operand).name
    elif ok in arm.FIELDS_DREG:
        return arm.DREG(operand).name
    elif ok is arm.OK.REG_0_3 and arm.OPC_FLAG.ADDR_DEC in opcode.classes:
        return "-" + arm.REG(operand).name
    elif ok in arm.FIELDS_REG:
        return arm.REG(operand).name
    elif ok is arm.OK.SHIFT_MODE_5_6:
        return arm.SHIFT(operand).name
    elif ok in {arm.OK.IMM_0_7_TIMES_4, arm.OK.IMM_0_11, arm.OK.IMM_0_3_8_11}:
        if arm.OPC_FLAG.ADDR_DEC in opcode.classes:
            return f"#-{operand}"
        else:
            return f"#{operand}"
    elif ok in arm.FIELDS_IMM:
        return f"#{operand}"
    elif ok is arm.OK.PRED_28_31:
        return arm.PRED(operand).name
    elif ok is arm.OK.REGLIST_0_15:
        reg_mask = operand
        regs = [arm.REG(x).name for x in range(16) if reg_mask & (1 << x)]
        expr = "{%s}" % (",".join(regs))
        return expr
    elif ok is arm.OK.REG_RANGE_0_7 or ok is arm.OK.REG_RANGE_1_7:
        return f"#{operand}"
    else:
        assert False, f"OK:{ok} OP:{operand}"


def _EmitReloc(ins: arm.Ins, pos: int) -> str:
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


def _SymbolizeOperand(field: arm.OK, value: int) -> str:
    if field == arm.OK.PRED_28_31:
        return arm.PRED(value).name
    elif field in arm.FIELDS_REG:
        return arm.REG(value).name
    elif field in arm.FIELDS_DREG:
        return arm.DREG(value).name
    elif field in arm.FIELDS_SREG:
        return arm.SREG(value).name
    elif field in arm.FIELDS_IMM:
        return f"{value}"
    elif field in arm.FIELDS_SHIFT:
        return arm.SHIFT(value).name
    elif field is arm.OK.REG_RANGE_0_7 or field is arm.OK.REG_RANGE_1_7:
        return f"regrange:{value}"
    elif field is arm.OK.REGLIST_0_15:
        return f"reglist:0x{value:04x}"
    else:
        assert False, f"unsupported field {field}"
        return ""


def SymbolizeOperands(ins: arm.Ins) -> List[str]:
    out = []
    for pos, (field, value) in enumerate(zip(ins.opcode.fields, ins.operands)):
        if field in arm.FIELDS_IMM and ins.reloc_kind != 0 and ins.reloc_pos == pos:
            out.append(_EmitReloc(ins, pos))
        else:
            out.append(_SymbolizeOperand(field, value))
    return out


def RenderInstructionSystematic(ins: arm.Ins) -> str:
    return f"{ins.opcode.NameForEnum()} {' '.join(SymbolizeOperands(ins))}"


def UnsymbolizeOperand(o: str, ok: arm.OK) -> int:
    if ok is arm.OK.SHIFT_MODE_5_6:
        return SHIFT_NAMES_MAP[o]
    elif ok is arm.OK.PRED_28_31:
        return PRED_NAMES_MAP[o]
    x = REG_NAMES_MAP.get(o)
    if x is not None:
        return x
    elif ":" in o:
        tag, val = o.split(":")
        return int(val, 0)
    else:
        # must be a number
        return int(o, 0)


_RELOC_KIND_MAP = {
    "abs32": enum_tab.RELOC_TYPE_ARM.ABS32,
    "jump24": enum_tab.RELOC_TYPE_ARM.JUMP24,
    "call": enum_tab.RELOC_TYPE_ARM.CALL,
    "movw_abs_nc": enum_tab.RELOC_TYPE_ARM.MOVW_ABS_NC,
    "movt_abs": enum_tab.RELOC_TYPE_ARM.MOVT_ABS,
}


def InsParse(mnemonic, token: List[str]) -> arm.Ins:
    """Takes textual form of an A32 instruction (in systematic notation) and parses it into a Ins

     * Supports relocatable expressions
     * Adds missing "al" predicate if necessary
     Example input:
     "add_regimm", ["r4", "r4", "r0", "lsl", "0"]
     """
    opcode: arm.Opcode = arm.Opcode.name_to_opcode[mnemonic]
    if opcode.HasPred() and len(token) == len(opcode.fields) - 1:
        token = ["al"] + token
    ins = arm.Ins(opcode)
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


if __name__ == "__main__":
    import sys


    def disass(data):
        ins = arm.Disassemble(data)
        if ins.opcode is None:
            print(f"could not disassemble {data:x}")
            return
        std_name = ins.opcode.name
        std_ops = [RenderOperandStd(ins.opcode, op, ok)
                   for ok, op in zip(ins.opcode.fields, ins.operands)]

        if std_ops and std_ops[0] == "al":
            std_ops.pop(0)
        print(f"{data:08x} {std_name} {', '.join(std_ops)}")
        print("OPCODE", ins.opcode.name, ins.opcode.variant)
        operands_str = SymbolizeOperands(ins)
        for f, o, o_str in zip(ins.opcode.fields, ins.operands, operands_str):
            print(f"    {f.name:19s} {o_str} ({o})")
        print()
        data2 = arm.Assemble(ins)
        assert data == data2
        operands2 = [UnsymbolizeOperand(o, ok)
                     for o, ok in zip(operands_str, ins.opcode.fields)]
        assert tuple(ins.operands) == tuple(

            operands2), f"{ins.operands} vs {operands2}"


    # opcode.AssembleOperands(operands2)

    for arg_hex_number in sys.argv[1:]:
        disass(int(arg_hex_number, 16))
