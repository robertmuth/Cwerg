#!/usr/bin/python3

"""
Convert WASM files to Cwerg
"""

import logging
import typing
import dataclasses
import struct
from FrontEndWASM import opcode_tab as wasm_opc
import FrontEndWASM.parser as wasm
from Base import ir
from Base import opcode_tab as o
from Base import serialize
from Base import sanity

ZERO = ir.Const(o.DK.U32, 0)
ONE = ir.Const(o.DK.U32, 1)

ZERO_S = ir.Const(o.DK.S32, 0)
ONE_S = ir.Const(o.DK.S32, 1)

WASI_FUNCTIONS = {
    "$wasi$args_get",
    "$wasi$args_sizes_get",
    "$wasi$environ_get",
    "$wasi$environ_sizes_get",
    #
    "$wasi$fd_write",
    "$wasi$fd_read",
    "$wasi$fd_seek",
    "$wasi$fd_close",
    "$wasi$fd_fdstat_get",
    "$wasi$fd_prestat_get",
    "$wasi$fd_prestat_dir_name",
    "$wasi$fd_fdstat_set_flags",
    #
    "$wasi$path_open",
    #
    "$wasi$clock_time_get",
    #
    "$wasi$proc_exit",
    # pseudo (cwerg specific)
    "$wasi$print_i32_ln",
    "$wasi$print_i64_ln",
}


def ExtractBytesFromConstIns(wasm_ins: wasm.Instruction, val_type: wasm.NUM_TYPE) -> bytes:
    o = wasm_ins.opcode
    v = wasm_ins.args[0]
    if o is wasm_opc.I32_CONST:
        return v.to_bytes(4, 'little', signed=True)
    elif o is wasm_opc.I64_CONST:
        return v.to_bytes(8, 'little', signed=True)
    elif o is wasm_opc.F32_CONST:
        assert isinstance(v, float)
        return struct.pack("<f", v)
    elif o is wasm_opc.F64_CONST:
        assert isinstance(v, float)
        return struct.pack("<d", v)
    else:
        assert False, f"unexpected instruction {wasm_ins}"


def GenerateMemcpyFun(unit: ir.Unit, addr_type: o.DK) -> ir.Fun:
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


def GetInsFromInitializerExpression(expr: wasm.Expression) -> wasm.Instruction:
    assert len(expr.instructions) == 2
    assert expr.instructions[1].opcode is wasm_opc.END
    return expr.instructions[0]


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
        kind = o.MEM_KIND.RO if data.global_type.mut is wasm.MUT.CONST else o.MEM_KIND.RW
        mem = unit.AddMem(ir.Mem(f"global_vars_{n}", 16, kind))
        ins = GetInsFromInitializerExpression(data.expr)
        var_type = data.global_type.value_type
        if ins.opcode is wasm_opc.GLOBAL_GET:
            mem.AddData(ir.DataBytes(1, b"\0" * (4 if var_type.is_32bit() else 8)))
            src_mem = unit.GetMem(f"global_vars_{int(ins.args[0])}")
            reg = val32 if var_type.is_32bit() else val64
            bbl.AddIns(ir.Ins(o.LD_MEM, [reg, src_mem, ZERO]))
            bbl.AddIns(ir.Ins(o.ST_MEM, [mem, ZERO, reg]))
        elif ins.opcode.kind is wasm_opc.OPC_KIND.CONST:
            mem.AddData(ir.DataBytes(1, ExtractBytesFromConstIns(ins, var_type)))
        else:
            assert False, f"unsupported init instructions {ins}"
    return fun


def GenerateInitDataFun(mod: wasm.Module, unit: ir.Unit,
                        memcpy: ir.Fun, addr_type: o.DK) -> typing.Optional[ir.Fun]:
    fun = unit.AddFun(ir.Fun("init_data_fun", o.FUN_KIND.NORMAL, [], [addr_type]))
    bbl = fun.AddBbl(ir.Bbl("start"))
    epilog = fun.AddBbl(ir.Bbl("end"))
    epilog.AddIns(ir.Ins(o.RET, []))
    section = mod.sections.get(wasm.SECTION_ID.DATA)

    mem_base = fun.AddReg(ir.Reg("mem_base", addr_type))
    bbl.AddIns(ir.Ins(o.POPARG, [mem_base]))
    if not section:
        return None

    offset = fun.AddReg(ir.Reg("offset", o.DK.S32))
    src = fun.AddReg(ir.Reg("src", addr_type))
    dst = fun.AddReg(ir.Reg("dst", addr_type))

    for n, data in enumerate(section.items):
        assert data.memory_index == 0
        assert isinstance(data.offset, wasm.Expression)
        ins = GetInsFromInitializerExpression(data.offset)
        init = unit.AddMem(ir.Mem(f"global_init_mem_{n}", 16, o.MEM_KIND.RO))
        init.AddData(ir.DataBytes(1, data.init))
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

LOAD_TO_CWERG_TYPE = {
    "load8_u": o.DK.U8,
    "load8_s": o.DK.S8,
    "load16_u": o.DK.U16,
    "load16_s": o.DK.S16,
    "load32_u": o.DK.U32,
    "load32_s": o.DK.S32,
}

WASM_TYPE_TO_CWERG_TYPE = {
    wasm.VAL_TYPE.I32: o.DK.S32,
    wasm.VAL_TYPE.I64: o.DK.S64,
    wasm.VAL_TYPE.F32: o.DK.F32,
    wasm.VAL_TYPE.F64: o.DK.F64,
}

# value:  (br, swap, unsigned)
WASM_CMP_TO_CWERG_CBR_INV = {
    "eq": (o.BNE, False, False),
    "ne": (o.BEQ, False, False),
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

# value:  (br, swap, unsigned)
WASM_CMP_TO_CWERG_CBR = {
    "eq": (o.BEQ, False, False),
    "ne": (o.BNE, False, False),
    #
    "lt": (o.BLT, False, False),
    "lt_u": (o.BLT, False, True),
    "lt_s": (o.BLT, False, False),
    #
    "le": (o.BLE, False, False),
    "le_u": (o.BLE, False, True),
    "le_s": (o.BLE, False, False),
    #
    "gt": (o.BLT, True, False),
    "gt_u": (o.BLT, True, True),
    "gt_s": (o.BLT, True, False),
    #
    "ge": (o.BLE, True, False),
    "ge_u": (o.BLE, True, True),
    "ge_s": (o.BLE, True, False),
}

# value: (cmp, swap_op, swap_res, unsigned)
WASM_CMP_TO_CWERG_CMP = {
    "eq": (o.CMPEQ, False, False, False),
    "ne": (o.CMPEQ, False, True, False),
    #
    "lt": (o.CMPLT, False, False, False),
    "lt_u": (o.CMPLT, False, False, True),
    "lt_s": (o.CMPLT, False, False, False),
    #
    "le": (o.CMPLT, True, True, False),
    "le_u": (o.CMPLT, True, True, True),
    "le_s": (o.CMPLT, True, True, False),
    #
    "gt": (o.CMPLT, True, False, False),
    "gt_u": (o.CMPLT, True, False, True),
    "gt_s": (o.CMPLT, True, False, False),
    #
    "ge": (o.CMPLT, False, True, False),
    "ge_u": (o.CMPLT, False, True, True),
    "ge_s": (o.CMPLT, False, True, False),
}

WASM_ALU1_TO_CWERG = {
    "sqrt": ([], o.SQRT),
    "abs": ([], o.ABS),
    "neg": ([ir.Const(o.DK.S32, 0)], o.SUB),
    "clz": ([], o.CNTLZ),
    "ctz": ([], o.CNTTZ),
}


def HandleRotl(dst: ir.Reg, op1: ir.Reg, op2: ir.Reg, bbl: ir.Bbl):
    assert dst != op1
    assert dst.kind is o.DK.U32 or dst.kind is o.DK.U64, f"{dst}"
    bitwidth = ir.Const(dst.kind, dst.kind.bitwidth())
    bbl.AddIns(ir.Ins(o.SHL, [dst, op1, op2]))
    bbl.AddIns(ir.Ins(o.SUB, [op2, bitwidth, op2]))
    bbl.AddIns(ir.Ins(o.SHR, [op1, op1, op2]))  # here the unsigned requirement kicks in
    bbl.AddIns(ir.Ins(o.OR, [dst, dst, op1]))


WASM_ALU_TO_CWERG = {
    "xor": o.XOR,
    "and": o.AND,
    "or": o.OR,

    "shl": o.SHL,
    "shr_u": o.SHR,
    "shr_s": o.SHR,
    "rotl": HandleRotl,
    #
    "sub": o.SUB,
    "add": o.ADD,
    "mul": o.MUL,
    "div": o.DIV,
    "div_s": o.DIV,
    "div_u": o.DIV,
    "rem": o.REM,
    "rem_s": o.REM,
    "rem_u": o.REM,
    #
    # "copysign": o.ADD,
}

WASM_CONV_TO_CWERG = {
    #
    "f64.convert_i32_u": (o.CONV, False, True),
    "f32.convert_i32_u": (o.CONV, False, True),
    "i64.extend_i32_u": (o.CONV, False, True),
    #
    "i64.extend_i32_s": (o.CONV, False, False),
    #
    "i32.wrap_i64": (o.CONV, False, False),
    #
    "f64.convert_i32_s": (o.CONV, False, False),
    "f64.convert_i64_s": (o.CONV, False, False),
    "f32.convert_i32_s": (o.CONV, False, False),
    "f32.convert_i64_s": (o.CONV, False, False),
    #
    "i32.trunc_f64_u": (o.CONV, True, False),
    "i64.trunc_f64_u": (o.CONV, True, False),
    "i32.trunc_f64_s": (o.CONV, False, False),
    "i64.trunc_f64_s": (o.CONV, False, False),
    "i32.trunc_f32_s": (o.CONV, False, False),
    "i64.trunc_f32_s": (o.CONV, False, False),
    "f64.promote_f32": (o.CONV, False, False),
    "f32.demote_f64": (o.CONV, False, False),
}

SUPPORTED_BITCAST = {
    'i32.reinterpret_f32',
    'i64.reinterpret_f64',
    'f32.reinterpret_i32',
    'f64.reinterpret_i64',
}


def FindFunWithSignature(unit: ir.Unit, arguments: typing.List[o.DK], returns: typing.List[o.DK]) -> ir.Fun:
    for fun in unit.funs:
        if fun.output_types == returns and fun.input_types == arguments:
            return fun
    assert False


def MakeBranch(pred: wasm_opc.Opcode, op_stack, inverse):
    if pred.kind is wasm_opc.OPC_KIND.CMP:
        if wasm_opc.FLAGS.UNARY in pred.flags:
            # eqz
            op1 = op_stack.pop(-1)
            op2 = ir.Const(op1.kind, 0)
            return o.BNE if inverse else o.BEQ, op1, op2, False
        else:
            # std two op cmp
            op2 = op_stack.pop(-1)
            op1 = op_stack.pop(-1)
            tab = WASM_CMP_TO_CWERG_CBR_INV if inverse else WASM_CMP_TO_CWERG_CBR
            br, swap, unsigned = tab[pred.basename]
            if swap:
                op1, op2 = op2, op1
            return br, op1, op2, unsigned
    else:
        op1 = op_stack.pop(-1)
        op2 = ir.Const(op1.kind, 0)
        return o.BEQ if inverse else o.BNE, op1, op2, False


def MakeCompare(opc: wasm_opc.Opcode, op_stack):
    if wasm_opc.FLAGS.UNARY in opc.flags:
        # eqz
        op1 = op_stack.pop(-1)
        op2 = ir.Const(op1.kind, 0)
        return o.CMPEQ, ONE_S, ZERO_S, op1, op2, False

    cmp, swap_op, swap_res, unsigned = WASM_CMP_TO_CWERG_CMP[opc.basename]
    op2 = op_stack.pop(-1)
    op1 = op_stack.pop(-1)
    if swap_op:
        op1, op2 = op2, op1
    res1 = ONE_S
    res2 = ZERO_S
    if swap_res:
        res1, res2 = res2, res1
    return cmp, res1, res2, op1, op2, unsigned


def GetOpReg(fun: ir.Fun, dk: o.DK, pos: int) -> ir.Reg:
    reg_name = f"$op_{pos}_{dk.name}"
    reg = fun.MaybeGetReg(reg_name)
    return reg if reg else fun.AddReg(ir.Reg(reg_name, dk))


def GetLocalReg(fun: ir.Fun, no: int) -> ir.Reg:
    reg_name = f"$loc_{no}"
    reg = fun.MaybeGetReg(reg_name)
    assert reg, f"unknown reg {reg_name}"
    return reg


@dataclasses.dataclass
class Block:
    opcode: wasm_opc.Opcode
    no: int
    start_bbl: ir.Bbl
    end_bbl: ir.Bbl
    result_types: typing.List[o.DK]
    param_types: typing.List[o.DK]
    stack_start: int
    else_bbl: typing.Optional[ir.Bbl]

    def OpStackSizeAfter(self):
        return self.stack_start + len(self.result_types) - len(self.param_types)

    def FinalizeIf(self, op_stack, bbl: ir.Bbl, fun: ir.Fun, unreachable: bool):
        expected_op_stack_size = self.OpStackSizeAfter()
        if unreachable:
            assert len(op_stack) >= self.stack_start - len(self.param_types)
            # reset so that the else branch can start at the same place
        else:
            # print (f"@@ FinalizePop {fun.name}:  {self.num_results}")
            assert len(op_stack) == expected_op_stack_size
        while len(op_stack) > self.stack_start - len(self.param_types):
            op_stack.pop(-1)
        for dk in self.param_types:
            op_stack.append(GetOpReg(fun, dk, len(op_stack)))

    def FinalizeEnd(self, op_stack, bbl: ir.Bbl, fun: ir.Fun, unreachable: bool):
        expected_op_stack_size = self.OpStackSizeAfter()
        if unreachable:
            assert len(op_stack) >= self.stack_start - len(self.param_types)
            while len(op_stack) > expected_op_stack_size:
                op_stack.pop(-1)
            while len(op_stack) < expected_op_stack_size:
                dk = self.result_types[len(op_stack) - expected_op_stack_size]
                op_stack.append(GetOpReg(fun, dk, len(op_stack)))
            return
        assert len(
            op_stack) == expected_op_stack_size, f"[{fun.name}] end of block stack size mismatch wanted:{expected_op_stack_size}  got:{len(op_stack)}"

    def FinalizeResultsCopy(self, op_stack, bbl: ir.Bbl, fun: ir.Fun):
        # print (f"@@ FinalizeCopy {fun.name}:  {self.num_results}")
        dst_pos = self.stack_start + len(self.result_types)
        src_pos = len(op_stack)
        for i in range(len(self.result_types)):
            dst_pos -= 1
            src_pos -= 1
            op = op_stack[src_pos]
            dst_reg = GetOpReg(fun, op.kind, dst_pos)
            if dst_reg != op:
                bbl.AddIns(ir.Ins(o.MOV, [dst_reg, op]))


def TranslateTypeList(result_type: wasm.ResultType) -> typing.List[o.DK]:
    return [WASM_TYPE_TO_CWERG_TYPE[x] for x in result_type.types]


def MakeBlock(no: int, opc, args, fun, op_stack: typing.List, mod: wasm.Module) -> Block:
    prefix = opc.name
    start_bbl = fun.AddBbl(ir.Bbl(f"{prefix}_{no}"))
    else_bbl = None
    result_types = []
    param_types = []
    type_arg = args[0]
    if opc is wasm_opc.IF:
        else_bbl = fun.AddBbl(ir.Bbl(f"else_{no}"))
    if type_arg is not None:
        if isinstance(args[0], wasm.VAL_TYPE):
            result_types = [WASM_TYPE_TO_CWERG_TYPE[args[0]]]
        else:
            assert isinstance(type_arg, wasm.TypeIdx), f"{type(type_arg)}"
            type_sec = mod.sections.get(wasm.SECTION_ID.TYPE)
            block_type: wasm.FunctionType = type_sec.items[int(type_arg)]
            result_types = TranslateTypeList(block_type.rets)
            param_types = TranslateTypeList(block_type.args)
        for op, dk in zip(op_stack[-len(result_types):], result_types):
            assert op.kind is dk

    next_bbl = fun.AddBbl(ir.Bbl(f"end{prefix}_{no}"))
    return Block(opc, no, start_bbl, next_bbl, result_types, param_types, len(op_stack),
                 else_bbl)


def GetTargetBbl(block_stack: typing.List[Block], offset: wasm.LabelIdx):
    block = block_stack[-offset - 1]
    if block.opcode is wasm_opc.LOOP:
        return block.start_bbl
    else:
        return block.end_bbl


def GetTargetBlock(block_stack: typing.List[Block], offset: wasm.LabelIdx):
    return block_stack[-offset - 1]


def ToUnsigned(dk: o.DK):
    if dk is o.DK.S32:
        return o.DK.U32
    elif dk is o.DK.S64:
        return o.DK.U64
    else:
        assert False, f"unexpected operand type {dk}"


def EmitCall(fun: ir.Fun, bbl: ir.Bbl, call_ins: ir.Ins, op_stack, mem_base, callee: ir.Fun):
    """
    if the wasm function has the signature:
    [a b] -> [c d]
    This means the top of op_stack must be [a b] before the call and will be [c d] after the call

    The called Cwerg function expects the right most input to be pushed on the stack first, so we get
    pusharg b
    pusharg a
    We always pass mem_base as the the first argument so there is also
    pusharg mem_base

    The called Cwerg function pushes the results also from right to left
    [callee] pusharg d
    [callee] pusharg c


    """
    # print (f"########## calling {callee.name} in:{callee.input_types}  out:{callee.output_types}")
    # print ("# STACK")
    # print (op_stack)
    for dk in reversed(callee.input_types[1:]):
        arg = op_stack.pop(-1)
        assert arg.kind == dk, f"expected type {dk} [{arg}] got {arg.kind}"
        bbl.AddIns(ir.Ins(o.PUSHARG, [arg]))
    bbl.AddIns(ir.Ins(o.PUSHARG, [mem_base]))

    bbl.AddIns(call_ins)

    for dk in callee.output_types:
        dst = GetOpReg(fun, dk, len(op_stack))
        op_stack.append(dst)
        bbl.AddIns(ir.Ins(o.POPARG, [dst]))


def GenerateFun(unit: ir.Unit, mod: wasm.Module, wasm_fun: wasm.Function,
                fun: ir.Fun, global_table, addr_type):
    # op_stack contains regs produced by GetOpReg (it may only occur a the position encoding in its name
    op_stack: typing.List[typing.Union[ir.Reg, ir.Const]] = []
    block_stack: typing.List[Block] = []
    bbls: typing.List[ir.Bbl] = []
    bbl_count = 0
    jtb_count = 0

    bbls.append(fun.AddBbl(ir.Bbl("start")))

    loc_index = 0
    assert fun.input_types[0] is addr_type
    mem_base = fun.AddReg(ir.Reg("mem_base", addr_type))
    bbls[-1].AddIns(ir.Ins(o.POPARG, [mem_base]))
    for dk in fun.input_types[1:]:
        reg = fun.AddReg(ir.Reg(f"$loc_{loc_index}", dk))
        loc_index += 1
        bbls[-1].AddIns(ir.Ins(o.POPARG, [reg]))

    for locals in wasm_fun.impl.locals_list:
        for i in range(locals.count):
            reg = fun.AddReg(ir.Reg(f"$loc_{loc_index}", WASM_TYPE_TO_CWERG_TYPE[locals.kind]))
            loc_index += 1
            bbls[-1].AddIns(ir.Ins(o.MOV, [reg, ir.Const(reg.kind, 0)]))

    DEBUG = False
    if DEBUG:
        print()
        print(f"# {fun.name} #ins:{len(wasm_fun.impl.expr.instructions)} in:{fun.input_types} out:{fun.output_types}")

    opc = None
    last_opc = None
    for n, wasm_ins in enumerate(wasm_fun.impl.expr.instructions):
        last_opc = opc
        opc = wasm_ins.opcode
        args = wasm_ins.args
        op_stack_size_before = len(op_stack)
        if DEBUG:
            print(f"#@@ {opc.name}", args, len(op_stack))
        if opc.kind is wasm_opc.OPC_KIND.CONST:
            # breaks for floats
            # breaks for floats
            kind = OPC_TYPE_TO_CWERG_TYPE[opc.op_type]
            dst = GetOpReg(fun, kind, len(op_stack))
            bbls[-1].AddIns(ir.Ins(o.MOV, [dst, ir.Const(kind, args[0])]))
            op_stack.append(dst)
        elif opc is wasm_opc.NOP:
            pass
        elif opc.kind is wasm_opc.OPC_KIND.STORE:
            val = op_stack.pop(-1)
            offset = op_stack.pop(-1)
            if args[1] != 0:
                tmp = GetOpReg(fun, offset.kind, len(op_stack))
                bbls[-1].AddIns(ir.Ins(o.ADD, [tmp, offset, ir.Const(offset.kind, args[1])]))
                offset = tmp
            bbls[-1].AddIns(ir.Ins(o.ST, [mem_base, offset, val]))
        elif opc is wasm_opc.DROP:
            op_stack.pop(-1)
        elif opc is wasm_opc.LOCAL_GET:
            loc = GetLocalReg(fun, int(args[0]))
            dst = GetOpReg(fun, loc.kind, len(op_stack))
            bbls[-1].AddIns(ir.Ins(o.MOV, [dst, loc]))
            op_stack.append(dst)
        elif opc is wasm_opc.LOCAL_SET:
            op = op_stack.pop(-1)
            bbls[-1].AddIns(ir.Ins(o.MOV, [GetLocalReg(fun, int(args[0])), op]))
        elif opc is wasm_opc.LOCAL_TEE:
            op = op_stack[-1]  # no pop!
            bbls[-1].AddIns(ir.Ins(o.MOV, [GetLocalReg(fun, int(args[0])), op]))
        elif opc is wasm_opc.GLOBAL_GET:
            var_index = int(args[0])
            var: wasm.Glob = mod.sections.get(wasm.SECTION_ID.GLOBAL).items[var_index]
            dst = GetOpReg(fun, WASM_TYPE_TO_CWERG_TYPE[var.global_type.value_type], len(op_stack))
            var_mem = unit.GetMem(f"global_vars_{var_index}")
            bbls[-1].AddIns(ir.Ins(o.LD_MEM, [dst, var_mem, ZERO]))
            op_stack.append(dst)
        elif opc is wasm_opc.GLOBAL_SET:
            op = op_stack.pop(-1)
            var_index = int(args[0])
            var_mem = unit.GetMem(f"global_vars_{var_index}")
            bbls[-1].AddIns(ir.Ins(o.ST_MEM, [var_mem, ZERO, op]))
        elif opc.kind is wasm_opc.OPC_KIND.ALU:
            if wasm_opc.FLAGS.UNARY in opc.flags:
                arg, opcode = WASM_ALU1_TO_CWERG[opc.basename]
                op = op_stack.pop(-1)
                dst = GetOpReg(fun, op.kind, len(op_stack))
                bbls[-1].AddIns(ir.Ins(opcode, [dst] + arg + [op]))
                op_stack.append(dst)
            else:
                op2 = op_stack.pop(-1)
                op1 = op_stack.pop(-1)
                dst = GetOpReg(fun, op1.kind, len(op_stack))
                alu = WASM_ALU_TO_CWERG[opc.basename]
                if wasm_opc.FLAGS.UNSIGNED in opc.flags:
                    tmp1 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 1)
                    tmp2 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 2)
                    tmp3 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 3)
                    bbls[-1].AddIns(ir.Ins(o.CONV, [tmp1, op1]))
                    bbls[-1].AddIns(ir.Ins(o.CONV, [tmp2, op2]))
                    if isinstance(alu, o.Opcode):
                        bbls[-1].AddIns(ir.Ins(alu, [tmp3, tmp1, tmp2]))
                    else:
                        alu(tmp3, tmp1, tmp2, bbls[-1])
                    bbls[-1].AddIns(ir.Ins(o.CONV, [dst, tmp3]))
                else:
                    assert isinstance(alu, o.Opcode), f"{alu}"
                    bbls[-1].AddIns(ir.Ins(alu, [dst, op1, op2]))
                op_stack.append(dst)
        elif opc.kind is wasm_opc.OPC_KIND.CONV:
            conv, dst_unsigned, src_unsigned = WASM_CONV_TO_CWERG[opc.name]
            op = op_stack.pop(-1)
            dst = GetOpReg(fun, OPC_TYPE_TO_CWERG_TYPE[opc.op_type], len(op_stack))
            if src_unsigned:
                tmp = GetOpReg(fun, ToUnsigned(op.kind), op_stack_size_before + 1)
                bbls[-1].AddIns(ir.Ins(o.CONV, [tmp, op]))
                op = tmp
            if dst_unsigned:
                tmp = GetOpReg(fun, ToUnsigned(dst.kind), op_stack_size_before + 1)
                dst, tmp = tmp, dst
            bbls[-1].AddIns(ir.Ins(conv, [dst, op]))
            if dst_unsigned:
                bbls[-1].AddIns(ir.Ins(o.CONV, [tmp, dst]))
                dst = tmp
            op_stack.append(dst)
        elif opc.kind is wasm_opc.OPC_KIND.BITCAST:
            assert opc.name in SUPPORTED_BITCAST
            op = op_stack.pop(-1)
            dst = GetOpReg(fun, OPC_TYPE_TO_CWERG_TYPE[opc.op_type], len(op_stack))
            bbls[-1].AddIns(ir.Ins(o.BITCAST, [dst, op]))
            op_stack.append(dst)
        elif opc.kind is wasm_opc.OPC_KIND.CMP:
            # this always works because of the sentinel: "end"
            succ = wasm_fun.impl.expr.instructions[n + 1]
            if succ.opcode not in {wasm_opc.IF, wasm_opc.BR_IF, wasm_opc.SELECT}:
                cmp, res1, res2, op1, op2, unsigned = MakeCompare(opc, op_stack)
                if unsigned:
                    tmp1 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 1)
                    tmp2 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 2)
                    bbls[-1].AddIns(ir.Ins(o.CONV, [tmp1, op1]))
                    bbls[-1].AddIns(ir.Ins(o.CONV, [tmp2, op2]))
                    op1 = tmp1
                    op2 = tmp2
                dst = GetOpReg(fun, o.DK.S32, len(op_stack))
                bbls[-1].AddIns(ir.Ins(cmp, [dst, res1, res2, op1, op2]))
                op_stack.append(dst)
        elif opc is wasm_opc.LOOP or opc is wasm_opc.BLOCK:
            block_stack.append(MakeBlock(bbl_count, opc, args, fun, op_stack, mod))
            bbl_count += 1
            bbls.append(block_stack[-1].start_bbl)
        elif opc is wasm_opc.IF:
            # note we do set the new bbl right away because we add some instructions to the old one
            # this always works because the stack cannot be empty at this point
            pred = wasm_fun.impl.expr.instructions[n - 1].opcode
            br, op1, op2, unsigned = MakeBranch(pred, op_stack, True)
            if unsigned:
                tmp1 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 1)
                tmp2 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 2)
                bbls[-1].AddIns(ir.Ins(o.CONV, [tmp1, op1]))
                bbls[-1].AddIns(ir.Ins(o.CONV, [tmp2, op2]))
                op1 = tmp1
                op2 = tmp2
            block_stack.append(MakeBlock(bbl_count, opc, args, fun, op_stack, mod))
            # assert len(block_stack[-1].param_types) == 0
            bbl_count += 1
            bbls[-1].AddIns(ir.Ins(br, [op1, op2, block_stack[-1].else_bbl]))
            bbls.append(block_stack[-1].start_bbl)
        elif opc is wasm_opc.ELSE:
            block = block_stack[-1]
            assert block.opcode is wasm_opc.IF
            block.FinalizeIf(op_stack, bbls[-1], fun, last_opc in {wasm_opc.UNREACHABLE, wasm_opc.BR})
            if DEBUG:
                print(f"#@@ AFTER STACK RESTORE", len(op_stack))
            op_stack = op_stack[0:block.stack_start]
            bbls[-1].AddIns(ir.Ins(o.BRA, [block.end_bbl]))
            assert block.else_bbl is not None
            bbls.append(block.else_bbl)
            block.else_bbl = None
        elif opc is wasm_opc.END:
            if block_stack:
                block = block_stack.pop(-1)
                block.FinalizeEnd(op_stack, bbls[-1], fun, last_opc in {wasm_opc.UNREACHABLE, wasm_opc.BR})
                if block.else_bbl:
                    bbls.append(block.else_bbl)
                bbls.append(block.end_bbl)
            else:
                # end of function
                assert n + 1 == len(wasm_fun.impl.expr.instructions)
                pred = wasm_fun.impl.expr.instructions[n - 1].opcode
                if pred not in {wasm_opc.RETURN, wasm_opc.UNREACHABLE, wasm_opc.BR}:
                    for x in reversed(fun.output_types):
                        op = op_stack.pop(-1)
                        assert op.kind == x, f"outputs: {fun.output_types} mismatch {op.kind} vs {x}"
                        bbls[-1].AddIns(ir.Ins(o.PUSHARG, [op]))
                    bbls[-1].AddIns(ir.Ins(o.RET, []))

        elif opc is wasm_opc.CALL:
            wasm_callee = mod.functions[int(wasm_ins.args[0])]
            callee = unit.GetFun(wasm_callee.name)
            assert callee, f"unknown fun: {wasm_callee.name}"
            EmitCall(fun, bbls[-1], ir.Ins(o.BSR, [callee]), op_stack, mem_base, callee)
        elif opc is wasm_opc.CALL_INDIRECT:
            assert isinstance(args[1], wasm.TableIdx), f"{type(args[1])}"
            assert int(args[1]) == 0, f"only one table supported"
            assert isinstance(args[0], wasm.TypeIdx), f"{type(args[0])}"
            type_sec = mod.sections.get(wasm.SECTION_ID.TYPE)
            func_type: wasm.FunctionType = type_sec.items[int(args[0])]
            arguments = [addr_type] + TranslateTypeList(func_type.args)
            returns = TranslateTypeList(func_type.rets)
            # print (f"# @@@@ CALL INDIRECT {returns} <- {arguments}  [{int(args[0])}] {func_type}")
            signature = FindFunWithSignature(unit, arguments, returns)
            table_reg = GetOpReg(fun, addr_type, len(op_stack))
            code_type = o.DK.C32 if addr_type is o.DK.A32 else o.DK.C64
            fun_reg = GetOpReg(fun, code_type, len(op_stack) + 1)
            index = op_stack.pop(-1)
            assert index.kind is o.DK.S32

            bbls[-1].AddIns(ir.Ins(o.MUL, [index, index, ir.Const(o.DK.U32, code_type.bitwidth() // 8)]))
            bbls[-1].AddIns(ir.Ins(o.LEA_MEM, [table_reg, global_table, ZERO]))
            bbls[-1].AddIns(ir.Ins(o.LD, [fun_reg, table_reg, index]))
            EmitCall(fun, bbls[-1], ir.Ins(o.JSR, [fun_reg, signature]), op_stack, mem_base, signature)
        elif opc is wasm_opc.RETURN:
            for x in reversed(fun.output_types):
                op = op_stack.pop(-1)
                assert op.kind == x, f"outputs: {fun.output_types} mismatch {op.kind} vs {x}"
                bbls[-1].AddIns(ir.Ins(o.PUSHARG, [op]))
            bbls[-1].AddIns(ir.Ins(o.RET, []))
        elif opc is wasm_opc.BR:
            assert isinstance(args[0], wasm.LabelIdx)
            block = GetTargetBlock(block_stack, args[0])
            target = block.start_bbl
            if block.opcode is not wasm_opc.LOOP:
                target = block.end_bbl
                block.FinalizeResultsCopy(op_stack, bbls[-1], fun)
            bbls[-1].AddIns(ir.Ins(o.BRA, [target]))
        elif opc is wasm_opc.BR_IF:
            assert isinstance(args[0], wasm.LabelIdx)
            pred = wasm_fun.impl.expr.instructions[n - 1].opcode
            br, op1, op2, unsigned = MakeBranch(pred, op_stack, False)
            if unsigned:
                tmp1 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 1)
                tmp2 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 2)
                bbls[-1].AddIns(ir.Ins(o.CONV, [tmp1, op1]))
                bbls[-1].AddIns(ir.Ins(o.CONV, [tmp2, op2]))
                op1 = tmp1
                op2 = tmp2
            block = GetTargetBlock(block_stack, args[0])
            target = block.start_bbl
            if block.opcode is not wasm_opc.LOOP:
                target = block.end_bbl
                block.FinalizeResultsCopy(op_stack, bbls[-1], fun)
            bbls[-1].AddIns(ir.Ins(br, [op1, op2, target]))
        elif opc is wasm_opc.SELECT:
            pred = wasm_fun.impl.expr.instructions[n - 1].opcode
            br, op1, op2, unsigned = MakeBranch(pred, op_stack, False)
            val_f = op_stack.pop(-1)
            val_t = op_stack.pop(-1)
            assert val_f.kind == val_t.kind
            reg = GetOpReg(fun, val_f.kind, len(op_stack))
            op_stack.append(reg)
            bbls[-1].AddIns(ir.Ins(o.MOV, [reg, val_t]))
            bbls.append(fun.AddBbl(ir.Bbl(f"select_{bbl_count}")))
            bbl_count += 1
            if unsigned:
                tmp1 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 1)
                tmp2 = GetOpReg(fun, ToUnsigned(op1.kind), op_stack_size_before + 2)
                bbls[-1].AddIns(ir.Ins(o.CONV, [tmp1, op1]))
                bbls[-1].AddIns(ir.Ins(o.CONV, [tmp2, op2]))
                op1 = tmp1
                op2 = tmp2
            bbls[-2].AddIns(ir.Ins(br, [op1, op2, bbls[-1]]))
            bbls[-2].AddIns(ir.Ins(o.MOV, [reg, val_f]))
        elif opc.kind is wasm_opc.OPC_KIND.LOAD:
            offset = op_stack.pop(-1)
            if args[1] != 0:
                tmp = GetOpReg(fun, offset.kind, len(op_stack))
                bbls[-1].AddIns(ir.Ins(o.ADD, [tmp, offset, ir.Const(offset.kind, args[1])]))
                offset = tmp
            dst = GetOpReg(fun, OPC_TYPE_TO_CWERG_TYPE[opc.op_type], len(op_stack))
            op_stack.append(dst)
            dk_tmp = LOAD_TO_CWERG_TYPE.get(opc.basename)
            if dk_tmp:
                tmp = GetOpReg(fun, dk_tmp, len(op_stack))
                bbls[-1].AddIns(ir.Ins(o.LD, [tmp, mem_base, offset]))
                bbls[-1].AddIns(ir.Ins(o.CONV, [dst, tmp]))
            else:
                bbls[-1].AddIns(ir.Ins(o.LD, [dst, mem_base, offset]))
        elif opc is wasm_opc.BR_TABLE:
            bbl_tab = {n: GetTargetBbl(block_stack, x)
                       for n, x in enumerate(args[0])}
            bbl_def = GetTargetBbl(block_stack, args[1])
            op = op_stack.pop(-1)
            tab_size = ir.Const(ToUnsigned(op.kind), len(bbl_tab))
            jtb_count += 1
            jtb = fun.AddJtb(ir.Jtb(f"jtb_{jtb_count}", bbl_def, bbl_tab,
                                    tab_size.value))
            reg_unsigned = GetOpReg(fun, ToUnsigned(op.kind), len(op_stack))
            bbls[-1].AddIns(ir.Ins(o.CONV, [reg_unsigned, op]))
            bbls[-1].AddIns(ir.Ins(o.BLE, [tab_size, reg_unsigned, bbl_def]))
            bbls[-1].AddIns(ir.Ins(o.SWITCH, [reg_unsigned, jtb]))
        elif opc is wasm_opc.UNREACHABLE:
            bbls[-1].AddIns(ir.Ins(o.TRAP, []))
        elif opc is wasm_opc.MEMORY_GROW or opc is wasm_opc.MEMORY_SIZE:
            op = ZERO_S
            if opc is wasm_opc.MEMORY_GROW:
                op = op_stack.pop(-1)
            bbls[-1].AddIns(ir.Ins(o.PUSHARG, [op]))
            assert unit.GetFun("__memory_grow")
            bbls[-1].AddIns(ir.Ins(o.BSR, [unit.GetFun("__memory_grow")]))
            dst = GetOpReg(fun, o.DK.S32, len(op_stack))
            bbls[-1].AddIns(ir.Ins(o.POPARG, [dst]))
            op_stack.append(dst)
        else:
            assert False, f"unsupported opcode [{opc.name}]"
    assert not op_stack, f"op_stack not empty in {fun.name}: {op_stack}"
    assert not block_stack, f"block_stack not empty in {fun.name}: {block_stack}"
    assert len(bbls) == len(fun.bbls)
    fun.bbls = bbls


def GenerateStartup(unit: ir.Unit, global_argc, global_argv, main: ir.Fun,
                    init_global: ir.Fun, init_data: ir.Fun, initial_heap_size_pages: int,
                    addr_type: o.DK) -> ir.Fun:
    bit_width = addr_type.bitwidth()

    global_mem_base = unit.AddMem(ir.Mem("__memory_base", 0, o.MEM_KIND.EXTERN))

    fun = unit.AddFun(ir.Fun("main", o.FUN_KIND.NORMAL, [o.DK.U32], [o.DK.U32, addr_type]))
    argc = fun.AddReg(ir.Reg("argc", o.DK.U32))
    argv = fun.AddReg(ir.Reg("argv", addr_type))

    bbl = fun.AddBbl(ir.Bbl("start"))
    bbl.AddIns(ir.Ins(o.POPARG, [argc]))
    bbl.AddIns(ir.Ins(o.POPARG, [argv]))
    bbl.AddIns(ir.Ins(o.ST_MEM, [global_argc, ZERO, argc]))
    bbl.AddIns(ir.Ins(o.ST_MEM, [global_argv, ZERO, argv]))

    bbl.AddIns(ir.Ins(o.BSR, [unit.GetFun("__wasi_init")]))
    if initial_heap_size_pages:
        bbl.AddIns(ir.Ins(o.PUSHARG, [ir.Const(o.DK.S32, initial_heap_size_pages)]))
        bbl.AddIns(ir.Ins(o.BSR, [unit.GetFun("__memory_grow")]))
        bbl.AddIns(ir.Ins(o.POPARG, [fun.AddReg(ir.Reg("dummy", o.DK.S32))]))

    mem_base = fun.AddReg(ir.Reg("mem_base", addr_type))
    bbl.AddIns(ir.Ins(o.LD_MEM, [mem_base, global_mem_base, ZERO]))

    if init_global:
        bbl.AddIns(ir.Ins(o.BSR, [init_global]))
    if init_data:
        bbl.AddIns(ir.Ins(o.PUSHARG, [mem_base]))
        bbl.AddIns(ir.Ins(o.BSR, [init_data]))

    bbl.AddIns(ir.Ins(o.PUSHARG, [mem_base]))
    bbl.AddIns(ir.Ins(o.BSR, [main]))
    bbl.AddIns(ir.Ins(o.PUSHARG, [ir.Const(o.DK.U32, 0)]))
    bbl.AddIns(ir.Ins(o.RET, []))
    return fun


def MaybeMakeGlobalTable(mod: wasm.Module, unit: ir.Unit, addr_type: o.DK):
    bit_width = addr_type.bitwidth()
    table_sec = mod.sections.get(wasm.SECTION_ID.TABLE)
    table_elements = mod.sections.get(wasm.SECTION_ID.ELEMENT)
    if not table_sec:
        return None

    global_table = None
    assert table_elements
    assert len(table_sec.items) == 1
    table_type: wasm.TableType = table_sec.items[0].table_type
    assert table_type.element_type == wasm.REF_TYPE.FUNCREF
    table_data = [None] * table_type.limits.max
    for elem in table_elements.items:
        ins = GetInsFromInitializerExpression(elem.expr)
        assert ins.opcode is wasm_opc.I32_CONST
        start = ins.args[0]
        for n, fun in enumerate(elem.funcidxs):
            table_data[start + n] = fun

    global_table = unit.AddMem(ir.Mem("global_table", bit_width // 8, o.MEM_KIND.RO))
    width = addr_type.bitwidth() // 8
    for fun in table_data:
        if fun is None:
            global_table.AddData(ir.DataBytes(width, b"\0"))
        else:
            assert isinstance(fun, wasm.FuncIdx)
            fun = unit.GetFun(mod.functions[int(fun)].name)
            global_table.AddData(ir.DataAddrFun(width, fun))
    return global_table


def Translate(mod: wasm.Module, addr_type: o.DK) -> ir.Unit:
    table_import = mod.sections.get(wasm.SECTION_ID.IMPORT)
    for i in table_import.items:
        assert isinstance(i, wasm.Import)
        assert isinstance(i.desc, wasm.TypeIdx), f"cannot handle strange imports: {i}"

    bit_width = addr_type.bitwidth()
    unit = ir.Unit("unit")

    global_argv = unit.AddMem(ir.Mem("global_argv",
                                     2 * bit_width // 8, o.MEM_KIND.RW))
    global_argv.AddData(ir.DataBytes(bit_width // 8, b"\0"))

    global_argc = unit.AddMem(ir.Mem("global_argc", 4, o.MEM_KIND.RW))
    global_argc.AddData(ir.DataBytes(4, b"\0"))

    memcpy = GenerateMemcpyFun(unit, addr_type)
    init_global = GenerateInitGlobalVarsFun(mod, unit, addr_type)
    init_data = GenerateInitDataFun(mod, unit, memcpy, addr_type)
    unit.AddFun(ir.Fun("__wasi_init", o.FUN_KIND.EXTERN, [], []))
    unit.AddFun(ir.Fun("__memory_grow", o.FUN_KIND.EXTERN, [o.DK.S32], [o.DK.S32]))

    main = None
    for wasm_fun in mod.functions:
        # forward declare everything since we cannot rely on a topological sort of the funs
        if isinstance(wasm_fun.impl, wasm.Import):
            assert wasm_fun.name in WASI_FUNCTIONS, f"unimplemented external function: {wasm_fun.name}"
        arguments = [addr_type] + TranslateTypeList(wasm_fun.func_type.args)
        returns = TranslateTypeList(wasm_fun.func_type.rets)
        # assert len(returns) <= 1
        unit.AddFun(ir.Fun(wasm_fun.name, o.FUN_KIND.EXTERN, returns, arguments))

    global_table = MaybeMakeGlobalTable(mod, unit, addr_type)

    for wasm_fun in mod.functions:
        if isinstance(wasm_fun.impl, wasm.Import):
            continue
        fun = unit.GetFun(wasm_fun.name)
        fun.kind = o.FUN_KIND.NORMAL
        if fun.name == "_start":
            fun.name = "$main"
            main = fun
        GenerateFun(unit, mod, wasm_fun, fun, global_table, addr_type)
        # print ("\n".join(serialize.FunRenderToAsm(fun)))
        sanity.FunCheck(fun, unit, check_cfg=False)

    initial_heap_size_pages = 0
    sec_memory = mod.sections.get(wasm.SECTION_ID.MEMORY)
    if sec_memory:
        assert len(sec_memory.items) == 1
        heap: wasm.Mem = sec_memory.items[0]
        initial_heap_size_pages = heap.mem_type.limits.min
    assert main, f"missing main function"
    GenerateStartup(unit, global_argc, global_argv, main, init_global, init_data,
                    initial_heap_size_pages, addr_type)

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
