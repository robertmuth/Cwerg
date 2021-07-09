#!/usr/bin/python3

"""ASM Parser/Dumper"""

import collections
import struct
from typing import List, Dict, Optional, Any

from Base import ir
from Base import opcode_tab as o
from Util import parse
from Base import sanity

PREFIX = ""


def RenderOperand(v: Any, tc: o.TC):
    if isinstance(v, ir.Reg):
        if v.HasCpuReg():
            return f"{v.name}@{v.cpu_reg.name}"
        return v.name
    elif isinstance(v, ir.Fun):
        return PREFIX + v.name
    elif isinstance(v, ir.Bbl):
        return v.name
    elif isinstance(v, ir.Mem):
        return PREFIX + v.name
    elif isinstance(v, ir.Stk):
        return v.name
    elif isinstance(v, ir.Const):
        if tc in {o.TC.OFFSET, o.TC.SAME_AS_PREV}:
            return str(v.value)
        return str(v)
    elif isinstance(v, ir.Jtb):
        return v.name
    else:
        raise ir.ParseError(f"cannot read op type: {v}")


def EscapeCStyle(data: bytes, max_length=1000 * 1000) -> str:
    out = []
    for i in range(0, len(data), max_length):
        out.append(
            '"' + parse.BytesToEscapedString(data[i:i + max_length]) + '"')
    return "\n".join(out)


def MemRenderToAsm(mem: ir.Mem) -> List[str]:
    out = [f".mem {PREFIX + mem.name} {mem.alignment} {mem.kind.name}"]
    for d in mem.datas:
        if isinstance(d, ir.DataBytes):
            out.append(f"    .data {d.count} {EscapeCStyle(d.data)}")
        elif isinstance(d, ir.DataAddrFun):
            out.append(f"    .addr.fun {d.size} {d.fun.name}")
        elif isinstance(d, ir.DataAddrMem):
            out.append(f"    .addr.mem {d.size} {d.mem.name} {d.offset}")
        else:
            assert False, f"NYI {d}"
    return out


def InsRenderToAsm(ins: ir.Ins) -> str:
    ops = [RenderOperand(v, tc) for v, tc in zip(
        ins.operands, ins.opcode.constraints)]
    ops_str = f" {' '.join(ops)}" if ops else ""
    return f"    {ins.opcode.name}{ops_str}"


def BblRenderToAsm(bbl: ir.Bbl) -> List[str]:
    edge_out = sorted([bbl.name for bbl in bbl.edge_out])
    live_out = sorted([r.name for r in bbl.live_out])
    annotations = ""
    if edge_out or live_out:
        annotations = "  #"
        if edge_out:
            annotations += f"  edge_out[{'  '.join(edge_out)}]"
        if live_out:
            annotations += f"  live_out[{'  '.join(live_out)}]"
    out = [f".bbl {bbl.name}{annotations}"]
    for ins in bbl.inss:
        out.append(InsRenderToAsm(ins))
    return out


def FunRenderToAsm(fun: ir.Fun) -> List[str]:
    out = []
    reg_i = [x.name for x in fun.input_types]
    reg_o = [x.name for x in fun.output_types]

    out.append(
        f".fun {PREFIX + fun.name} {fun.kind.name} [{' '.join(reg_o)}] = [{' '.join(reg_i)}]")
    if fun.cpu_live_in:
        out.append(f"# live_in: [{' '.join(r.name for r in fun.cpu_live_in)}]")
    if fun.cpu_live_out:
        out.append(f"# live_out: [{' '.join(r.name for r in fun.cpu_live_out)}]")
    if fun.cpu_live_clobber:
        out.append(f"# live_clobber: [{' '.join(r.name for r in fun.cpu_live_clobber)}]")
    regs: Dict[int, List[str]] = collections.defaultdict(list)
    for r in fun.regs:
        regs[r.kind.value].append(r.name)
    for kind, rr in sorted(regs.items()):
        out.append(f".reg {o.DK(kind).name} [{' '.join(sorted(rr))}]")
    for _, stk in sorted(fun.stk_syms.items()):
        out.append(f".stk {stk.name} {stk.alignment} {stk.count}")

    for jtb in fun.jtbs:
        t = [f"{k} {v.name}" for k, v in sorted(jtb.bbl_tab.items())]
        out.append(f".jtb {jtb.name} {jtb.size} {jtb.def_bbl.name} [{' '.join(t)}]")
    for bbl in fun.bbls:
        out += BblRenderToAsm(bbl)
    return out


def UnitRenderToASM(unit: ir.Unit) -> List[str]:
    out = []
    # out.append("## NUM")
    # for num in mod.num_syms.values():
    #    out.append(f".num {num.name} {num.kind[3:]} {num.value}")
    for mem in unit.mems:
        out += MemRenderToAsm(mem)

    for fun in unit.funs:
        out += [""]
        out += FunRenderToAsm(fun)
    return out


############################################################
# Directives
############################################################
class ParseError(Exception):
    pass


def DirFun(unit: ir.Unit, operands: List):
    name, kind, output_types, input_types = operands
    if len(input_types) > o.MAX_PARAMETERS or len(output_types) > o.MAX_PARAMETERS:
        raise ParseError(f"parameter list too long {name}")
    fun = unit.GetFun(name)
    if fun is None:
        fun = ir.Fun(name, kind, output_types, input_types)
        unit.AddFun(fun)
    elif fun.forward_declared:
        unit.InitForwardDeclaredFun(fun, kind, output_types, input_types)
    else:
        raise ParseError(f"duplicate Fun {name}")


def DirBbl(unit: ir.Unit, operands: List):
    name = operands[0]
    fun = unit.funs[-1]
    bbl = fun.GetBbl(name)
    if bbl is None:
        bbl = ir.Bbl(name)
        fun.AddBbl(bbl)
    elif bbl.forward_declared:
        fun.InitForwardDeclaredBbl(bbl)
    else:
        raise ParseError(f"duplicate Bbl {name}")


def DirReg(unit: ir.Unit, operands: List):
    fun = unit.funs[-1]
    reg_list = operands[1]
    assert isinstance(reg_list, list)
    for r in reg_list:
        fun.AddReg(ir.Reg(r, operands[0]))


def DirStk(unit: ir.Unit, operands: List):
    fun = unit.funs[-1]
    name, alignment, count = operands
    fun.AddStk(ir.Stk(name, alignment, count))


def DirMem(unit: ir.Unit, operands: List):
    unit.AddMem(ir.Mem(*operands))


def DirData(unit: ir.Unit, operands: List):
    unit.AddData(ir.DataBytes(*operands))


def DirAddrFun(unit: ir.Unit, operands: List):
    unit.AddData(ir.DataAddrFun(*operands))


def DirAddrMem(unit: ir.Unit, operands: List):
    unit.AddData(ir.DataAddrMem(*operands))


# TODO: remove ugly globals
# gCurrentStructName = ""
# gCurrentStructOffset = 0
# gCurrentStructAlignment = 0
#
#
# def align(x, alignment):
#     return (x + alignment - 1) // alignment * alignment
#
#
# def DirStruct(_mod: ir.Unit, operands: List):
#     global gCurrentStructName, gCurrentStructOffset, gCurrentStructAlignment
#     assert not gCurrentStructName
#     gCurrentStructName = operands[0]
#     gCurrentStructOffset = 0
#     gCurrentStructAlignment = 0
#
#
# def DirEndStruct(unit: ir.Unit, _operands: List):
#     global gCurrentStructName, gCurrentStructOffset, gCurrentStructAlignment
#     assert gCurrentStructName
#     gCurrentStructOffset = align(gCurrentStructOffset, gCurrentStructAlignment)
#     unit.AddNum(ir.Num(f"{gCurrentStructName}.sizeof", o.NumKind.POS,
#                        gCurrentStructOffset))
#     unit.AddNum(ir.Num(f"{gCurrentStructName}.alignment", o.NumKind.POS,
#                        gCurrentStructAlignment))
#     gCurrentStructName = ""
#
#
# def DirField(mod: ir.Unit, operands: List):
#     global gCurrentStructName, gCurrentStructOffset, gCurrentStructAlignment
#     assert gCurrentStructName
#     alignment = operands[1].value
#     size = operands[2].value
#     gCurrentStructOffset = align(gCurrentStructOffset, alignment)
#     mod.AddNum(ir.Num(f"{gCurrentStructName}.{operands[0]}",
#                       o.NumKind.POS, gCurrentStructOffset))
#     gCurrentStructOffset += size
#     if alignment > gCurrentStructAlignment:
#         gCurrentStructAlignment = alignment


def DirJtb(unit: ir.Unit, operands: List):
    fun = unit.funs[-1]
    name, size, def_bbl, tab = operands
    fun.AddJtb(ir.Jtb(name, def_bbl, tab, size))


DIR_DISPATCHER = {
    ".fun": DirFun,
    ".bbl": DirBbl,
    ".jtb": DirJtb,
    ".reg": DirReg,
    ".stk": DirStk,
    ".mem": DirMem,
    ".data": DirData,
    ".addr.fun": DirAddrFun,
    ".addr.mem": DirAddrMem,
    # ".struct": DirStruct,
    # ".field": DirField,
    # ".endstruct": DirEndStruct,
}


def ExtractBblTable(fun: ir.Fun, lst: List) -> Dict[int, ir.Bbl]:
    assert len(lst) % 2 == 0
    it = iter(lst)
    out = {}
    for num_str in it:
        bbl_name = next(it)
        out[int(num_str)] = fun.GetBblOrAddForwardDeclaration(bbl_name)
    return out


_STRUCT_FMT = {
    "u8": "<B",
    "s8": "<b",
    "u16": "<H",
    "s16": "<h",
    "u32": "<I",
    "s32": "<i",
    "u64": "<Q",
    "s64": "<q",
    "f32": "<f",
    "f64": "<d",
}


def ExtractBytes(v) -> bytes:
    if isinstance(v, list):
        return b"".join(ExtractBytes(x) for x in v)

    if v[0] == '"':
        assert '"' == v[-1]
        return parse.EscapedStringToBytes(v[1:-1])
    else:
        num = v.split(":")
        if len(num) == 1:
            num.append("u8")
        fmt = _STRUCT_FMT.get(num[1])
        if num[1][0] == "f":
            val = float(num[0])
        else:
            val = int(num[0])
        return struct.pack(fmt, val)


def _GetRegOrConstOperand(fun: ir.Fun, last_kind: o.DK,
                          ok: o.OP_KIND, tc: o.TC,
                          token: str, regs_cpu: Dict[str, ir.Reg]) -> Any:
    if ok == o.OP_KIND.REG_OR_CONST:
        ok = o.OP_KIND.CONST if parse.IsLikelyConst(token) else o.OP_KIND.REG

    if ok is o.OP_KIND.REG:
        cpu_reg = None
        pos = token.find("@")
        if pos > 0:
            cpu_reg = regs_cpu.get(token[pos + 1:])
            assert cpu_reg is not None, f"unknown cpu_reg {token[pos + 1:]} known regs {regs_cpu.keys()}"
            token = token[:pos]
        pos = token.find(":")
        if pos < 0:
            reg = fun.GetReg(token)
        else:
            kind = token[pos + 1:]
            reg_name = token[:pos]
            reg = ir.Reg(reg_name, o.SHORT_STR_TO_RK.get(kind))
            fun.AddReg(reg)
            assert o.CheckTypeConstraint(last_kind, tc, reg.kind)
        if cpu_reg:
            if reg.cpu_reg:
                assert reg.cpu_reg == cpu_reg
            else:
                reg.cpu_reg = cpu_reg
        return reg

    else:
        pos = token.find(":")
        if pos >= 0:
            kind = token[pos + 1:]
            value_str = token[:pos]
            const = ir.ParseConst(value_str, o.SHORT_STR_TO_RK.get(kind))
            return const
        elif tc == o.TC.SAME_AS_PREV:
            const = ir.ParseConst(token, last_kind)
            return const
        elif tc == o.TC.OFFSET:
            const = ir.ParseOffsetConst(token)
            return const
        elif tc == o.TC.UINT:
            assert token[0] != "-"
            const = ir.ParseOffsetConst(token)
            return const
        else:
            assert False, f"cannot deduce type for const {token} [{tc}]"


def _GetOperand(unit: ir.Unit, fun: ir.Fun, ok: o.OP_KIND, v: Any) -> Any:
    if ok in o.OKS_LIST:
        assert isinstance(
            v, list) or v[0] == v[-1] == '"', f"operand {ok}: [{v}]"
    else:
        assert isinstance(v, str), f"bad operand {v} of type [{ok}]"

    if ok is o.OP_KIND.TYPE_LIST:
        out = []
        for kind_name in v:
            kind = o.SHORT_STR_TO_RK.get(kind_name)
            assert kind is not None, f"bad kind name [{kind_name}]"
            out.append(kind)
        return out
    elif ok is o.OP_KIND.FUN:
        return unit.GetFunOrAddForwardDeclaration(v)
    elif ok is o.OP_KIND.BBL:
        return fun.GetBblOrAddForwardDeclaration(v)
    elif ok is o.OP_KIND.BBL_TAB:
        return ExtractBblTable(fun, v)
    elif ok is o.OP_KIND.MEM:
        return unit.GetMem(v)
    elif ok is o.OP_KIND.STK:
        return fun.GetStk(v)
    elif ok is o.OP_KIND.FUN_KIND:
        return o.SHORT_STR_TO_FK[v]
    elif ok is o.OP_KIND.DATA_KIND:
        rk = o.SHORT_STR_TO_RK.get(v)
        assert rk is not None, f"bad kind name [{v}]"
        return rk
    elif ok is o.OP_KIND.NAME:
        assert parse.RE_IDENTIFIER.match(v), f"bad identifier [{v}]"
        return v
    elif ok is o.OP_KIND.NAME_LIST:
        for x in v:
            assert parse.RE_IDENTIFIER.match(x), f"bad identifier [{x}]"
        return v
    elif ok is o.OP_KIND.MEM_KIND:
        return o.SHORT_STR_TO_MK[v]
    elif ok is o.OP_KIND.VALUE:
        return v
    elif ok is o.OP_KIND.BYTES:
        return ExtractBytes(v)
    elif ok is o.OP_KIND.JTB:
        return fun.GetJbl(v)
    else:
        raise ir.ParseError(f"cannot read op type: {ok}")


def RetrieveActualOperands(unit: ir.Unit, fun: ir.Fun,
                           opc: o.Opcode, token: List, regs_cpu: Dict[str, ir.Reg]):
    out = []
    assert len(opc.operand_kinds) == len(token) - 1
    last_type: o.DK = o.DK.INVALID
    for ok, tc, token in zip(opc.operand_kinds, opc.constraints, token[1:]):
        if ok in {o.OP_KIND.REG_OR_CONST, o.OP_KIND.REG, o.OP_KIND.CONST}:
            assert isinstance(token, str), f"bad operand {token} of type [{ok}]"
            x = _GetRegOrConstOperand(fun, last_type, ok, tc, token, regs_cpu)
            last_type = x.kind
        else:
            x = _GetOperand(unit, fun, ok, token)
        if x is None:
            raise ir.ParseError(f"cannot read  [{ok}] in ops: {token}")
        out.append(x)
    return out


def ProcessLine(token: List, unit: ir.Unit, fun: Optional[ir.Fun], cpu_regs: Dict[str, ir.Reg]):
    opc = o.Opcode.Table.get(token[0])
    if not opc:
        raise ir.ParseError(f"unknown opcode/directive: {token}")
    if opc == o.LEA:
        if token[2] in fun.reg_syms:
            pass  # in case the register name is shadows a global
        elif token[2] in unit.fun_syms:
            opc = o.LEA_FUN
        elif token[2] in unit.mem_syms:
            opc = o.LEA_MEM
        elif token[2] in fun.stk_syms:
            opc = o.LEA_STK

        if opc != o.LEA_FUN and len(token) < 4:
            token.append("0")
    if len(token) - 1 != len(opc.operand_kinds):
        raise ir.ParseError("operand number %d mismatch: %s" % (
            len(opc.operand_kinds), token))

    if token[0].startswith("."):
        operands = RetrieveActualOperands(unit, fun, opc, token, {})
        directive = DIR_DISPATCHER[token[0]]
        directive(unit, operands)

    else:
        assert fun is not None
        operands = RetrieveActualOperands(unit, fun, opc, token, cpu_regs)
        assert fun.bbls, f"no bbl specified to contain instruction"
        bbl = fun.bbls[-1]
        ins = ir.Ins(opc, operands)
        bbl.AddIns(ins)
        sanity.InsCheckConstraints(ins)


def UnitParseFromAsm(fin, verbose=False, cpu_regs: Dict[str, ir.CpuReg] = {}) -> ir.Unit:
    out = ir.Unit("module")
    for line_num, line in enumerate(fin):
        fun = None if len(out.funs) == 0 else out.funs[-1]

        # print ("@@@", line[:-1])
        token_raw = parse.ParseLine(line)
        token = []
        in_list = False
        for t in token_raw:
            if t.startswith("#"):
                break
            elif t == "]":
                in_list = False
            elif t == "[":
                in_list = True
                token.append([])
            elif in_list:
                token[-1].append(t)
            else:
                token.append(t)
        if not token:
            continue
        if verbose:
            print(token)
        try:
            ProcessLine(token, out, fun, cpu_regs)
        except Exception as err:
            raise ParseError(
                f"UnitParseFromAsm error in line {line_num}:\n{line}\n{token}\n{err}")

    for fun in out.funs:
        assert not fun.forward_declared
        for bbl in fun.bbls:
            assert not bbl.forward_declared
    return out


def SynthesizeBenchmark(unit: ir.Unit, repeats: int):
    """Re-emits a given asm file multiple times with different prefices

    This is useful to for generating really large programs for benchmarking the
    compiler speed
    """
    global PREFIX
    for i in range(repeats):
        PREFIX = f"a{i:03d}_"
        print("\n".join(UnitRenderToASM(unit)))


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        unit = UnitParseFromAsm(sys.stdin)
        SynthesizeBenchmark(unit, int(sys.argv[1]))
        sys.exit(1)

    def process(fin):
        unit = UnitParseFromAsm(fin)
        # for fun in unit.funs:
        #    sanity.FunCheck(fun, unit, False, True, True)
        print("\n".join(UnitRenderToASM(unit)))


    process(sys.stdin)
