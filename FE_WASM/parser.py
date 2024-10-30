#!/bin/env python3

"""
Parser for WASM files

Spec:
https://webassembly.github.io/spec/core/syntax/types.html
"""

import logging
import struct
import io
import typing
import enum
import dataclasses
from FE_WASM.opcode_tab import Opcode, ARG_TYPE, FLAGS, OPC_KIND
from Util import parse


def read_bytes(r: typing.BinaryIO) -> bytes:
    n = parse.read_leb128(r)
    data = r.read(n)
    assert len(data) == n
    return data


def read_string(r: typing.BinaryIO) -> str:
    return read_bytes(r).decode()


def read_vec(r: typing.BinaryIO, cls) -> typing.List:
    n = parse.read_leb128(r)
    return [cls.read(r) for _ in range(n)]


############################################################
# TYPES
# https://webassembly.github.io/spec/core/binary/types.html
############################################################


@enum.unique
class NUM_TYPE(enum.IntEnum):
    F64 = 0x7c
    F32 = 0x7d
    I64 = 0x7e
    I32 = 0x7f


@enum.unique
class REF_TYPE(enum.IntEnum):
    EXTERNREF = 0x6f
    FUNCREF = 0x70


@enum.unique
class VAL_TYPE(enum.IntEnum):
    EXTERNREF = 0x6f
    FUNCREF = 0x70
    F64 = 0x7c
    F32 = 0x7d
    I64 = 0x7e
    I32 = 0x7f

    def is_32bit(self):
        return self is VAL_TYPE.I32 or self is VAL_TYPE.F32


@enum.unique
class MUT(enum.IntEnum):
    CONST = 0
    VAR = 1


@enum.unique
class EXTERN(enum.IntEnum):
    FUNCTION = 0
    TABLE = 1
    MEMORY = 2
    GLOBAL = 3


@dataclasses.dataclass(frozen=True)
class ResultType:
    types: typing.List[VAL_TYPE] = dataclasses.field(default_factory=list)

    @classmethod
    def read(cls, r: typing.BinaryIO):
        n = parse.read_leb128(r)
        return ResultType([VAL_TYPE(ord(r.read(1))) for _ in range(n)])


@dataclasses.dataclass(frozen=True)
class FunctionType:
    args: ResultType
    rets: ResultType

    @classmethod
    def read(cls, r: typing.BinaryIO):
        s = ord(r.read(1))
        assert s == 0x60
        return FunctionType(ResultType.read(r), ResultType.read(r))


@dataclasses.dataclass(frozen=True)
class Limits:
    min: int
    max: int

    @classmethod
    def read(cls, r: typing.BinaryIO):
        flag = ord(r.read(1))
        a_min = parse.read_leb128(r)
        a_max = parse.read_leb128(r) if flag else 0x00
        return Limits(a_min, a_max)


@dataclasses.dataclass(frozen=True)
class MemoryType:
    limits: Limits

    @classmethod
    def read(cls, r: typing.BinaryIO):
        return MemoryType(Limits.read(r))


@dataclasses.dataclass(frozen=True)
class TableType:
    element_type: ResultType
    limits: Limits

    @classmethod
    def read(cls, r: typing.BinaryIO):
        return TableType(REF_TYPE(ord(r.read(1))), Limits.read(r))


@dataclasses.dataclass(frozen=True)
class GlobalType:
    value_type: VAL_TYPE
    mut: MUT

    @classmethod
    def read(cls, r: typing.BinaryIO):
        return GlobalType(VAL_TYPE(ord(r.read(1))), MUT(ord(r.read(1))))


# https://webassembly.github.io/spec/core/syntax/types.html#external-types
ExternalType = typing.Union[FunctionType, TableType, MemoryType, GlobalType]


def ReadArg(r: typing.BinaryIO, at: ARG_TYPE) -> typing.Any:
    if at is ARG_TYPE.UINT:
        return parse.read_leb128(r)
    elif at is ARG_TYPE.SINT:
        return parse.read_leb128(r, True)
    elif at is ARG_TYPE.BYTE1_ZERO:
        return ord(r.read(1))
    elif at is ARG_TYPE.FLOAT:
        v = r.read(4)
        return struct.unpack("<f", v)[0]
    elif at is ARG_TYPE.DOUBLE:
        v = r.read(8)
        return struct.unpack("<d", v)[0]
    elif at is ARG_TYPE.LOCAL_IDX:
        return LocalIdx.read(r)
    elif at is ARG_TYPE.GLOBAL_IDX:
        return GlobalIdx.read(r)
    elif at is ARG_TYPE.TABLE_IDX:
        return TableIdx.read(r)
    elif at is ARG_TYPE.ELEM_IDX:
        return ElemIdx.read(r)
    elif at is ARG_TYPE.FUNC_IDX:
        return FuncIdx.read(r)
    elif at is ARG_TYPE.TYPE_IDX:
        return TypeIdx.read(r)
    elif at is ARG_TYPE.DATA_IDX:
        return DataIdx.read(r)
    elif at is ARG_TYPE.LABEL_IDX:
        return LabelIdx.read(r)
    elif at is ARG_TYPE.VEC_LABEL_IDX:
        return read_vec(r, LabelIdx)
    elif at is ARG_TYPE.BLOCK_TYPE:
        block_type = parse.read_leb128(r, True)
        if block_type >= 0:
            return TypeIdx(block_type)
        block_type += 0x80
        if block_type == 0x40:
            return None
        return VAL_TYPE(block_type)
    else:
        assert False


@dataclasses.dataclass(frozen=True)
class Instruction:
    opcode: Opcode
    args: typing.List[typing.Any]

    def __repr__(self):
        return f"{self.opcode.name} {' '.join([repr(a) for a in self.args])}"

    @classmethod
    def read(cls, r: typing.BinaryIO):
        opcode = Opcode.Table[ord(r.read(1))]
        args = [ReadArg(r, kind) for kind in opcode.args]
        return Instruction(opcode, args)


###########################################################
# INDICES
# https://webassembly.github.io/spec/core/binary/modules.html#indices
############################################################

class Idx(int):
    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'

    @classmethod
    def read(cls, r: typing.BinaryIO):
        return cls(parse.read_leb128(r))


class TypeIdx(Idx):
    pass


class FuncIdx(Idx):
    pass


class TableIdx(Idx):
    pass


class MemIdx(Idx):
    pass


class GlobalIdx(Idx):
    pass


class ElemIdx(Idx):
    pass


class DataIdx(Idx):
    pass


class LocalIdx(Idx):
    pass


class LabelIdx(Idx):
    pass


###########################################################
# SECTIONS Elements
# https://webassembly.github.io/spec/core/binary/modules.html#sections
############################################################

ImportDesc = typing.Union[TypeIdx, TableType, MemoryType, GlobalType]


@dataclasses.dataclass(frozen=True)
class Import:
    module: str
    name: str
    desc: ImportDesc

    @classmethod
    def read(cls, r: typing.BinaryIO):
        module = read_string(r)
        name = read_string(r)
        kind = EXTERN(ord(r.read(1)))
        desc = {
            EXTERN.FUNCTION: TypeIdx.read,
            EXTERN.TABLE: TableType.read,
            EXTERN.MEMORY: MemoryType.read,
            EXTERN.GLOBAL: GlobalType.read,
        }[kind](r)
        return Import(module, name, desc)


@dataclasses.dataclass(frozen=True)
class Table:
    table_type: TableType

    @classmethod
    def read(cls, r: typing.BinaryIO):
        return Table(TableType.read(r))


@dataclasses.dataclass(frozen=True)
class Mem:
    mem_type: MemoryType

    @classmethod
    def read(cls, r: typing.BinaryIO):
        return Mem(MemoryType.read(r))


@dataclasses.dataclass(frozen=True)
class Expression:
    instructions: typing.List[Instruction]

    def __repr__(self):
        return "\n".join([repr(i) for i in self.instructions])

    @classmethod
    def read(cls, r: typing.BinaryIO):
        instructions = []
        nesting = 1
        while True:
            i = Instruction.read(r)
            # print ("@@", nesting, i)
            instructions.append(i)
            if i.opcode.kind is OPC_KIND.BLOCK_START:
                nesting += 1
            if i.opcode.kind is OPC_KIND.BLOCK_END:
                nesting -= 1
            if nesting == 0:
                break

        return Expression(instructions)


@dataclasses.dataclass(frozen=True)
class Glob:
    global_type: GlobalType
    expr: Expression

    @classmethod
    def read(cls, r: typing.BinaryIO):
        return Glob(GlobalType.read(r), Expression.read(r))


@dataclasses.dataclass(frozen=True)
class Export:
    name: str
    desc: typing.Union[FuncIdx, TableIdx, MemIdx, GlobalIdx]

    @classmethod
    def read(cls, r: typing.BinaryIO):
        name = read_string(r)
        kind = EXTERN(ord(r.read(1)))
        desc = {
            EXTERN.FUNCTION: FuncIdx.read,
            EXTERN.TABLE: TableIdx.read,
            EXTERN.MEMORY: MemIdx.read,
            EXTERN.GLOBAL: GlobalIdx.read,
        }[kind](r)
        return Export(name, desc)


@dataclasses.dataclass(frozen=True)
class Locals:
    count: int
    kind: NUM_TYPE

    @classmethod
    def read(cls, r: typing.BinaryIO):
        count = parse.read_leb128(r)
        kind = VAL_TYPE(ord(r.read(1)))
        return Locals(count, kind)


@dataclasses.dataclass(frozen=True)
class Code:
    locals_list: typing.List[Locals]
    expr: Expression

    def __repr__(self):
        return f"locals: {self.locals_list}\nexpr:\n{self.expr}"

    @classmethod
    def read(cls, rr: typing.BinaryIO):
        r = io.BytesIO(read_bytes(rr))
        local_list = read_vec(r, Locals)
        expr = Expression.read(r)
        rest = r.read(-1)
        if rest:
            raise Exception(f'not all code data was for Func: {rest}')
        return Code(local_list, expr)


@dataclasses.dataclass(frozen=True)
class Data:
    memory_index: typing.Optional[MemIdx]
    offset: typing.Optional[Expression]
    init: bytes

    @classmethod
    def read(cls, r: typing.BinaryIO):
        flags = ord(r.read(1))
        if flags == 0:
            return Data(MemIdx(0), Expression.read(r), read_bytes(r))
        elif flags == 1:
            # can this still happen?
            return Data(None, None, read_bytes(r))
        elif flags == 2:
            return Data(MemIdx.read(r), Expression.read(r), read_bytes(r))
        else:
            assert False


@dataclasses.dataclass(frozen=True)
class Elem:
    flags: int
    expr: Expression
    funcidxs: typing.List[FuncIdx]

    @classmethod
    def read(cls, r: typing.BinaryIO):
        flags = ord(r.read(1))
        if flags == 0:
            expr = Expression.read(r)
            funcidxs = read_vec(r, FuncIdx)
            return Elem(flags, expr, funcidxs)
        else:
            assert False, f"NYI {flags}"
        return Elem(flags)


###########################################################
# SECTIONS
# https://webassembly.github.io/spec/core/binary/modules.html#sections
############################################################
@enum.unique
class SECTION_ID(enum.IntEnum):
    CUSTOM = 0x0
    TYPE = 0x1
    IMPORT = 0x2
    FUNCTION = 0x3
    TABLE = 0x4
    MEMORY = 0x5
    GLOBAL = 0x6
    EXPORT = 0x7
    START = 0x8
    ELEMENT = 0x9
    CODE = 0xa
    DATA = 0xb
    DATA_COUNT = 0xc


@dataclasses.dataclass(frozen=True)
class Section:
    no: SECTION_ID
    # usually a list except for Custom and Start Sections
    items: typing.Any


_sec_id_to_reader = {
    SECTION_ID.CUSTOM: lambda r: (read_string(r), bytes(r.read(-1))),
    SECTION_ID.TYPE: lambda r: read_vec(r, FunctionType),
    SECTION_ID.IMPORT: lambda r: read_vec(r, Import),
    SECTION_ID.FUNCTION: lambda r: read_vec(r, TypeIdx),
    SECTION_ID.TABLE: lambda r: read_vec(r, Table),
    SECTION_ID.MEMORY: lambda r: read_vec(r, Mem),
    SECTION_ID.GLOBAL: lambda r: read_vec(r, Glob),
    SECTION_ID.EXPORT: lambda r: read_vec(r, Export),
    SECTION_ID.START: lambda r: FuncIdx.read(r),
    SECTION_ID.ELEMENT: lambda r: read_vec(r, Elem),
    SECTION_ID.CODE: lambda r: read_vec(r, Code),
    SECTION_ID.DATA: lambda r: read_vec(r, Data),
    SECTION_ID.DATA_COUNT: lambda r: 0,
}


@dataclasses.dataclass(frozen=True)
class Function:
    name: str
    func_type: FunctionType
    impl: typing.Union[Code, Import]


def ExtractFunctions(sections, fun_name_map) -> typing.List[Function]:
    out: typing.List[Function] = []
    import_sec = sections.get(SECTION_ID.IMPORT)
    type_sec = sections.get(SECTION_ID.TYPE)

    all_names = set()

    if import_sec:
        for i in import_sec.items:
            if isinstance(i.desc, TypeIdx):
                fun_name = f"${i.module}${i.name}"
                # HACK
                fun_name = fun_name.replace("wasi_snapshot_preview1", "wasi")
                fun_name = fun_name.replace("wasi_unstable", "wasi")
                assert fun_name not in all_names
                all_names.add(fun_name)
                out.append(Function(fun_name, type_sec.items[int(i.desc)], i))

    function_sec = sections.get(SECTION_ID.FUNCTION)
    code_sec = sections.get(SECTION_ID.CODE)

    if function_sec:
        start_index = len(out)
        assert len(code_sec.items) == len(function_sec.items)
        names = [f"$fun_{i + len(out)}" for i in range(len(code_sec.items))]
        for i in range(len(names)):
            name = fun_name_map.get(i + start_index)
            if name:
                name = name.replace("undefined:", "")
                if "(" in name:
                    name = name.split("(")[0]
                if " " in name:
                    name = name.split(" ")[0]
                names[i] = "_" + name
        export_sec = sections.get(SECTION_ID.EXPORT)
        if export_sec:
            for e in export_sec.items:
                if isinstance(e.desc, FuncIdx):
                    names[int(e.desc) - start_index] = e.name

        for n, (c, f) in enumerate(zip(code_sec.items, function_sec.items)):
            name = names[n]
            while name in all_names:
                name += "_"
            all_names.add(name)
            out.append(Function(name, type_sec.items[int(f)], c))

    return out


def ExtractFunNames(r: typing.BinaryIO) -> typing.Dict[int, str]:
    out = {}
    while True:
        map_id = r.read(1)
        if not map_id:
            break

        raw = read_bytes(r)
        content = io.BytesIO(raw)
        if ord(map_id) != 1:
            continue
        count = parse.read_leb128(content)
        for i in range(count):
            index = parse.read_leb128(content)
            name = read_string(content)
            out[index] = name
    return out


@dataclasses.dataclass(frozen=True)
class Module:
    version: typing.List[int]
    sections: typing.Dict[SECTION_ID, Section]
    custom: typing.Dict
    functions: typing.List[Function]

    @classmethod
    def read(cls, r: typing.BinaryIO):
        header = r.read(4)
        if header != b"\x00asm":
            raise Exception(f'no magic wasm header detected: {header}')
        version = list(r.read(4))
        # if version != [0x01, 0x00, 0x00, 0x00]:
        #    raise Exception(f'unknown binary version: {version}')

        sections: typing.Dict[SECTION_ID, Section] = {}
        custom = {}
        while True:
            id_byte = r.read(1)
            if not id_byte:
                break
            sec_id = SECTION_ID(ord(id_byte))
            raw = read_bytes(r)
            io_data = io.BytesIO(raw)
            logging.debug(
                f"Reading section of type {sec_id.name} size {len(raw)}")
            data = _sec_id_to_reader[sec_id](io_data)
            if sec_id is SECTION_ID.CUSTOM:
                assert isinstance(data, tuple)
                custom[data[0]] = data[1]
            else:
                sections[sec_id] = Section(sec_id, data)
            # print (sections[sec_id])
            if io_data.read(1):
                raise Exception(
                    f'not all section data was consumed for {sec_id}')

        fun_name_map = {}
        if "name" in custom:
            fun_name_map = ExtractFunNames(io.BytesIO(custom["name"]))
        return Module(version, sections, custom, ExtractFunctions(sections, fun_name_map))


if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Reading {sys.argv[1]}")
    with open(sys.argv[1], "rb") as fin:
        mod = Module.read(fin)
        for sec_id, sec in sorted(mod.sections.items()):
            print(f"\nsection {sec_id.name}")
            # make  some exceptions in for section types where this does not work
            for n, item in enumerate(sec.items):
                print(f"{n} {item}")
        for key, val in mod.custom.items():
            print(f"CUSTOM: [{key}]")
            print(val)
        print("\nFunctions:")
        for n, f in enumerate(mod.functions):
            print(
                f"{n}: [{f.name:30}] {type(f.impl).__name__:15}  {f.func_type}")
