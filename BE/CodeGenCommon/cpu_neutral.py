
from IR import opcode_tab as o
from BE.Base import serialize
from BE.Base import ir


MEMKIND_TO_SECTION = {
    o.MEM_KIND.RO: "rodata",
    o.MEM_KIND.RW: "data",
    # bss missing
}


def MemCodeGenText(mem: ir.Mem, _mod: ir.Unit):
    yield f"# size {mem.Size()}"
    yield f".mem {mem.name} {mem.alignment} {MEMKIND_TO_SECTION[mem.kind]}"
    for d in mem.datas:
        if isinstance(d, ir.DataBytes):
            yield f"    .data {d.count} {serialize.EscapeCStyle(d.data)}"
        elif isinstance(d, ir.DataAddrFun):
            yield f"    .addr.fun {d.size} {d.fun.name}"
        elif isinstance(d, ir.DataAddrMem):
            yield f"    .addr.mem {d.size} {d.mem.name} 0x{d.offset:x}"
        else:
            assert False

    yield ".endmem"


def JtbCodeGenSimpleText(jtb: ir.Jtb, addr_size: int):
    yield f".localmem {jtb.name} {addr_size} rodata"
    for i in range(jtb.size):
        bbl = jtb.bbl_tab.get(i, jtb.def_bbl)
        yield f"    .addr.bbl {addr_size} {bbl.name}"
    yield ".endmem"
