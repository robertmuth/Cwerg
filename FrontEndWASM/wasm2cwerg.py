#!/usr/bin/python3

"""
Convert WASM files to Cwerg
"""

import logging
import io
import typing
import enum
import dataclasses
from FrontEndWASM import opcode_tab as wasm_opc
import FrontEndWASM.parser as wasm
from Base import ir
from Base import opcode_tab as o
from Base import serialize
from Base import sanity

ZERO = ir.Const(o.DK.U32, 0)
ONE = ir.Const(o.DK.U32, 1)

PAGE_SIZE = 64 * 1024

WASI_FUNCTIONS = {
    "$wasi_unstable$fd_write",
}


def ExtractBytesFromConstIns(wasm_ins: wasm.Instruction, val_type: wasm.NUM_TYPE):
    o = wasm_ins.opcode
    v = wasm_ins.args[0]
    if o is wasm_opc.I32_CONST:
        return v.to_bytes(4, 'little')
    elif o is wasm_opc.I64_CONST:
        return v.to_bytes(8, 'little')
    elif o is wasm_opc.F32_CONST or o is wasm_opc.F64_CONST:
        assert isinstance(v, bytes)
        return v
    else:
        assert False, f"unexpected instruction {wasm_ins}"


def GenerateMemcopyFun(unit: ir.Unit, addr_type: o.DK) -> ir.Fun:
    fun = unit.AddFun(ir.Fun("$memcpy", o.FUN_KIND.NORMAL, [], [addr_type, addr_type, o.DK.U32]))
    dst = fun.AddReg(ir.Reg("dst", addr_type))
    src = fun.AddReg(ir.Reg("src", addr_type))
    cnt = fun.AddReg(ir.Reg("cnt", o.DK.U32))
    data = fun.AddReg(ir.Reg("data", o.DK.U8))

    prolog = fun.AddBbl(ir.Bbl("prolog"))
    loop = fun.AddBbl(ir.Bbl("loop"))
    epilog = fun.AddBbl(ir.Bbl("epilog"))

    prolog.AddIns(ir.Ins(o.POPARG, [dst]))
    prolog.AddIns(ir.Ins(o.POPARG, [src]))
    prolog.AddIns(ir.Ins(o.POPARG, [cnt]))
    prolog.AddIns(ir.Ins(o.BRA, [epilog]))

    loop.AddIns(ir.Ins(o.SUB, [cnt, cnt, ONE]))
    loop.AddIns(ir.Ins(o.LD, [data, src, cnt]))
    loop.AddIns(ir.Ins(o.ST, [dst, cnt, data]))

    epilog.AddIns(ir.Ins(o.BLT, [ZERO, cnt, loop]))
    epilog.AddIns(ir.Ins(o.RET, []))
    return fun


def GenerateInitGlobalVarsFun(mod: wasm.Module, unit: ir.Unit, addr_type: o.DK) -> ir.Fun:
    fun = unit.AddFun(ir.Fun("init_global_vars_fun", o.FUN_KIND.NORMAL, [], []))
    bbl = fun.AddBbl(ir.Bbl("start"))
    epilog = fun.AddBbl(ir.Bbl("end"))
    epilog.AddIns(ir.Ins(o.RET, []))

    section = mod.sections.get(wasm.SECTION_ID.GLOBAL)
    if not section:
        return fun
    val32 = fun.AddReg(ir.Reg("val32", o.DK.U32))
    val64 = fun.AddReg(ir.Reg("val64", o.DK.U64))
    for n, data in enumerate(section.items):
        print(data)
        kind = o.MEM_KIND.RO if data.global_type.mut is wasm.MUT.CONST else o.MEM_KIND.RW
        mem = unit.AddMem(ir.Mem(f"global_vars_{n}", ir.Const(o.DK.U32, 16), kind))
        assert len(data.expr.instructions) == 1
        ins = data.expr.instructions[0]
        var_type = data.global_type.value_type
        if ins.opcode is wasm_opc.GLOBAL_GET:
            mem.AddData(ir.DataBytes(ONE, b"\0" * (4 if var_type.is_32bit() else 8)))
            src_mem = unit.GetMem(f"global_vars_{int(ins.args[0])}")
            reg = val32 if var_type.is_32bit() else val64
            bbl.AddIns(ir.Ins(o.LD_MEM, [reg, src_mem, ZERO]))
            bbl.AddIns(ir.Ins(o.ST_MEM, [mem, ZERO, reg]))
        elif wasm_opc.FLAGS.CONST in ins.opcode.flags:
            mem.AddData(ir.DataBytes(ONE, ExtractBytesFromConstIns(ins, var_type)))
        else:
            assert False, f"unsupported init instructions {ins}"
    return fun


def GenerateInitDataFun(mod: wasm.Module, unit: ir.Unit, global_mem_base: ir.Mem,
                        memcpy: ir.Fun, addr_type: o.DK) -> ir.Fun:
    fun = unit.AddFun(ir.Fun("init_data_fun", o.FUN_KIND.NORMAL, [], []))
    bbl = fun.AddBbl(ir.Bbl("start"))
    epilog = fun.AddBbl(ir.Bbl("end"))
    epilog.AddIns(ir.Ins(o.RET, []))
    section = mod.sections.get(wasm.SECTION_ID.DATA)
    if not section:
        return
    mem_base = fun.AddReg(ir.Reg("mem_base", addr_type))
    offset = fun.AddReg(ir.Reg("offset", o.DK.S32))
    src = fun.AddReg(ir.Reg("src", addr_type))
    dst = fun.AddReg(ir.Reg("dst", addr_type))

    bbl.AddIns(ir.Ins(o.LD_MEM, [mem_base, global_mem_base, ZERO]))

    for n, data in enumerate(section.items):
        assert data.memory_index == 0
        assert isinstance(data.offset, wasm.Expression)
        assert len(data.offset.instructions) == 1
        init = unit.AddMem(ir.Mem(f"global_init_mem_{n}", ir.Const(o.DK.U32, 16), o.MEM_KIND.RO))
        init.AddData(ir.DataBytes(ONE, data.init))
        ins = data.offset.instructions[0]
        if ins.opcode is wasm_opc.GLOBAL_GET:
            src_mem = unit.GetMem(f"global_vars_{int(ins.args[0])}")
            bbl.AddIns(ir.Ins(o.LD_MEM, [offset, src_mem, ZERO]))
        elif ins.opcode is wasm_opc.I32_CONST:
            bbl.AddIns(ir.Ins(o.MOV, [offset, ir.Const(o.DK.S32, ins.args[0])]))
        else:
            assert False, f"unsupported init instructions {ins}"
        bbl.AddIns(ir.Ins(o.LEA, [dst, mem_base, offset]))
        bbl.AddIns(ir.Ins(o.LEA_MEM, [src, init, ZERO]))
        bbl.AddIns(ir.Ins(o.PUSHARG, [ir.Const(o.DK.U32, len(data.init))]))
        bbl.AddIns(ir.Ins(o.PUSHARG, [src]))
        bbl.AddIns(ir.Ins(o.PUSHARG, [dst]))
        bbl.AddIns(ir.Ins(o.BSR, [memcpy]))
    return fun


OPC_TYPE_TO_CWERG_TYPE = {
    "i32": o.DK.S32,
    "i64": o.DK.S64,
    "f32": o.DK.F32,
    "f64": o.DK.F64,
}

WASM_TYPE_TO_CWERG_TYPE = {
    wasm.VAL_TYPE.I32: o.DK.S32,
    wasm.VAL_TYPE.I64: o.DK.S64,
    wasm.VAL_TYPE.F32: o.DK.F32,
    wasm.VAL_TYPE.F64: o.DK.F64,
}


def TranslateTypeList(result_type: wasm.ResultType) -> typing.List[o.DK]:
    return [WASM_TYPE_TO_CWERG_TYPE[x] for x in result_type.types]


def GenerateFun(unit: ir.Unit, mod: wasm.Module, wasm_fun: wasm.Function,
                global_mem_base, addr_type) -> ir.Fun:
    arguments = TranslateTypeList(wasm_fun.func_type.args)
    returns = TranslateTypeList(wasm_fun.func_type.rets)
    fun = unit.AddFun(ir.Fun(wasm_fun.name, o.FUN_KIND.NORMAL, arguments, returns))
    bbl = fun.AddBbl(ir.Bbl("start"))
    mem_base = fun.AddReg(ir.Reg("mem_base", addr_type))
    bbl.AddIns(ir.Ins(o.LD_MEM, [mem_base, global_mem_base, ZERO]))
    op_stack: typing.List[typing.Union[ir.Reg, ir.Const]] = []
    block_stack = []
    for wasm_ins in wasm_fun.impl.expr.instructions:
        opc = wasm_ins.opcode
        if wasm_opc.FLAGS.CONST in opc.flags:
            # breaks for floats
            val = wasm_ins.args[0]
            op_stack.append(ir.Const(OPC_TYPE_TO_CWERG_TYPE[opc.op_type], val))
        elif wasm_opc.FLAGS.STORE in opc.flags:
            val = op_stack.pop(-1)
            offset = op_stack.pop(-1)
            bbl.AddIns(ir.Ins(o.ST, [mem_base, offset, val]))
        elif opc is wasm_opc.DROP:
            op_stack.pop(-1)
        elif opc is wasm_opc.CALL:
            wasm_callee = mod.functions[int(wasm_ins.args[0])]
            callee = unit.GetFun(wasm_callee.name)
            for _ in range(len(callee.input_types) - 1):
                bbl.AddIns(ir.Ins(o.PUSHARG, [op_stack.pop(-1)]))
            if callee.kind is o.FUN_KIND.BUILTIN:
                bbl.AddIns(ir.Ins(o.PUSHARG, [mem_base]))
            bbl.AddIns(ir.Ins(o.BSR, [callee]))
            # TODO check order
            for dk in reversed(callee.output_types):
                reg_name = f"$op_{len(op_stack)}_{dk.name}"
                reg = fun.MaybeGetReg(reg_name)
                if not reg:
                    reg = fun.AddReg(ir.Reg(reg_name, dk))
                op_stack.append(reg)
                bbl.AddIns(ir.Ins(o.POPARG, [reg]))

        else:
            assert False, f"unsupported opcode {opc.name}"
    if op_stack:
        assert False
    assert not block_stack
    bbl.AddIns(ir.Ins(o.RET, []))
    return fun


def GenerateStartup(unit: ir.Unit, global_mem_base, main: ir.Fun, init_global: ir.Fun,
                    init_data: ir.Fun, initial_heap_size: int, addr_type: o.DK) -> ir.Fun:
    fun = unit.AddFun(ir.Fun("_start", o.FUN_KIND.NORMAL, [], []))
    addr = fun.AddReg(ir.Reg("addr", addr_type))

    xbrk = unit.AddFun(ir.Fun("xbrk", o.FUN_KIND.EXTERN, [addr_type], [addr_type]))
    exit = unit.AddFun(ir.Fun("exit", o.FUN_KIND.EXTERN, [], [o.DK.S32]))

    bbl = fun.AddBbl(ir.Bbl("start"))
    if initial_heap_size:
        bbl.AddIns(ir.Ins(o.PUSHARG, [ir.Const(addr_type, 0)]))
        bbl.AddIns(ir.Ins(o.BSR, [xbrk]))
        bbl.AddIns(ir.Ins(o.POPARG, [addr]))
        bbl.AddIns(ir.Ins(o.ST_MEM, [global_mem_base, ZERO, addr]))
        bbl.AddIns(ir.Ins(o.LEA, [addr, addr, ir.Const(o.DK.S32, initial_heap_size)]))
        bbl.AddIns(ir.Ins(o.PUSHARG, [addr]))
        bbl.AddIns(ir.Ins(o.BSR, [xbrk]))
        bbl.AddIns(ir.Ins(o.POPARG, [addr]))
        bbl.AddIns(ir.Ins(o.ST_MEM, [global_mem_base, ir.Const(o.DK.S32, addr_type.bitwidth()
                                                               // 8), addr]))

    bbl.AddIns(ir.Ins(o.BSR, [init_global]))
    bbl.AddIns(ir.Ins(o.BSR, [init_data]))
    bbl.AddIns(ir.Ins(o.BSR, [main]))
    bbl.AddIns(ir.Ins(o.PUSHARG, [ir.Const(o.DK.S32, 0)]))
    bbl.AddIns(ir.Ins(o.BSR, [exit]))
    # unreachable
    bbl.AddIns(ir.Ins(o.RET, []))
    return fun


def Translate(mod: wasm.Module, addr_type: o.DK) -> ir.Unit:
    bit_width = addr_type.bitwidth()
    unit = ir.Unit("unit")
    global_mem_base = unit.AddMem(ir.Mem("global_mem_base",
                                         ir.Const(o.DK.U32, 2 * bit_width // 8), o.MEM_KIND.RW))
    memcpy = GenerateMemcopyFun(unit, addr_type)
    init_global = GenerateInitGlobalVarsFun(mod, unit, addr_type)
    init_data = GenerateInitDataFun(mod, unit, global_mem_base, memcpy, addr_type)
    main = None
    for wasm_fun in mod.functions:
        if isinstance(wasm_fun.impl, wasm.Import):
            assert wasm_fun.name in WASI_FUNCTIONS, f"unimplemented external function: {wasm_fun.name}"
            arguments = [addr_type] + TranslateTypeList(wasm_fun.func_type.args)
            returns = TranslateTypeList(wasm_fun.func_type.rets)
            wasm_fun = unit.AddFun(ir.Fun(wasm_fun.name, o.FUN_KIND.BUILTIN, returns, arguments))
        else:
            assert isinstance(wasm_fun.impl, wasm.Code)
            if wasm_fun.name == "_start":
                wasm_fun = wasm.Function("$main", wasm_fun.func_type, wasm_fun.impl)
            fun = GenerateFun(unit, mod, wasm_fun, global_mem_base, addr_type)
            sanity.FunCheck(fun, unit)
            if wasm_fun.name == "$main":
                main = fun

    initial_heap_size = 0
    sec_memory = mod.sections.get(wasm.SECTION_ID.MEMORY)
    if sec_memory:
        assert len(sec_memory.items) == 1
        heap: wasm.Mem = sec_memory.items[0]
        initial_heap_size = heap.mem_type.limits.min
    assert main, f"missing main function"
    GenerateStartup(unit, global_mem_base, main, init_global, init_data,
                    initial_heap_size * PAGE_SIZE, addr_type)

    return unit


if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.DEBUG)
    logging.info(f"Reading {sys.argv[1]}")
    with open(sys.argv[1], "rb") as fin:
        unit = Translate(wasm.Module.read(fin), o.DK.A32)
        print("\n".join(serialize.UnitRenderToASM(unit)))
