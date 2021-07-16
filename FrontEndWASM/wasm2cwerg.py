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

ZERO = ir.Const(o.DK.U32, 0)
ONE = ir.Const(o.DK.U32, 1)


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


def GenerateInitGlobalVarsFun(mod: wasm.Module, unit: ir.Unit, addr_type: o.DK):
    fun = unit.AddFun(ir.Fun("init_global_vars_fun", o.FUN_KIND.NORMAL, [], []))
    bbl = fun.AddBbl(ir.Bbl("start"))
    section = mod.sections.get(wasm.SECTION_ID.GLOBAL)
    if not section:
        return
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


def GenerateInitDataFun(mod: wasm.Module, unit: ir.Unit, global_mem_base: ir.Mem, addr_type: o.DK):
    fun = unit.AddFun(ir.Fun("init_data_fun", o.FUN_KIND.NORMAL, [], []))
    bbl = fun.AddBbl(ir.Bbl("start"))
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
        # insert memcpy call


def Translate(mod: wasm.Module, addr_type: o.DK) -> ir.Unit:
    bit_width = addr_type.bitwidth()
    unit = ir.Unit("unit")
    global_mem_base = unit.AddMem(ir.Mem("global_mem_base",
                                         ir.Const(o.DK.U32, bit_width // 8), o.MEM_KIND.RW))
    GenerateInitGlobalVarsFun(mod, unit, addr_type)
    GenerateInitDataFun(mod, unit, global_mem_base, addr_type)

    return unit


if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.DEBUG)
    logging.info(f"Reading {sys.argv[1]}")
    with open(sys.argv[1], "rb") as fin:
        unit = Translate(wasm.Module.read(fin), o.DK.A32)
        print("\n".join(serialize.UnitRenderToASM(unit)))
