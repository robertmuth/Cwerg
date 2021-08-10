#!/usr/bin/python3

import typing
import enum


###########################################################
# Opcodes
# https://webassembly.github.io/spec/core/binary/instructions.html#control-instructions
############################################################

@enum.unique
class ARG_TYPE(enum.IntEnum):
    INVALID = 0
    UINT = 1
    BYTE1_ZERO = 2
    BYTE4 = 3
    BYTE8 = 4
    LOCAL_IDX = 5
    GLOBAL_IDX = 6
    TABLE_IDX = 7
    ELEM_IDX = 8
    FUNC_IDX = 9
    TYPE_IDX = 10
    DATA_IDX = 11
    LABEL_IDX = 12
    VEC_LABEL_IDX = 13
    BLOCK_TYPE = 14
    SINT = 15


@enum.unique
class FLAGS(enum.IntFlag):

    SIGNED = 1
    UNSIGNED = 2
    UNARY = 4


@enum.unique
class OPC_KIND(enum.Enum):
    BLOCK_START = 1
    BLOCK_END = 2
    CONST = 3
    STORE = 4
    LOAD = 5
    CMP = 6
    UNARY = 7
    ALU = 8
    CFG = 9
    VAR = 10
    TABLE = 11
    MEM = 12
    CONV = 13
    MISC = 14


###########################################################
# OPCODES
############################################################
def op_type(name):
    x = name.split(".")[0]
    if x in {"i32", "i64", "f32", "f64"}:
        return x
    else:
        return None


class Opcode:
    Table: typing.Dict[int, "Opcode"] = {}

    def __init__(self, no, name, kind, arg1=ARG_TYPE.INVALID, arg2=ARG_TYPE.INVALID, arg3=ARG_TYPE.INVALID, flags=FLAGS(0)):
        # assert flags != 0, f"{name}: no flags set"
        self.no = no
        self.name = name
        self.basename = name.split(".")[-1]
        self.kind = kind
        self.flags = flags
        self.op_type = op_type(name)
        self.args = [a for a in (arg1, arg2, arg3) if a != ARG_TYPE.INVALID]
        assert no not in Opcode.Table
        Opcode.Table[no] = self


def OpConst(no, name, arg):
    return Opcode(no, name, OPC_KIND.CONST, arg)


def OpVar(no, name, arg):
    return Opcode(no, name, OPC_KIND.VAR, arg)


def OpCmp(no, name, flags=FLAGS(0)):
    return Opcode(no, name, OPC_KIND.CMP, flags=flags)


def OpAlu(no, name, flags=FLAGS(0)):
    return Opcode(no, name, OPC_KIND.ALU, flags=flags)


def OpLoad(no, name, flags=FLAGS(0)):
    return Opcode(no, name, OPC_KIND.LOAD, ARG_TYPE.UINT, ARG_TYPE.UINT, flags=flags)


def OpStore(no, name):
    return Opcode(no, name, OPC_KIND.STORE, ARG_TYPE.UINT, ARG_TYPE.UINT)


def OpTable(no, name, arg1, arg2=ARG_TYPE.INVALID):
    return Opcode(no, name, OPC_KIND.TABLE, arg1, arg2)


def OpMem(no, name, arg1, arg2=ARG_TYPE.INVALID, arg3=ARG_TYPE.INVALID):
    return Opcode(no, name, OPC_KIND.MEM, arg1, arg2, arg3)


def OpCfg(no, name, arg1=ARG_TYPE.INVALID, arg2=ARG_TYPE.INVALID):
    return Opcode(no, name, OPC_KIND.CFG, arg1, arg2)


def OpConv(no, name):
    return Opcode(no, name, OPC_KIND.CONV)


def OpBlk(no, name, arg1=ARG_TYPE.INVALID):
    return Opcode(no, name, OPC_KIND.BLOCK_START, arg1)


# control Instructions
UNREACHABLE = OpCfg(0x00, 'unreachable')
NOP = OpCfg(0x01, 'nop')

BLOCK = OpBlk(0x02, 'block', ARG_TYPE.BLOCK_TYPE)
LOOP = OpBlk(0x03, 'loop', ARG_TYPE.BLOCK_TYPE)
IF = OpBlk(0x04, 'if', ARG_TYPE.BLOCK_TYPE)
ELSE = OpCfg(0x05, 'else')
END = Opcode(0x0b, 'end', OPC_KIND.BLOCK_END)

BR = OpCfg(0x0c, 'br', ARG_TYPE.LABEL_IDX)
BR_IF = OpCfg(0x0d, 'br_if', ARG_TYPE.LABEL_IDX)
BR_TABLE = OpCfg(0x0e, 'br_table', ARG_TYPE.VEC_LABEL_IDX, ARG_TYPE.LABEL_IDX)
RETURN = OpCfg(0x0f, 'return')
CALL = OpCfg(0x10, 'call', ARG_TYPE.FUNC_IDX)
CALL_INDIRECT = OpCfg(0x11, 'call_indirect', ARG_TYPE.TYPE_IDX, ARG_TYPE.TABLE_IDX)

# parametric Instructions
DROP = Opcode(0x1a, 'drop', OPC_KIND.MISC)
SELECT = Opcode(0x1b, 'select', OPC_KIND.MISC)
# op(0x1c, 'select_val')


LOCAL_GET = OpVar(0x20, 'local.get', ARG_TYPE.LOCAL_IDX)
LOCAL_SET = OpVar(0x21, 'local.set', ARG_TYPE.LOCAL_IDX)
LOCAL_TEE = OpVar(0x22, 'local.tee', ARG_TYPE.LOCAL_IDX)
GLOBAL_GET = OpVar(0x23, 'global.get', ARG_TYPE.GLOBAL_IDX)
GLOBAL_SET = OpVar(0x24, 'global.set', ARG_TYPE.GLOBAL_IDX)

OpTable(0x25, "table.get", ARG_TYPE.TABLE_IDX)
OpTable(0x26, "table.set", ARG_TYPE.TABLE_IDX)
OpTable(0x0cfc, "table.init", ARG_TYPE.ELEM_IDX, ARG_TYPE.TABLE_IDX)
OpTable(0x0dfc, "table.drop", ARG_TYPE.ELEM_IDX)
OpTable(0x0efc, "table.copy", ARG_TYPE.TABLE_IDX, ARG_TYPE.TABLE_IDX)
OpTable(0x0ffc, "table.grow", ARG_TYPE.TABLE_IDX)
OpTable(0x10fc, "table.size", ARG_TYPE.TABLE_IDX)
OpTable(0x11fc, "table.fill", ARG_TYPE.TABLE_IDX)

OpLoad(0x28, 'i32.load')
OpLoad(0x29, 'i64.load')
OpLoad(0x2a, 'f32.load')
OpLoad(0x2b, 'f64.load')
OpLoad(0x2c, 'i32.load8_s')
OpLoad(0x2d, 'i32.load8_u', FLAGS.UNSIGNED)
OpLoad(0x2e, 'i32.load16_s')
OpLoad(0x2f, 'i32.load16_u', FLAGS.UNSIGNED)
OpLoad(0x30, 'i64.load8_s')
OpLoad(0x31, 'i64.load8_u', FLAGS.UNSIGNED)
OpLoad(0x32, 'i64.load16_s')
OpLoad(0x33, 'i64.load16_u')
OpLoad(0x34, 'i64.load32_s')
OpLoad(0x35, 'i64.load32_u', FLAGS.UNSIGNED)

OpStore(0x36, 'i32.store')
OpStore(0x37, 'i64.store')
OpStore(0x38, 'f32.store')
OpStore(0x39, 'f64.store')
OpStore(0x3a, 'i32.store8')
OpStore(0x3b, 'i32.store16')
OpStore(0x3c, 'i64.store8')
OpStore(0x3d, 'i64.store16')
OpStore(0x3e, 'i64.store32')

OpMem(0x3f, 'memory.size', ARG_TYPE.BYTE1_ZERO)
OpMem(0x40, 'memory.grow', ARG_TYPE.BYTE1_ZERO)
OpMem(0x08fc, 'memory.init', ARG_TYPE.DATA_IDX, ARG_TYPE.BYTE1_ZERO)
OpMem(0x09fc, 'data.drop', ARG_TYPE.DATA_IDX)
OpMem(0x0afc, 'memory.copy', ARG_TYPE.BYTE1_ZERO, ARG_TYPE.BYTE1_ZERO)
OpMem(0x0bfc, 'memory.fill', ARG_TYPE.BYTE1_ZERO)

# numeric instructions
# Note, potential issue with floating point constants:
# https://stackoverflow.com/questions/47961537/webassembly-f32-const-nan0x200000-means-0x7fa00000-or-0x7fe00000
I32_CONST = OpConst(0x41, 'i32.const', ARG_TYPE.SINT)
I64_CONST = OpConst(0x42, 'i64.const', ARG_TYPE.SINT)
F32_CONST = OpConst(0x43, 'f32.const', ARG_TYPE.BYTE4)
F64_CONST = OpConst(0x44, 'f64.const', ARG_TYPE.BYTE8)

OpCmp(0x45, 'i32.eqz', FLAGS.UNARY)
OpCmp(0x50, 'i64.eqz', FLAGS.UNARY)

OpCmp(0x46, 'i32.eq')
OpCmp(0x47, 'i32.ne')
OpCmp(0x48, 'i32.lt_s')
OpCmp(0x49, 'i32.lt_u', FLAGS.UNSIGNED)
OpCmp(0x4a, 'i32.gt_s')
OpCmp(0x4b, 'i32.gt_u', FLAGS.UNSIGNED)
OpCmp(0x4c, 'i32.le_s')
OpCmp(0x4d, 'i32.le_u', FLAGS.UNSIGNED)
OpCmp(0x4e, 'i32.ge_s')
OpCmp(0x4f, 'i32.ge_u')
OpCmp(0x51, 'i64.eq')
OpCmp(0x52, 'i64.ne')
OpCmp(0x53, 'i64.lt_s')
OpCmp(0x54, 'i64.lt_u', FLAGS.UNSIGNED)
OpCmp(0x55, 'i64.gt_s')
OpCmp(0x56, 'i64.gt_u', FLAGS.UNSIGNED)
OpCmp(0x57, 'i64.le_s')
OpCmp(0x58, 'i64.le_u', FLAGS.UNSIGNED)
OpCmp(0x59, 'i64.ge_s')
OpCmp(0x5a, 'i64.ge_u')
OpCmp(0x5b, 'f32.eq')
OpCmp(0x5c, 'f32.ne')
OpCmp(0x5d, 'f32.lt')
OpCmp(0x5e, 'f32.gt')
OpCmp(0x5f, 'f32.le')
OpCmp(0x60, 'f32.ge')
OpCmp(0x61, 'f64.eq')
OpCmp(0x62, 'f64.ne')
OpCmp(0x63, 'f64.lt')
OpCmp(0x64, 'f64.gt')
OpCmp(0x65, 'f64.le')
OpCmp(0x66, 'f64.ge')

OpAlu(0x67, 'i32.clz', FLAGS.UNARY)
OpAlu(0x68, 'i32.ctz', FLAGS.UNARY)
OpAlu(0x69, 'i32.popcnt', FLAGS.UNARY)

OpAlu(0x6a, 'i32.add')
OpAlu(0x6b, 'i32.sub')
OpAlu(0x6c, 'i32.mul')
OpAlu(0x6d, 'i32.div_s')
OpAlu(0x6e, 'i32.div_u', FLAGS.UNSIGNED)
OpAlu(0x6f, 'i32.rem_s')
OpAlu(0x70, 'i32.rem_u', FLAGS.UNSIGNED)
OpAlu(0x71, 'i32.and')
OpAlu(0x72, 'i32.or')
OpAlu(0x73, 'i32.xor')
OpAlu(0x74, 'i32.shl')
OpAlu(0x75, 'i32.shr_s')
OpAlu(0x76, 'i32.shr_u', FLAGS.UNSIGNED)
OpAlu(0x77, 'i32.rotl')
OpAlu(0x78, 'i32.rotr')

OpAlu(0x79, 'i64.clz')
OpAlu(0x7a, 'i64.ctz')
OpAlu(0x7b, 'i64.popcnt')

OpAlu(0x7c, 'i64.add')
OpAlu(0x7d, 'i64.sub')
OpAlu(0x7e, 'i64.mul')
OpAlu(0x7f, 'i64.div_s')
OpAlu(0x80, 'i64.div_u', FLAGS.UNSIGNED)
OpAlu(0x81, 'i64.rem_s')
OpAlu(0x82, 'i64.rem_u', FLAGS.UNSIGNED)
OpAlu(0x83, 'i64.and')
OpAlu(0x84, 'i64.or')
OpAlu(0x85, 'i64.xor')
OpAlu(0x86, 'i64.shl')
OpAlu(0x87, 'i64.shr_s')
OpAlu(0x88, 'i64.shr_u', FLAGS.UNSIGNED)
OpAlu(0x89, 'i64.rotl')
OpAlu(0x8a, 'i64.rotr')

OpAlu(0x8b, 'f32.abs', FLAGS.UNARY)
OpAlu(0x8c, 'f32.neg', FLAGS.UNARY)
OpAlu(0x8d, 'f32.ceil', FLAGS.UNARY)
OpAlu(0x8e, 'f32.floor', FLAGS.UNARY)
OpAlu(0x8f, 'f32.trunc', FLAGS.UNARY)
OpAlu(0x90, 'f32.nearest', FLAGS.UNARY)
OpAlu(0x91, 'f32.sqrt', FLAGS.UNARY)

OpAlu(0x92, 'f32.add')
OpAlu(0x93, 'f32.sub')
OpAlu(0x94, 'f32.mul')
OpAlu(0x95, 'f32.div')
OpAlu(0x96, 'f32.min')
OpAlu(0x97, 'f32.max')

OpAlu(0x98, 'f32.copysign', FLAGS.UNARY)
OpAlu(0x99, 'f64.abs', FLAGS.UNARY)
OpAlu(0x9a, 'f64.neg', FLAGS.UNARY)
OpAlu(0x9b, 'f64.ceil', FLAGS.UNARY)
OpAlu(0x9c, 'f64.floor', FLAGS.UNARY)
OpAlu(0x9d, 'f64.trunc', FLAGS.UNARY)
OpAlu(0x9e, 'f64.nearest', FLAGS.UNARY)
OpAlu(0x9f, 'f64.sqrt', FLAGS.UNARY)

OpAlu(0xa0, 'f64.add')
OpAlu(0xa1, 'f64.sub')
OpAlu(0xa2, 'f64.mul')
OpAlu(0xa3, 'f64.div')
OpAlu(0xa4, 'f64.min')
OpAlu(0xa5, 'f64.max')

OpAlu(0xa6, 'f64.copysign', FLAGS.UNARY)

OpConv(0xa7, 'i32.wrap_i64')
OpConv(0xa8, 'i32.trunc_f32_s')
OpConv(0xa9, 'i32.trunc_f32_u')
OpConv(0xaa, 'i32.trunc_f64_s')
OpConv(0xab, 'i32.trunc_f64_u')
OpConv(0xac, 'i64.extend_i32_s')
OpConv(0xad, 'i64.extend_i32_u')
OpConv(0xae, 'i64.trunc_f32_s')
OpConv(0xaf, 'i64.trunc_f32_u')
OpConv(0xb0, 'i64.trunc_f64_s')
OpConv(0xb1, 'i64.trunc_f64_u')
OpConv(0xb2, 'f32.convert_i32_s')
OpConv(0xb3, 'f32.convert_i32_u')
OpConv(0xb4, 'f32.convert_i64_s')
OpConv(0xb5, 'f32.convert_i64_u')
OpConv(0xb6, 'f32.demote_f64')
OpConv(0xb7, 'f64.convert_i32_s')
OpConv(0xb8, 'f64.convert_i32_u')
OpConv(0xb9, 'f64.convert_i64_s')
OpConv(0xba, 'f64.convert_i64_u')
OpConv(0xbb, 'f64.promote_f32')

OpConv(0xbc, 'i32.reinterpret_f32')
OpConv(0xbd, 'i64.reinterpret_f64')
OpConv(0xbe, 'f32.reinterpret_i32')
OpConv(0xbf, 'f64.reinterpret_i64')

if __name__ == '__main__':
    def dump():
        for no, opcode in sorted(Opcode.Table.items()):
            args = [a.name for a in opcode.args]
            print(f"{opcode.no:02x} {opcode.name:20} {' '.join(args)}  {int(opcode.flags):x}")


    dump()
