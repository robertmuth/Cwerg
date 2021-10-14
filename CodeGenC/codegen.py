#!/usr/bin/python3

"""Emulator for IR"""

from typing import List
import sys

from Base import ir
from Base import opcode_tab as o
from Base import serialize
from Base import sanity

KIND_MAP = {
    o.DK.S8: "int8_t",
    o.DK.S16: "int16_t",
    o.DK.S32: "int32_t",
    o.DK.S64: "int64_t",

    o.DK.U8: "uint8_t",
    o.DK.U16: "uint16_t",
    o.DK.U32: "uint32_t",
    o.DK.U64: "uint64_t",

    o.DK.F32: "float",
    o.DK.F64: "double",

    o.DK.A32: "void*",  # hack
    o.DK.A64: "void*",  # hack

    o.DK.C32: "FUN_POINTER",  # hack
    o.DK.C64: "FUN_POINTER",  # hack

}


def MangleFun(fun):
    if fun.kind is o.FUN_KIND.BUILTIN or fun.name == "main":
        return fun.name
    return "A_" + fun.name


def FunOutputStructName(fun):
    return MangleFun(fun) + "_output"


def MangleReg(reg):
    return reg.name.replace("%", "L_")


def RegType(reg):
    return KIND_MAP[reg.kind]


def MangleBbl(bbl: ir.Bbl):
    return bbl.name.replace("%", "B_")


def MangleMem(mem: ir.Mem):
    return mem.name.replace("%", "M_")


def MangleStk(stk: ir.Stk):
    return stk.name.replace("%", "S_")


COMPARE_COND_BRA = {
    "beq": "==",
    "bne": "!=",
    "blt": "<",
    "ble": "<=",
}

COMPARE_CMP = {
    "cmpeq": "==",
    "cmplt": "<",
}


def RegOrNum(_fun, op) -> str:
    if isinstance(op, ir.Reg):
        return MangleReg(op)
    else:
        assert isinstance(op, ir.Const)
        if op.kind in {o.DK.S64, o.DK.U64}:
            return f"{op.value}LL"
        return f"{op.value}"


def Handle_COND_BRA(fun, opcode, ops, _ctx):
    left = RegOrNum(fun, ops[0])
    right = RegOrNum(fun, ops[1])
    op = COMPARE_COND_BRA[opcode.name]
    print(f"    if ({left} {op} {right})  goto {MangleBbl(ops[2])};")


def Handle_CMP(fun, opcode, ops, _ctx):
    dst = RegOrNum(fun, ops[0])
    left = RegOrNum(fun, ops[3])
    op = COMPARE_CMP[opcode.name]
    right = RegOrNum(fun, ops[4])
    val_t = RegOrNum(fun, ops[1])
    val_f = RegOrNum(fun, ops[2])
    print(f"    {dst} = ({left} {op} {right})  ? {val_t} : {val_f};")


def Handle_BRA(_fun, _opcode, ops: List, _ctx):
    print(f"    goto {MangleBbl(ops[0])};")


def Handle_RET(fun: ir.Fun, _, _ops: List, ctx):
    results: List = ctx["pushes"]
    if len(results) == 0:
        print(f"    return;")
    elif len(results) == 1:
        print(f"    return {RegOrNum(fun, results[0])};")
    else:
        for n, r in enumerate(reversed(results)):
            print(f"    L_out.output{n} = {RegOrNum(fun, r)};")
        print(f"    return L_out;")
    results.clear()


def Handle_MOV(fun: ir.Fun, _opcode, ops: List, _ctx):
    print(f"    {RegOrNum(fun, ops[0])} = {RegOrNum(fun, ops[1])};")


ALU_INT = {
    o.SUB: "{src1} - {src2}",
    o.ADD: "{src1} + {src2}",
    o.AND: "{src1} & {src2}",
    o.OR: "{src1} | {src2}",
    o.XOR: "{src1} ^ {src2}",
    #

    # need masking for shifts
    o.SHL: "{src1} << ({src2} & {mask})",
    o.SHR: "{src1} >> ({src2} & {mask})",
    o.MUL: "{src1} * {src2}",
    # needs div by zero handling
    o.DIV: "{src1} / {src2}",
    o.REM: "{src1} % {src2}",
    # TODO: many missing
}

ALU_FLT = {
    o.SUB: "{src1} - {src2}",
    o.ADD: "{src1} + {src2}",
    o.MUL: "{src1} * {src2}",
    o.DIV: "{src1} / {src2}",
    o.REM: "fmod({src1}, {src2})",
    o.COPYSIGN: "copysign({src1}, {src2})",
}


def Handle_ALU(fun, opcode, ops, _ctx):
    dst_flavor = ops[0].kind.flavor()
    if dst_flavor in {o.DK_FLAVOR_S, o.DK_FLAVOR_U}:
        expr = ALU_INT[opcode]
    elif dst_flavor is o.DK_FLAVOR_F:
        expr = ALU_FLT[opcode]
    else:
        assert False, dst_flavor
    shift_mask = ops[0].kind.bitwidth() - 1
    computation = expr.format(
        src1=RegOrNum(fun, ops[1]), src2=RegOrNum(fun, ops[2]), mask=shift_mask)
    print(f"    {RegOrNum(fun, ops[0])} = {computation};")


ALU1_INT = {
    (o.CNTLZ, 8): "({src} == 0) ? 8 : __builtin_clz({src} & 0xff) - 24",
    (o.CNTLZ, 16): "({src} == 0) ? 16 : __builtin_clz({src} & 0xffff) - 16",
    (o.CNTLZ, 32): "({src} == 0) ? 32 : __builtin_clz({src} & 0xffffffff)",
    (o.CNTTZ, 8): "({src} == 0) ? 8:  __builtin_ctz({src} & 0xff)",
    (o.CNTTZ, 16): "({src} == 0) ? 16:  __builtin_ctz({src} & 0xffff)",
    (o.CNTTZ, 32): "({src} == 0) ? 32:  __builtin_ctz({src} & 0xffffffff)",

}

ALU1_FLT = {
}


def Handle_ALU1(fun, opcode, ops, _ctx):
    dst_flavor = ops[0].kind.flavor()
    if dst_flavor in {o.DK_FLAVOR_S, o.DK_FLAVOR_U}:
        expr = ALU1_INT[(opcode, ops[1].kind.bitwidth())]
    elif dst_flavor is o.DK_FLAVOR_F:
        expr = ALU1_FLT[opcode]
    else:
        assert False, dst_flavor
    computation = expr.format(src=RegOrNum(fun, ops[1]))

    print(f"    {RegOrNum(fun, ops[0])} = {computation};")


def EmitCall(target, caller, target_expr, ctx):
    name = MangleFun(target)
    n = len(target.output_types)
    if n == 0:
        assignee = ""
    elif n == 1:
        assignee = f"{name}_result"
    else:
        assignee = f"{name}_results"

    if assignee:
        if target.name not in ctx["seen_funs"]:
            ctx["seen_funs"].add(target.name)
            if n == 1:
                type_name = KIND_MAP[target.output_types[0]]
            else:
                type_name = f"struct {MangleFun(target)}_output"
            print(f"    {type_name} {assignee};")
        print(f"    {assignee} = {target_expr} (", end="")
    else:
        print(f"    {target_expr} (")

    sep = ""
    for r in reversed(ctx["pushes"]):
        print(f"{sep}{RegOrNum(caller, r)}", end="")
        sep = ", "
    print(");")
    ctx["pushes"].clear()
    if n == 1:
        ctx["pops"] = [assignee]
    elif n > 1:
        ctx["pops"] = [f"{assignee}.output{n}"
                       for n, x in enumerate(target.output_types)]


def Handle_BSR(fun: ir.Fun, _, ops: List, ctx):
    target: ir.Fun = ops[0]
    assert target.kind != o.FUN_KIND.INVALID, f"call to undefined function {target.name}"
    EmitCall(target, fun, MangleFun(target), ctx)


def Handle_JSR(fun: ir.Fun, _, ops: List, ctx):
    target: ir.Fun = ops[1]
    expr = f"({MangleReg(ops[0])})"
    EmitCall(target, fun, expr, ctx)


def Handle_LEA(fun: ir.Fun, opcode, ops: List, _ctx):
    if opcode is o.LEA:
        dst = RegOrNum(fun, ops[0])
        src1 = RegOrNum(fun, ops[1])
        src2 = RegOrNum(fun, ops[2])
        if src2 == "0":
            src2 = ""
        else:
            src2 = f" + {src2}"
        print(f"    {dst} = {src1}{src2};")
    elif opcode is o.LEA_FUN:
        print(
            f"    {RegOrNum(fun, ops[0])} = (FUN_POINTER)&{MangleFun(ops[1])};")
    else:
        dst = RegOrNum(fun, ops[0])
        base = ops[1]
        src2 = RegOrNum(fun, ops[2])
        if src2 == "0":
            src2 = ""
        else:
            src2 = f" + {src2}"
        if isinstance(base, ir.Mem) and base.kind == o.MEM_KIND.FIX:
            print(f"    {dst} = ((char*) {base.alignment}){src2};")

        else:
            print(f"    {dst} = ((char*)&{ops[1].name}){src2};")


def Handle_LD(fun: ir.Fun, _, ops: List, _ctx):
    base = ops[1]
    if isinstance(base, ir.Mem):
        base = "&" + MangleMem(base)
    elif isinstance(base, ir.Stk):
        base = "&" + MangleStk(base)
    elif isinstance(base, ir.Reg):
        base = MangleReg(base)
    else:
        assert False, base
    dst = RegOrNum(fun, ops[0])
    offset = RegOrNum(fun, ops[2])
    if offset != 0:
        offset = f" + {offset}"
    else:
        offset = ""
    print(f"    {dst} = *({RegType(ops[0])}*)(((char*){base}){offset});")


def Handle_ST(fun: ir.Fun, _, ops: List, _ctx):
    base = ops[0]
    if isinstance(base, ir.Mem):
        base = "&" + MangleMem(base)
    elif isinstance(base, ir.Stk):
        base = "&" + MangleStk(base)
    elif isinstance(base, ir.Reg):
        base = MangleReg(base)
    else:
        assert False, base
    offset = RegOrNum(fun, ops[1])
    if offset != 0:
        offset = f" + {offset}"
    else:
        offset = ""
    src = RegOrNum(fun, ops[2])
    print(f"    *({RegType(ops[2])}*)(((char*){base}){offset}) = {src};")


def Handle_SWITCH(fun: ir.Fun, _, ops: List, _ctx):
    jtb = ops[1]
    assert isinstance(jtb, ir.Jtb)
    print(f"    switch ({RegOrNum(fun, ops[0])})" + " {")
    print(f"    default: goto {jtb.def_bbl.name};")
    for k, v in jtb.bbl_tab.items():
        print(f"    case {k}: goto {v.name};")

    print("    }")


def Handle_CONV(_fun: ir.Fun, _, ops: List, _ctx):
    print(
        f"    {MangleReg(ops[0])} = ({RegType(ops[0])}) {RegOrNum(_fun, ops[1])};")


def Handle_POPARG(_fun: ir.Fun, _, ops: List, ctx):
    src = ctx["pops"].pop(0)
    print(f"    {MangleReg(ops[0])} = {src};")


def Handle_PUSHARG(_fun: ir.Fun, _, ops: List, ctx):
    ctx["pushes"].append(ops[0])


INS_HANDLER = {
    o.OPC_KIND.COND_BRA: Handle_COND_BRA,
    o.OPC_KIND.BRA: Handle_BRA,
    o.OPC_KIND.CMP: Handle_CMP,

    o.OPC_KIND.BSR: Handle_BSR,
    o.OPC_KIND.JSR: Handle_JSR,

    o.OPC_KIND.RET: Handle_RET,
    o.OPC_KIND.MOV: Handle_MOV,
    o.OPC_KIND.ALU: Handle_ALU,
    o.OPC_KIND.ALU1: Handle_ALU1,
    o.OPC_KIND.LEA: Handle_LEA,
    o.OPC_KIND.LEA1: Handle_LEA,
    o.OPC_KIND.LD: Handle_LD,
    o.OPC_KIND.ST: Handle_ST,
    o.OPC_KIND.SWITCH: Handle_SWITCH,
    o.OPC_KIND.CONV: Handle_CONV,
    o.OPC_KIND.POPARG: Handle_POPARG,
    o.OPC_KIND.PUSHARG: Handle_PUSHARG,
}

PROLOG = """
#include "std_types.h"

typedef void (*FUN_POINTER)(void);

#define MIN(a, b) a < b ? a : b
"""

EPILOG = """
"""


def Alignment(x):
    if x == 0:
        return ""
    return f"__attribute__ ((aligned ({x})))"


def IsAllZeros(datas):
    for d in datas:
        if isinstance(d, ir.DataBytes):
            for b in d.data:
                if b != 0:
                    return False
        elif isinstance(d, ir.DataAddrFun):
            return False
        elif isinstance(d, ir.DataAddrMem):
            return False
        else:
            assert False
    return True


def EmitMemory(mem: ir.Mem):
    print("struct {")
    for n, d in enumerate(mem.datas):
        if isinstance(d, ir.DataBytes):
            print(f"    char X_{n}[{d.size}];")
        elif isinstance(d, ir.DataAddrFun):
            # we cheat and ignore the size field
            print(f"    FUN_POINTER X_{n};")
        elif isinstance(d, ir.DataAddrMem):
            # we cheat and ignore the size field
            print(f"    char* X_{n};")
        else:
            assert False, d
    print("} " + f"{Alignment(mem.alignment)} {MangleMem(mem)}", end="")
    if IsAllZeros(mem.datas):
        print(";\n")
        return

    print("= " + "{")
    sep = ""
    for n, d in enumerate(mem.datas):
        if isinstance(d, ir.DataBytes):
            print(f'    {sep}{serialize.EscapeCStyle(d.data * d.count, 30)}')
        elif isinstance(d, ir.DataAddrFun):
            print(f'    {sep}(FUN_POINTER)&{MangleFun(d.fun)}')
        elif isinstance(d, ir.DataAddrMem):
            print(f'    {sep}((char*)&{MangleMem(d.mem)}) + {d.offset}')
        else:
            assert False, d
        sep = ","
    print("};\n")


def EmitFunctionProto(fun, include_output_struct):
    name = MangleFun(fun)

    if len(fun.output_types) == 0:
        return_type = "void"
    elif len(fun.output_types) == 1:
        return_type = KIND_MAP[fun.output_types[0]]
    else:
        if include_output_struct:
            print(f"struct {FunOutputStructName(fun)}" + " {")
            for n, r in enumerate(fun.output_types):
                print(f"    {KIND_MAP[r]} output{n};")
            print("};")
            print("")
        return_type = f"struct {FunOutputStructName(fun)}"

    print(f"{return_type} {name} (", end="")
    sep = ""
    for n, r in enumerate(fun.input_types):
        print(f"{sep}{KIND_MAP[r]} input{n}", end="")
        sep = ", "
    print(")")
    return return_type


def EmitFunction(fun: ir.Fun):
    return_type = EmitFunctionProto(fun, False)
    name = MangleFun(fun)
    print("{")
    # result decls
    if len(fun.output_types) > 1:
        print(f"    struct {name}_output L_out;")
    for r in fun.regs:
        print(f"    {RegType(r)} {MangleReg(r)};")

    # stack decls
    for _, stk in sorted(fun.stk_syms.items()):
        print(
            f"    char {MangleStk(stk)}[{stk.count}] {Alignment(stk.alignment)};")

    ctx = {
        "pops": [],
        "pushes": [],
        "seen_funs": set(),
    }
    # now emit the actual code
    for b in fun.bbls:
        ctx["pops"].clear()
        if b == fun.bbls[0]:
            ctx["pops"] = [f"input{i}"
                           for i in range(len(fun.input_types))]
        ctx["pushes"].clear()
        print(f"{MangleBbl(b)}: ;")
        for i in b.inss:
            handler = INS_HANDLER.get(i.opcode.kind)
            if handler:
                handler(fun, i.opcode, i.operands, ctx)
            else:
                assert False, f"no handler for {i.opcode.name} cat: {i.opcode.kind}"
    print("}")
    print("\n")


if __name__ == "__main__":
    import argparse


    def main():
        parser = argparse.ArgumentParser(description='CodeGenC')
        parser.add_argument('--trace', action='store_const',
                            const=True, default=False,
                            help='show info after every step')
        parser.add_argument('--debug_parser', action='store_const',
                            const=True, default=False,
                            help='dump module before starting execution')
        parser.add_argument('filename', type=str,
                            help='file to execute')
        args = parser.parse_args()
        if args.filename == "-":
            fin = sys.stdin
        else:
            fin = open(args.filename)
        unit = serialize.UnitParseFromAsm(fin, args.debug_parser)
        assert "main" in unit.fun_syms
        print(PROLOG)
        for fun in unit.funs:
            if fun.kind is o.FUN_KIND.BUILTIN:
                continue
            sanity.FunCheck(fun, unit, check_push_pop=True, check_cfg=False)
            EmitFunctionProto(fun, True)
            print(";")
        for mem in unit.mems:
            EmitMemory(mem)
        for fun in unit.funs:
            if fun.kind is o.FUN_KIND.BUILTIN:
                continue
            EmitFunction(fun)
        print(EPILOG)


    main()
