
import logging
import re
import dataclasses

from FrontEnd import cwast

from typing import List, Dict, Tuple, Set, Optional, Union, Any

logger = logging.getLogger(__name__)


CanonType = str
NO_TYPE = None
STRINGIFIEDTYPE_RE = re.compile(r"^[a-zA-Z][_A-Za-z_0-9$,<>/]+$")


def is_mutable_def(node):
    if isinstance(node, cwast.Id):
        s = node.x_symbol
        if isinstance(s, (cwast.DefVar, cwast.DefGlobal)):
            return s.mut
    return False


def is_ref_def(node):
    if isinstance(node, cwast.Id):
        s = node.x_symbol
        return  isinstance(s, cwast.DefGlobal) or isinstance(s, cwast.DefVar) and s.ref
    return False


def align(x, a):
    return (x + a - 1) // a * a


def get_contained_type(cstr) -> CanonType:
    if isinstance(cstr, (cwast.TypeArray, cwast.TypeSlice)):
        return cstr.type
    else:
        assert False, f"unexpected type: {cstr}"


def get_array_dim(cstr: cwast.TypeArray) -> int:
    return cstr.size.x_value


def get_pointee(cstr: CanonType) -> CanonType:
    assert cstr.startswith("ptr"), f"expected pointer got {cstr}"
    return cstr.split("(", 1)[1][:-1]


def is_mutable(cstr: CanonType, actual_is_lvalue=False) -> bool:
    if isinstance(cstr, cwast.TypePtr):
        return cstr.mut
    elif isinstance(cstr, cwast.TypeSlice):
        return cstr.mut
    elif isinstance(cstr, cwast.TypeArray):
        return actual_is_lvalue
    else:
        assert False, f"unexpected node for mutable test: {cstr}"


def is_bool(cstr: CanonType) -> bool:
    if not isinstance(cstr, cwast.TypeBase):
        return False
    return cstr.base_type_kind is cwast.BASE_TYPE_KIND.BOOL


def is_void(cstr: CanonType) -> bool:
    return isinstance(cstr, cwast.TypeBase) and cstr.base_type_kind is cwast.BASE_TYPE_KIND.VOID

def is_void_or_wrapped_void(cstr: CanonType) -> bool:
    if isinstance(cstr, cwast.DefType):
        return is_void(cstr.type)
    return is_void(cstr)

def is_int(cstr: CanonType) -> bool:
    assert isinstance(cstr, cwast.TypeBase)
    return cstr.base_type_kind in cwast.BASE_TYPE_KIND_INT


def is_uint(cstr: CanonType) -> bool:
    assert isinstance(cstr, cwast.TypeBase)
    return cstr.base_type_kind in cwast.BASE_TYPE_KIND_UINT


def is_sint(cstr: CanonType) -> bool:
    assert isinstance(cstr, cwast.TypeBase)
    return cstr.base_type_kind in cwast.BASE_TYPE_KIND_SINT


def is_real(cstr: CanonType) -> bool:
    assert isinstance(cstr, cwast.TypeBase)
    return cstr.base_type_kind in cwast.BASE_TYPE_KIND_REAL


def is_number(cstr: CanonType) -> bool:
    if not isinstance(cstr, cwast.TypeBase):
        return False
    kind = cstr.base_type_kind
    return kind in cwast.BASE_TYPE_KIND_REAL or kind in cwast.BASE_TYPE_KIND_INT


def is_compatible(actual: CanonType, expected: CanonType, actual_is_lvalue=False) -> bool:
    if actual == expected:
        return True

    if isinstance(actual, cwast.TypeSlice) and isinstance(expected, cwast.TypeSlice):
        if actual.type == expected.type and actual.mut or not expected.mut:
            return True

    if isinstance(actual, cwast.TypeArray) and isinstance(expected, cwast.TypeSlice):
        # TODO: check "ref"
        return actual.type == expected.type and (not expected.mut or actual_is_lvalue)

    if not isinstance(expected, cwast.TypeSum):
        return False

    expected_children = set(expected.types)

    if isinstance(actual, cwast.TypeSum):
        return set(actual.types).issubset(expected_children)
    else:
        return actual in expected_children


_BASE_TYPE_MAP = {
    cwast.BASE_TYPE_KIND.SINT: ["S64"],
    cwast.BASE_TYPE_KIND.S8: ["S8"],
    cwast.BASE_TYPE_KIND.S16: ["S16"],
    cwast.BASE_TYPE_KIND.S32: ["S32"],
    cwast.BASE_TYPE_KIND.S64: ["S64"],
    #
    cwast.BASE_TYPE_KIND.UINT: ["U64"],
    cwast.BASE_TYPE_KIND.U8: ["U8"],
    cwast.BASE_TYPE_KIND.U16: ["U16"],
    cwast.BASE_TYPE_KIND.U32: ["U32"],
    cwast.BASE_TYPE_KIND.U64: ["U64"],
    #
    cwast.BASE_TYPE_KIND.R32: ["F32"],
    cwast.BASE_TYPE_KIND.R64: ["F64"],
    #
    cwast.BASE_TYPE_KIND.BOOL: ["U8"],
    cwast.BASE_TYPE_KIND.VOID: [],
    cwast.BASE_TYPE_KIND.NORET: [],
}


def _get_size_and_offset_for_sum_type(node: cwast.TypeSum, ptr_size):
    num_void = 0
    num_pointer = 0
    num_other = 0
    max_size = 0
    max_alignment = 1
    for t in node.types:
        if isinstance(t, cwast.DefType):
            assert t.wrapped
            t = t.type
        if is_void(t):
            num_void += 1
        elif isinstance(t, cwast.TypePtr):
            num_pointer += 1
            max_size = max(max_size, ptr_size)
            max_alignment = max(max_alignment, ptr_size)
        else:
            num_other += 1
            max_size = max(max_size, t.x_size)
            max_alignment = max(max_alignment, t.x_alignment)
    if num_other == 0 and num_pointer == 1:
        # special hack for pointer + error-code
        return ptr_size, ptr_size
    max_alignment = max(max_alignment, 2)
    size = align(2, max_alignment)
    return size + max_size, max_alignment


TYPE_ID_REG_TYPE = "U16"


def MakeAstTypeNodeFromCanonical(node, srcloc):
    clone = dataclasses.replace(node)
    #
    clone.x_srcloc = srcloc
    clone.x_type = node
    clone.x_size = None
    clone.x_alignement = None
    clone.x_offset = None

    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            setattr(clone, c, MakeAstTypeNodeFromCanonical(
                getattr(node, c), srcloc))
        elif nfd.kind is cwast.NFK.LIST:
            out = [cwast.MakeAstTypeNodeFromCanonical(cc, srcloc)
                   for cc in getattr(node, c)]
            setattr(clone, c, out)
    return clone


class TypeCorpus:
    """The type corpus uniquifies types

    It does so by representing each type with a string (basically a serialized
    version of type like "array<ptr<u32>,128>").
    That serialized version is mapped back to a structural version expressed
    using AST nodes.
    """

    def __init__(self, uint_kind: cwast.BASE_TYPE_KIND, sint_kind: cwast.BASE_TYPE_KIND):
        self.uint_kind: cwast.BASE_TYPE_KIND = uint_kind  # also used for ptr cast to ints
        self.sint_kind: cwast.BASE_TYPE_KIND = sint_kind
        # TODO
        self._addr_reg_type = "A64"
        self._code_reg_type = "C64"

        self.wrapped_curr = 1
        # maps to ast
        self.topo_order = []
        self.corpus: Dict[str, Any] = {}  # name to canonical type
        self._canon_name: Dict[Any, str] = {}   # canonical type to name
        # canonical type to Cwerg IR registers
        self._register_types: Dict[int, List[Any]] = {}

        for kind in cwast.BASE_TYPE_KIND:
            if kind.name in ("INVALID", "UINT", "SINT"):
                continue
            t = self.insert_base_type(kind)

    def canon_name(self, node):
        return self._canon_name.get(node, "@@ BAD CANONICAL TYPE @@")

    def register_types(self, node):
        return self._register_types[node]

    def _get_register_type_for_sum_type(self, node: cwast.TypeSum):
        num_void = 0
        scalars = []
        largest_by_kind = {}
        largest = 0
        for t in node.types:
            if isinstance(t, cwast.DefType):
                assert t.wrapped
                t = t.type
            if is_void(t):
                num_void += 1
                continue
            regs = self._register_types[t]
            if regs is None or len(regs) > 1:
                return None
            scalars.append(t)
            k = regs[0][0]
            size = int(regs[0][1:])
            largest_by_kind[k] = max(largest_by_kind.get(k, 0), size)
            largest = max(largest, size)
        # special hack for pointer + error-code
        if len(scalars) == 1 and isinstance(t, cwast.TypePtr):
            return self._register_types[t]

        k = next(iter(largest_by_kind)) if len(largest_by_kind) == 1 else "U"
        return [f"U{largest}", TYPE_ID_REG_TYPE]

    def get_register_type(self, ctype) -> Optional[List[str]]:
        """As long as a type can fit into no more than two regs it will have
        register representation which is also how it will be past in function calls.
        """
        if isinstance(ctype, cwast.TypeBase):
            return _BASE_TYPE_MAP.get(ctype.base_type_kind)
        elif isinstance(ctype, cwast.TypePtr):
            return [self._addr_reg_type]
        elif isinstance(ctype, cwast.TypeSlice):
            return [self._addr_reg_type] + _BASE_TYPE_MAP[self.uint_kind]
        elif isinstance(ctype, cwast.DefRec):
            fields = [f for f in ctype.fields if isinstance(f, cwast.RecField)]
            if len(fields) == 1:
                return self.get_register_type(fields[0].type.x_type)
            elif len(fields) == 2:
                a = self.get_register_type(fields[0].type.x_type)
                b = self.get_register_type(fields[1].type.x_type)
                if a is not None and b is not None and len(a) + len(b) <= 2:
                    return a + b
            else:
                return None
        elif isinstance(ctype, cwast.TypeArray):
            return None
        elif isinstance(ctype, cwast.DefEnum):
            return _BASE_TYPE_MAP[ctype.base_type_kind]
        elif isinstance(ctype, cwast.TypeSum):
            return self._get_register_type_for_sum_type(ctype)
        elif isinstance(ctype, cwast.DefType):
            assert ctype.wrapped
            return self.get_register_type(ctype.type)
        elif isinstance(ctype, cwast.TypeFun):
            return [self._code_reg_type]
        else:
            assert False, f"unknown type {ctype}"

    def get_size_and_alignment_and_set_offsets_for_rec_type(self, node: cwast.DefRec):
        size = 0
        alignment = 1
        for f in node.fields:
            if not isinstance(f, cwast.RecField):
                continue
            t = f.type.x_type
            size = align(size, t.x_alignment)
            f.x_offset = size
            size += t.x_size
            alignment = max(alignment, t.x_alignment)
        return size, alignment

    def finalize_rec_type(self, ctype: cwast.DefRec):
        ctype.x_size, ctype.x_alignment = self.get_size_and_alignment_and_set_offsets_for_rec_type(
            ctype)
        self._register_types[ctype] = self.get_register_type(ctype)

    def get_size_and_alignment(self, ctype):
        if isinstance(ctype, cwast.TypeBase):
            size = cwast.BASE_TYPE_KIND_TO_SIZE[ctype.base_type_kind]
            return size, size
        elif isinstance(ctype, cwast.TypePtr):
            size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
            return size, size
        elif isinstance(ctype, cwast.TypeSlice):
            size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
            return size * 2, size
        elif isinstance(ctype, cwast.TypeArray):
            alignment = ctype.type.x_alignment
            size = ctype.type.x_size
            # somtimes we need to round up. e.g. struct {int32, int8} needs 3 bytes padding
            size = align(size, alignment)
            len = ctype.size.x_value
            return len * size, alignment
        elif isinstance(ctype, cwast.TypeSum):
            return _get_size_and_offset_for_sum_type(
                ctype, cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind])
        elif isinstance(ctype, cwast.DefEnum):
            size = cwast.BASE_TYPE_KIND_TO_SIZE[ctype.base_type_kind]
            return size, size
        elif isinstance(ctype, cwast.TypeFun):
            size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
            return size, size
        elif isinstance(ctype, cwast.DefType):
            assert ctype.wrapped
            return self.get_size_and_alignment(ctype.type)
        else:
            # Note, DefRec is not handled here
            assert False, f"unknown type {ctype}"

    def _insert(self, name: str, node, finalize=True) -> CanonType:
        if name in self.corpus:
            return self.corpus[name]
        assert cwast.NF.TYPE_CORPUS in node.FLAGS, f"not a corpus node: {node}"
        self.corpus[name] = node
        self.topo_order.append(node)
        assert node not in self._canon_name
        assert STRINGIFIEDTYPE_RE.match(name), f"bad type name [{name}]"
        self._canon_name[node] = name
        if finalize:
            node.x_size, node.x_alignment = self.get_size_and_alignment(node)
            self._register_types[node] = self.get_register_type(node)
        return node

    def insert_base_type(self, kind: cwast.BASE_TYPE_KIND) -> CanonType:
        if kind == cwast.BASE_TYPE_KIND.UINT:
            kind = self.uint_kind
        elif kind == cwast.BASE_TYPE_KIND.SINT:
            kind = self.sint_kind
        name = kind.name.lower()
        return self._insert(name, cwast.TypeBase(kind))

    def insert_ptr_type(self, mut: bool, cstr: CanonType) -> CanonType:
        s = self.canon_name(cstr)
        if mut:
            name = f"ptr_mut<{s}>"
        else:
            name = f"ptr<{s}>"
        size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
        return self._insert(name, cwast.TypePtr(mut, cstr))

    def insert_slice_type(self, mut: bool, cstr: CanonType) -> CanonType:
        s = self.canon_name(cstr)
        if mut:
            name = f"slice_mut<{s}>"
        else:
            name = f"slice<{s}>"
        return self._insert(name, cwast.TypeSlice(mut, cstr))

    def insert_array_type(self, len: int, cstr: CanonType) -> CanonType:
        s = self.canon_name(cstr)
        name = f"array<{s},{len}>"
        dim = cwast.ValNum(str(len))
        dim.x_value = len
        return self._insert(name, cwast.TypeArray(dim, cstr))

    def lookup_rec_field(self, rec: cwast.DefRec, field_name) -> cwast.RecField:
        """Oddball since the node returned is NOT inside corpus

        See implementation of insert_rec_type
        """
        for x in rec.fields:
            if isinstance(x, cwast.RecField) and x.name == field_name:
                return x
        assert False

    def insert_rec_type(self, name: str, node: cwast.DefRec) -> CanonType:
        """Note: we re-use the original ast node"""
        name = f"rec<{name}>"
        return self._insert(name, node, finalize=False)

    def insert_enum_type(self, name: str, node: cwast.DefEnum) -> CanonType:
        """Note: we re-use the original ast node"""
        assert isinstance(node, cwast.DefEnum)
        name = f"enum<{name}>"
        return self._insert(name, node)

    def insert_sum_type(self, components: List[CanonType]) -> CanonType:
        assert len(components) > 1
        pieces = []
        for c in components:
            if isinstance(c, cwast.TypeSum):
                for cc in c.types:
                    pieces.append(cc)
            else:
                pieces.append(c)
        pp = sorted(self.canon_name(p) for p in pieces)
        name = f"sum<{','.join(pp)}>"
        node = cwast.TypeSum(pieces)
        return self._insert(name, node)

    def insert_fun_type(self, params: List[CanonType], result: CanonType) -> CanonType:
        x = [self.canon_name(p) for p in params]
        x.append(self.canon_name(result))
        name = f"fun<{','.join(x)}>"
        p = [cwast.FunParam("_", x) for x in params]
        return self._insert(name, cwast.TypeFun(p, result))

    def insert_wrapped_type(self, cstr: CanonType) -> CanonType:
        """Note: we re-use the original ast node"""
        uid = self.wrapped_curr
        self.wrapped_curr += 1
        name = f"wrapped<{uid},{self.canon_name(cstr)}>"
        assert name not in self.corpus
        return self._insert(name, cwast.DefType(False, True, "_", cstr))

    def insert_sum_complement(self, all: CanonType, part: CanonType) -> CanonType:
        assert isinstance(all, cwast.TypeSum)
        if isinstance(part, cwast.TypeSum):
            part_children = part.types
        else:
            part_children = [part]
        out = []
        for x in all.types:
            if x not in part_children:
                out.append(x)
        if len(out) == 1:
            return out[0]
        return self.insert_sum_type(out)

    def num_type(self, num: str, cstr: Optional[CanonType]) -> CanonType:
        for x in ("s8", "s16", "s32", "s64", "u8", "u16", "u32", "u64", "r32", "r64"):
            if num.endswith(x):
                return self.corpus[x]
        if num.endswith("sint"):
            return self.corpus[self.sint_kind.name.lower()]
        elif num.endswith("uint"):
            return self.corpus[self.uint_kind.name.lower()]
        elif cstr:
            return cstr
        else:
            return NO_TYPE
