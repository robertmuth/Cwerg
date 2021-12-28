"""This file implements all the basic abstractions:

Num: Number
Stk: Stack Region
Reg: Register
Ins: Instruction
Bbl: Basic Block
Jtb: Jump-Table
Fun: Function
Mem: (Heap) Memory Region
Mod: Module
"""

import collections
import dataclasses
import enum
import struct
from typing import List, Dict, Set, Optional, Any

from Base import opcode_tab as o


class ParseError(Exception):
    pass


############################################################
# Operand TYPE
############################################################


def BitWidth(n: int):
    """ compute the minimum bitwidth needed to represent and integer """
    if n == 0:
        return 0
    if n > 0:
        return n.bit_length()
    if n < 0:
        # two's-complement WITHOUT sign
        return (n + 1).bit_length()


_NUM_CONVERSION_STR = {
    o.DK.S8: "b",
    o.DK.S16: "h",
    o.DK.S32: "i",
    o.DK.S64: "q",

    o.DK.U8: "B",
    o.DK.U16: "H",
    o.DK.U32: "I",
    o.DK.U64: "Q",

    o.DK.F32: "f",
    o.DK.F64: "d",
}


@dataclasses.dataclass(init=True)
class Const:
    """Constant Number (arbitrary precision int or float)"""

    kind: o.DK
    value: Any

    def IsZero(self):
        # note this works for floats and ints
        return self.value == 0

    def IsOne(self):
        # note this works for floats and ints
        return self.value == 1

    def IsIntPowerOfTwo(self):
        return isinstance(self.value, int) and (
                (self.value & (self.value - 1)) == 0)

    def IntBinaryLog(self):
        n = self.value
        assert n > 0 and isinstance(n, int)
        count = -1
        while n > 0:
            count += 1
            n >>= 1
        return count

    # def IntBitWidth(self) -> int:
    #    assert not o.RegIsFloat(self.kind)
    #    return BitWidth(self.value)

    def ToBytes(self) -> bytes:
        return struct.pack("<" + _NUM_CONVERSION_STR[self.kind], self.value)

    def __repr__(self):
        return f"{self.value}:{self.kind.name}"


def ParseConst(value_str: str, kind: o.DK) -> Const:
    flavor = kind.flavor()
    if flavor is o.DK_FLAVOR_F:
        return Const(kind, float(value_str))

    bit_width = kind.bitwidth()
    x = int(value_str, 0)
    if flavor is o.DK_FLAVOR_U:
        assert x >= 0
        assert x < (1 << bit_width)
    elif x >= 0:
        assert x < (1 << (bit_width - 1))
    else:
        assert -x <= (1 << (bit_width - 1))

    return Const(kind, x)


def OffsetConst(value: int) -> Const:
    w = 1 + BitWidth(value)

    if w <= 8:
        kind = o.DK.S8 if value < 0 else o.DK.U8
    elif w <= 16:
        kind = o.DK.S16 if value < 0 else o.DK.U16
    elif w <= 32:
        kind = o.DK.S32 if value < 0 else o.DK.U32
    elif w <= 64:
        kind = o.DK.S64 if value < 0 else o.DK.U64
    else:
        assert False
    return Const(kind, value)


def ParseOffsetConst(value_str: str) -> Const:
    return OffsetConst(int(value_str, 0))


@dataclasses.dataclass
class Stk:
    """Stack region in a stack frame, count is number of bytes"""
    name: str
    count: int
    alignment: int
    # stack offset - will be set by Fun.AssignStackSlots
    slot: Optional[int] = None

    def __init__(self, name: str, alignment: int, count: int):
        assert alignment > 0
        self.name = name
        # TODO: consider keeping the Nums
        self.count = count
        self.alignment = alignment

    def __repr__(self):
        return f"[STK {self.name} {self.alignment} {self.count}]"


# forward declarations
INS_INVALID = None
BBL_INVALID = None


@dataclasses.dataclass(init=True)
class StackSlot:
    """CPU Register"""
    offset: int = 0


@dataclasses.dataclass(init=True)
class CpuReg:
    """CPU Register"""
    name: str
    no: int
    kind: int = 0

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other: "Reg"):
        return (self.kind, self.no) < (self.kind, other.no)


@enum.unique
class REG_FLAG(enum.Flag):
    GLOBAL = 1 << 1  # occurs in multiple bbls (ideally it also live across a bbl boundary)
    MULTI_DEF = 1 << 2  # has multiple definitions
    LAC = 1 << 3  # live across call
    IS_READ = 1 << 4  # is use at least once  (IS_WRITTEN is synthesized by reg.def_ins != INS_INVALID
    MULTI_READ = 1 << 5  # has multiple reads
    TWO_ADDRESS = 1 << 6  # used by x64 backend
    MARKED = 1 << 7


@dataclasses.dataclass(init=True)
class Reg:
    """Register"""
    name: str
    kind: o.DK
    cpu_reg: CpuReg = None
    flags: REG_FLAG = REG_FLAG(0)
    def_ins: "Ins" = INS_INVALID  # first definition used by reg_stats
    def_bbl: "Bbl" = BBL_INVALID  # first definition used by reg_stats

    def IsIntReg(self):
        flavor = self.kind.flavor()
        return flavor is o.DK_FLAVOR_U or flavor is o.DK_FLAVOR_S

    def HasCpuReg(self):
        return self.cpu_reg is not None

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        extra = f"@{self.cpu_reg.name}" if self.cpu_reg else ""
        return f"{self.name}:{self.kind.name}{extra}"

    def __lt__(self, other: "Reg"):
        return self.name < other.name


REG_INVALID = Reg("REG_INVALID", o.DK.INVALID)
CPU_REG_INVALID = CpuReg("CPU_REG_INVALID", -2, 1000)
CPU_REG_SPILL = CpuReg("CPU_REG_SPILL", -1, 1000)


# The top lattice element for reaching_defs analysis
# The bot lattice element is represented by not being in the REG_DEG_MAP


@dataclasses.dataclass()
class Ins:
    """Instruction"""

    opcode: o.Opcode
    operands: List[Any]
    operand_defs: List[Any]  # ir.INVALID, ir.Ins or ir.Bbl

    def __init__(self, opcode: o.Opcode, operands: List[Any]):
        self.Init(opcode, operands)

    def Init(self, opcode: o.Opcode, operands: List[Any]):
        assert len(operands) == len(opcode.operand_kinds), f"operand num mismatch for {opcode} {operands}"
        self.opcode = opcode
        self.operands = operands
        self.operand_defs = [INS_INVALID] * len(operands)
        return self

    # for reaching defs etc, this has cause subtle bugs
    def __eq__(self, other):
        assert False, "do not compare Ins directly. Use 'is' if appropriate"

    def __repr__(self):
        return f"[INS {self.opcode.name}]"


INS_INVALID = Ins(o.NOP, [])

# see documentation in reaching_defs
REG_DEF_MAP = Dict[Reg, Any]  # value is ir.INVALID, ir.Ins or ir.Bbl


def InsSwapOps(ins: Ins, a: int, b: int):
    ins.operands[a], ins.operands[b] = ins.operands[b], ins.operands[a]
    ins.operand_defs[a], ins.operand_defs[b] = ins.operand_defs[b], ins.operand_defs[a]


@dataclasses.dataclass()
class Bbl:
    """Basic Block"""
    name: str
    forward_declared: bool = False
    inss: List[Ins] = dataclasses.field(default_factory=list)
    edge_out: List["Bbl"] = dataclasses.field(default_factory=list)
    edge_in: List["Bbl"] = dataclasses.field(default_factory=list)
    live_out: Set[Reg] = dataclasses.field(default_factory=set)  # set of reg live at the end of the Bbl
    defs_in: Dict[Reg, Ins] = dataclasses.field(default_factory=dict)

    def AddIns(self, ins: Ins):
        self.inss.append(ins)

    def AddEdgeOut(self, succ: "Bbl"):
        succ.edge_in.append(self)
        self.edge_out.append(succ)

    def DelEdgeOut(self, succ: "Bbl"):
        succ.edge_in.remove(self)
        self.edge_out.remove(succ)

    def ReplaceEdgeOut(self, old_succ: "Bbl", new_succ: "Bbl"):
        # need to preserve cardinality
        for n, out in enumerate(self.edge_out):
            if out != old_succ:
                continue
            self.edge_out[n] = new_succ
            old_succ.edge_in.remove(self)
            new_succ.edge_in.append(self)

    def IsReturn(self):
        return self.inss and self.inss[-1].opcode.kind == o.OPC_KIND.RET

    def __repr__(self):
        forward = " FORWARD" if self.forward_declared else ""

        return f"[BBL {self.name}{forward} {len(self.inss)}  {self.live_out}]"


BBL_INVALID = Bbl("INVALID_BBL", forward_declared=True)


@dataclasses.dataclass()
class Jtb:
    """JumpTables"""

    name: str
    def_bbl: Bbl
    bbl_tab: Dict[int, Bbl]
    size: int

    def __repr__(self):
        return f"[JTB {self.name}]"


@enum.unique
class FUN_FLAG(enum.Flag):
    CFG_NOT_LINEAR = 1 << 1  # bra instructions have been removed
    LIVENESS_VALID = 1 << 2  # liveness info is valid
    STACK_FINALIZED = 1 << 3  # stack size must not change anymore (no more scratch regs!)


class Fun:
    """Function"""

    def __init__(self, name: str, kind=o.FUN_KIND.INVALID,
                 output_types=None, input_types=None):
        self.name = name
        self.kind: o.FUN_KIND = o.FUN_KIND.INVALID
        self.flags = FUN_FLAG(0)
        self.input_types: List[o.DK] = []
        self.output_types: List[o.DK] = []
        self.reg_syms: Dict[str, Reg] = {}
        # All regs mentioned in reg_syms are partioned in one of these:
        self.regs: List[Reg] = []
        #
        # basic block
        self.bbl_syms: Dict[str, Bbl] = {}
        self.bbls: List[Bbl] = []
        # jtb
        self.jtb_syms: Dict[str, Jtb] = {}
        self.jtbs: List[Jtb] = []
        # stack
        self.stk_syms: Dict[str, Stk] = {}
        self.stk_size = -1
        self.scratch_reg_id = 0
        # Liveness info: this is relevant after machine register allocation
        # (use) "used by function = parameters"
        self.cpu_live_in: List[CpuReg] = []
        # (def) "defined by function = results"
        self.cpu_live_out: List[CpuReg] = []
        # (def2) "potentially changed but no visible to caller = scratch"
        #        we usually use an approximation, i.e. caller-save regs
        self.cpu_live_clobber: List[CpuReg] = []

        if kind != o.FUN_KIND.INVALID:  # not  forward_declared
            self.Init(kind, output_types, input_types)

    def Init(self, kind: o.FUN_KIND, output_types, input_types):
        assert self.kind is o.FUN_KIND.INVALID
        assert kind is not o.FUN_KIND.INVALID
        self.kind = kind
        self.input_types = input_types
        self.output_types = output_types

    def FinalizeStackSlots(self):
        """Assigns stack-offsets to each stk location"""
        assert FUN_FLAG.STACK_FINALIZED not in self.flags
        slot = 0
        for _, stk in sorted(self.stk_syms.items()):
            slot += stk.alignment - 1
            slot = slot // stk.alignment * stk.alignment
            stk.slot = slot
            slot += stk.count
        self.stk_size = slot
        self.flags |= FUN_FLAG.STACK_FINALIZED

    def AddReg(self, reg: Reg):
        if reg.name in self.reg_syms:
            raise ParseError(f"duplicate register {reg.name}")
        self.reg_syms[reg.name] = reg
        self.regs.append(reg)
        return reg

    def FindOrAddCpuReg(self, cpu_reg: CpuReg, kind: o.DK) -> Reg:
        name = f"${cpu_reg.name}_{kind.name}"
        reg = self.reg_syms.get(name)
        if reg is None:
            reg = Reg(name, kind, cpu_reg)
            self.AddReg(reg)
        return reg

    def AddJtb(self, jtb: Jtb) -> Jtb:
        if jtb.name in self.jtb_syms:
            raise ParseError(f"duplicate Jtb {jtb.name}")
        self.jtb_syms[jtb.name] = jtb
        self.jtbs.append(jtb)
        return jtb

    def GetJbl(self, name: str) -> Jtb:
        return self.jtb_syms[name]

    def CreateSpillSlot(self, reg: Reg):
        size = Const(o.DK.U8, reg.kind.bitwidth() // 8)
        stk = Stk(reg.name + "_slot", size, size)
        self.AddStk(stk)
        return stk

    def GetScratchReg(self, kind: o.DK, purpose: str, add_kind_to_name) -> Reg:
        """README ME: This function should only be used before any register
         reallocation is done.
         The registers returned here are
         meant to be live within a bbl typically only between two instructions.
        Meaning: the register will be defined by instruction and only be used
         by the immediately following instruction"""
        assert not purpose.startswith("$")
        self.scratch_reg_id += 1
        name = f"${self.scratch_reg_id}_{purpose}"
        if add_kind_to_name:
            name += f"_{kind.name}"
        reg = Reg(name, kind)
        self.AddReg(reg)
        return reg

    def AddStk(self, stk: Stk):
        if stk.name in self.stk_syms:
            raise ParseError(f"duplicate Stk {stk.name}")
        self.stk_syms[stk.name] = stk

    def GetStk(self, name: str) -> Stk:
        return self.stk_syms[name]

    def MaybeGetStk(self, name: str):
        return self.stk_syms.get(name)

    def GetReg(self, name: str) -> Reg:
        return self.reg_syms[name]

    def MaybeGetReg(self, name: str) -> Reg:
        return self.reg_syms.get(name)

    def AddBbl(self, bbl: Bbl):
        if bbl.name in self.bbl_syms:
            raise ParseError(f"duplicate Bbl {bbl.name}")
        self.bbl_syms[bbl.name] = bbl
        self.bbls.append(bbl)
        return bbl

    def InitForwardDeclaredBbl(self, bbl):
        assert bbl.forward_declared
        bbl.forward_declared = False
        self.bbls.append(bbl)

    def GetBbl(self, name) -> Optional[Bbl]:
        return self.bbl_syms.get(name)

    def GetBblOrAddForwardDeclaration(self, name: str):
        bbl = self.bbl_syms.get(name)
        if bbl is None:
            bbl = Bbl(name, forward_declared=True)
            self.bbl_syms[name] = bbl
            # note we do not add it to self.bbls
        return bbl

    def render_signature(self) -> str:
        inputs = [r.name for r in self.input_types]
        outputs = [r.name for r in self.output_types]
        return f"IN: [{' '.join(inputs)}] -> OUT: [{' '.join(outputs)}]"

    def __str__(self):
        bbls = [b.name for b in self.bbls]
        return f"[FUN {self.name} {self.render_signature()}  BBLs: {bbls}]"

    def __repr__(self):
        return f"FUN[{self.name}] {self.kind.name}"


@dataclasses.dataclass()
class Mem:
    """Memory region in the rodata/data/tls/bss segment that must stay together"""

    name: str
    alignment: int
    kind: o.MEM_KIND
    datas: List[Any] = dataclasses.field(default_factory=list)

    def AddData(self, data):
        assert isinstance(data, (DataBytes, DataAddrMem, DataAddrFun))
        self.datas.append(data)

    def Size(self):
        return sum(d.size for d in self.datas)

    def __repr__(self):
        return f"[MEM {self.name} {self.alignment} {self.kind} {self.Size()}]"


@dataclasses.dataclass()
class DataBytes:
    count: int
    data: bytes
    size: int

    def __init__(self, count: int, data: bytes):
        assert isinstance(data, bytes)
        self.count: int = count
        self.data: bytes = data
        self.size: int = self.count * len(data)


@dataclasses.dataclass()
class DataAddrFun:
    size: int
    fun: Fun


@dataclasses.dataclass()
class DataAddrMem:
    size: int
    mem: Mem  # address being referenced
    offset: int


class Unit:

    def __init__(self, name: str):
        self.name = name
        self.funs: List[Fun] = []
        self.fun_syms: Dict[str, Fun] = {}
        self.mem_syms: Dict[str, Mem] = {}
        self.mems: List = []
        self._temp_name_count = 0

    def GetTempName(self) -> str:
        self._temp_name_count += 1
        return f"$temp_{self._temp_name_count}"

    def AddMem(self, mem: Mem):
        if mem.name in self.mem_syms:
            raise ParseError(f"duplicate Mem {mem.name}")
        self.mem_syms[mem.name] = mem
        self.mems.append(mem)
        return mem

    def GetMem(self, name) -> Mem:
        return self.mem_syms.get(name)

    def AddFun(self, fun: Fun):
        if fun.name in self.fun_syms:
            raise ParseError(f"duplicate Fun {fun.name}")
        self.funs.append(fun)
        self.fun_syms[fun.name] = fun
        return fun

    def InitForwardDeclaredFun(self, fun, kind, outputs, inputs):
        assert fun.kind == o.FUN_KIND.INVALID
        fun.Init(kind, outputs, inputs)
        self.funs.append(fun)

    def GetFun(self, name) -> Optional[Fun]:
        return self.fun_syms.get(name)

    def GetFunOrAddForwardDeclaration(self, name):
        fun = self.fun_syms.get(name)
        if fun is None:
            fun = Fun(name)  # forward declared
            self.fun_syms[name] = fun
            # note we do not add it to self.funs
        return fun

    def FindOrAddConstMem(self, num: Const):
        def MakeName(data: bytes, kind: o.DK) -> str:
            data_str = "_".join(f"{b:02x}" for b in data)
            return f"$const_{kind.name}_{data_str}"

        data = num.ToBytes()
        name = MakeName(data, num.kind)
        mem = self.mem_syms.get(name)
        if mem:
            return mem
        mem = Mem(name, len(data), o.MEM_KIND.RO)
        mem.AddData(DataBytes(1, data))
        self.AddMem(mem)
        return mem

    def AddData(self, data):
        mem = self.mems[-1]
        mem.AddData(data)

    def __str__(self):
        return f"{self.name} FUNS: {self.fun_syms.keys()}"


def UnitCheckCompatibility(
        unit: Unit,
        allowed_reg_kinds: Set,
        allowed_ins_groups: Set):
    for fun in unit.funs:
        for reg in fun.regs:
            assert reg.kind in allowed_reg_kinds
            for bbl in fun.bbls:
                for ins in bbl.inss:
                    assert ins.opcode.group in allowed_ins_groups


# Many of the helpers below make use of instruction transformer which must
# return an Optional[List[Ins]. The result will be used as follows:
# None: leave the current Ins as is, note that the Ins may have been change by the transformer
# List[Ins]: replace the current Ins with the list, an empty List means
# the Ins will be dropped


def BblGenericRewrite(bbl: Bbl, fun: Fun,
                      ins_transformer, **extra) -> int:
    """Ins at a time rewriter for Bbls"""
    count = 0
    inss: List[Ins] = []
    for ins in bbl.inss:
        new_inss = ins_transformer(ins, fun, **extra)
        if new_inss is None:
            new_inss = [ins]
        else:
            count += 1
        inss += new_inss
    bbl.inss = inss
    return count


def FunGenericRewrite(fun: Fun, ins_transformer, **extra) -> int:
    """Ins at a time rewriter for Funs"""
    count = 0
    for bbl in fun.bbls:
        count += BblGenericRewrite(bbl, fun, ins_transformer, **extra)
    return count


def BblGenericRewriteWithBbl(bbl: Bbl, fun: Fun, ins_transformer, **extra) -> int:
    """Ins at a time rewriter for Bbls"""
    count = 0
    inss: List[Ins] = []
    for ins in bbl.inss:
        new_inss = ins_transformer(ins, bbl, fun, **extra)
        if new_inss is None:
            new_inss = [ins]
        else:
            count += 1
        inss += new_inss
    bbl.inss = inss
    return count


def FunGenericRewriteWithBbl(fun: Fun, ins_transformer, **extra) -> int:
    """Ins at a time rewriter for Funs"""
    count = 0
    for bbl in fun.bbls:
        count += BblGenericRewriteWithBbl(bbl, fun, ins_transformer, **extra)
    return count


def BblGenericRewriteReverse(bbl: Bbl, fun: Fun,
                             ins_transformer, **extra) -> int:
    """Ins at a time rewriter for Bbls"""
    count = 0
    inss: List[Ins] = []
    for ins in reversed(bbl.inss):
        new_inss = ins_transformer(ins, fun, **extra)
        if new_inss is None:
            new_inss = [ins]
        else:
            count += 1
        inss += new_inss
    bbl.inss = list(reversed(inss))
    return count


def FunGenericRewriteReverse(
        fun: Fun,
        ins_transformer,
        **extra) -> int:
    """Ins at a time rewriter for Funs"""
    count = 0
    for bbl in reversed(fun.bbls):
        count += BblGenericRewriteReverse(bbl,
                                          fun, ins_transformer, **extra)
    return count


def FunGenericRewriteBbl(fun: Fun, bbl_transformer, **extra) -> int:
    """Ins at a time rewriter for Funs"""
    count = 0
    for bbl in fun.bbls:
        count += bbl_transformer(bbl, fun, **extra)
    return count


class FunInsKindHistogram:

    def __init__(self, fun: Fun):
        self.h: Dict[o.OPC_KIND, int] = collections.defaultdict(int)
        for bbl in fun.bbls:
            for ins in bbl.inss:
                self.h[ins.opcode.kind] += 1

    def is_leaf_fun(self):
        # we intentionally exclude IK_SYSCALL but maybe this should be
        # rethought
        return self.h[o.OPC_KIND.BSR] == 0 and self.h[o.OPC_KIND.JSR] == 0

    def has_stk_aliases(self):
        return self.h[o.OPC_KIND.LEA_IMM] == 0


def FunIsLeaf(fun) -> bool:
    for bbl in fun.bbls:
        for ins in bbl.inss:
            if ins.opcode is o.BSR or ins.opcode is o.JSR:
                return False
    return True
