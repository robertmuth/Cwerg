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
    "$wasi$fd_write",
    "$wasi$fd_read",
    "$wasi$fd_seek",
    "$wasi$fd_close",
    "$wasi$proc_exit",
    # pseudo (cwerg specific)
    "$wasi$print_i32_ln",
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
        assert len(data.offset.instructions) == 2
        assert data.offset.instructions[1].opcode is wasm_opc.END
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

WASM_CMP_TO_CWERG = {
    "eq": (o.BNE, False, False),
    "ne": (o.BNE, False, False),
    #
    "lt": (o.BLE, True, False),
    "lt_u": (o.BLE, True, True),
    "lt_s": (o.BLE, True, False),
    #
    "le": (o.BLT, True, False),
    "le_u": (o.BLT, True, True),
    "le_s": (o.BLT, True, False),
    #
    "gt": (o.BLE, False, False),
    "gt_u": (o.BLE, False, True),
    "gt_s": (o.BLE, False, False),
    #
    "ge": (o.BLT, False, False),
    "ge_u": (o.BLT, False, True),
    "ge_s": (o.BLT, False, False),
}

WASM_ALU_TO_CWERG = {
    "sub": o.SUB,
    "add": o.ADD,
    "mul": o.MUL,
    "div": o.DIV,
    "div_s": o.DIV,
    "div_u": o.DIV,
    "rem": o.REM,
    "rem_s": o.REM,
    "rem_u": o.REM,
}

def TranslateTypeList(result_type: wasm.ResultType) -> typing.List[o.DK]:
    return [WASM_TYPE_TO_CWERG_TYPE[x] for x in result_type.types]


def GenerateFun(unit: ir.Unit, mod: wasm.Module, wasm_fun: wasm.Function,
                global_mem_base, addr_type) -> ir.Fun:
    op_stack: typing.List[typing.Union[ir.Reg, ir.Const]] = []
    block_stack = []
    bbl_count = 0
    def GetOpReg(dk: o.DK, pos: int):
        reg_name = f"$op_{pos}_{dk.name}"
        reg = fun.MaybeGetReg(reg_name)
        return reg if reg else fun.AddReg(ir.Reg(reg_name, dk))

    def GetLocalReg(no: int):
        reg_name = f"$loc_{no}"
        reg = fun.MaybeGetReg(reg_name)
        assert reg, f"unknown reg {reg_name}"
        return reg

    arguments = TranslateTypeList(wasm_fun.func_type.args)
    returns = TranslateTypeList(wasm_fun.func_type.rets)
    fun = unit.AddFun(ir.Fun(wasm_fun.name, o.FUN_KIND.NORMAL, arguments, returns))
    bbl = fun.AddBbl(ir.Bbl("start"))
    for n, dk in enumerate(arguments):
        reg = fun.AddReg(ir.Reg(f"$loc_{n}", dk))
        bbl.AddIns(ir.Ins(o.POPARG, [reg]))

    mem_base = fun.AddReg(ir.Reg("mem_base", addr_type))
    bbl.AddIns(ir.Ins(o.LD_MEM, [mem_base, global_mem_base, ZERO]))

    for n, wasm_ins in enumerate(wasm_fun.impl.expr.instructions):
        opc = wasm_ins.opcode
        args = wasm_ins.args
        if opc.kind is wasm_opc.OPC_KIND.CONST:
            # breaks for floats
            op_stack.append(ir.Const(OPC_TYPE_TO_CWERG_TYPE[opc.op_type], args[0]))
        elif opc.kind is wasm_opc.OPC_KIND.STORE:
            val = op_stack.pop(-1)
            offset = op_stack.pop(-1)
            bbl.AddIns(ir.Ins(o.ST, [mem_base, offset, val]))
        elif opc is wasm_opc.DROP:
            op_stack.pop(-1)
        elif opc is wasm_opc.LOCAL_GET:
            op_stack.append(GetLocalReg(int(args[0])))
        elif opc.kind is wasm_opc.OPC_KIND.ALU:
            if wasm_opc.FLAGS.UNARY in opc.flags:
                op = op_stack.pop(-1)
                dst = GetOpReg(op.kind, len(op_stack))
                assert False
            else:
                op2 = op_stack.pop(-1)
                op1 = op_stack.pop(-1)
                dst = GetOpReg(op1.kind, len(op_stack))
                op_stack.append(dst)
                assert wasm_opc.FLAGS.UNSIGNED not in opc.flags
                bbl.AddIns(ir.Ins(WASM_ALU_TO_CWERG[opc.basename], [dst, op1, op2]))

        elif opc.kind is wasm_opc.OPC_KIND.CMP:
            # this always works because of the sentinel: "end"
            succ = wasm_fun.impl.expr.instructions[n + 1]
            assert succ.opcode is wasm_opc.IF
            # push the can down the road
        elif opc is wasm_opc.IF:
            next_bbl = fun.AddBbl(ir.Bbl(f"if_{bbl_count}"))
            target = fun.AddBbl(ir.Bbl(f"else_{bbl_count}"))
            reg = None
            if args[0]:
                reg = fun.AddReg(ir.Reg(f"$if_result_{bbl_count}", WASM_TYPE_TO_CWERG_TYPE[args[0]]))
            block_stack.append((opc, reg, target))
            bbl_count += 1
            # this always works because the stack cannot be empty at  this point
            pred = wasm_fun.impl.expr.instructions[n - 1].opcode
            if pred.kind is wasm_opc.OPC_KIND.CMP:
                if wasm_opc.FLAGS.UNARY in pred.flags:
                    # eqz
                    br = o.BNE
                    op1 = op_stack.pop(-1)
                    op2 = ir.Const(op1.kind, 0)
                else:
                    # std two op cmp
                    op2 = op_stack.pop(-1)
                    op1 = op_stack.pop(-1)
                    br, swap, unsigned = WASM_CMP_TO_CWERG[pred.basename]
                    assert not unsigned
                    if swap:
                        op1, op2 = op2, op1
            else:
                br = o.BEQ
                op1 = op_stack.pop(-1)
                op2 = ir.Const(op1.kind, 0)

            bbl.AddIns(ir.Ins(br, [op1, op2, target]))
            bbl = next_bbl
        elif opc is wasm_opc.ELSE:
            block_opc, reg, next_bbl = block_stack.pop(-1)
            endif_bbl = fun.AddBbl(ir.Bbl(f"endif_{bbl_count}"))
            bbl_count += 1
            block_stack.append((block_opc, reg, endif_bbl))
            assert block_opc is wasm_opc.IF
            if reg:
                op = op_stack.pop(-1)
                bbl.AddIns(ir.Ins(o.MOV, [reg, op]))
            bbl.AddIns(ir.Ins(o.BRA, [endif_bbl]))
            bbl = next_bbl

        elif opc is wasm_opc.END:
            if block_stack:
                block_opc, reg, next_bbl = block_stack.pop(-1)
                if block_opc is wasm_opc.IF:
                    if reg:
                        op = op_stack.pop(-1)
                        bbl.AddIns(ir.Ins(o.MOV, [reg, op]))
                        bbl = next_bbl
                        op_stack.append(reg)
                else:
                    assert False
            else:
                assert n + 1 == len(wasm_fun.impl.expr.instructions)
                if returns:
                    assert len(returns) == 1
                    op = op_stack.pop(-1)
                    bbl.AddIns(ir.Ins(o.PUSHARG, [op]))
        elif opc is wasm_opc.CALL:
            wasm_callee = mod.functions[int(wasm_ins.args[0])]
            callee = unit.GetFun(wasm_callee.name)
            assert callee
            if callee.kind is o.FUN_KIND.EXTERN:
                for _ in range(len(callee.input_types) - 1):
                    bbl.AddIns(ir.Ins(o.PUSHARG, [op_stack.pop(-1)]))
                bbl.AddIns(ir.Ins(o.PUSHARG, [mem_base]))
            else:
                for _ in range(len(callee.input_types)):
                    bbl.AddIns(ir.Ins(o.PUSHARG, [op_stack.pop(-1)]))
            bbl.AddIns(ir.Ins(o.BSR, [callee]))
            # TODO check order
            for dk in reversed(callee.output_types):
                reg = GetOpReg(dk, len(op_stack))
                op_stack.append(reg)
                bbl.AddIns(ir.Ins(o.POPARG, [reg]))

        else:
            assert False, f"unsupported opcode {opc.name}"
    assert not op_stack
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

    if init_global:
        bbl.AddIns(ir.Ins(o.BSR, [init_global]))
    if init_data:
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
    global_mem_base.AddData(ir.DataBytes(ir.Const(o.DK.U32, bit_width // 8), b"\0"))
    memcpy = GenerateMemcopyFun(unit, addr_type)
    init_global = GenerateInitGlobalVarsFun(mod, unit, addr_type)
    init_data = GenerateInitDataFun(mod, unit, global_mem_base, memcpy, addr_type)
    main = None
    for wasm_fun in mod.functions:
        if isinstance(wasm_fun.impl, wasm.Import):
            assert wasm_fun.name in WASI_FUNCTIONS, f"unimplemented external function: {wasm_fun.name}"
            arguments = [addr_type] + TranslateTypeList(wasm_fun.func_type.args)
            returns = TranslateTypeList(wasm_fun.func_type.rets)
            wasm_fun = unit.AddFun(ir.Fun(wasm_fun.name, o.FUN_KIND.EXTERN, returns, arguments))
        else:
            assert isinstance(wasm_fun.impl, wasm.Code)
            if wasm_fun.name == "_start":
                wasm_fun = wasm.Function("$main", wasm_fun.func_type, wasm_fun.impl)
            fun = GenerateFun(unit, mod, wasm_fun, global_mem_base, addr_type)
            # print ("\n".join(serialize.FunRenderToAsm(fun)))
            sanity.FunCheck(fun, unit, check_cfg=False)
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

    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) != 3:
        print(f"not enough arguments. Need:  [32|64]  <wasm-file>", file=sys.stderr)
        sys.exit(1)
    assert sys.argv[1] in {"32", "64"}
    logging.debug(f"Reading {sys.argv[2]}")
    with open(sys.argv[2], "rb") as fin:
        unit = Translate(wasm.Module.read(fin), o.DK.A64 if sys.argv[1] == "64" else o.DK.A32)
        print("\n".join(serialize.UnitRenderToASM(unit)))
