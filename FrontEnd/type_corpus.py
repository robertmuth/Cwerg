"""All types have a canonical representation in the TypeCorpus"""
import logging
import re

from typing import List, Dict, Optional, Any

from FrontEnd import cwast


logger = logging.getLogger(__name__)


NO_TYPE = None
STRINGIFIEDTYPE_RE = re.compile(r"[a-zA-Z][_A-Za-z_0-9$,<>/]+")


def is_mutable_def(node):
    if isinstance(node, cwast.Id):
        s = node.x_symbol
        if isinstance(s, (cwast.DefVar, cwast.DefGlobal)):
            return s.mut
    return False


def align(x, a):
    return (x + a - 1) // a * a


def is_mutable(cstr:  cwast.CanonType, actual_is_lvalue=False) -> bool:
    if cstr.is_pointer() or cstr.is_slice():
        return cstr.is_mutable()
    elif cstr.is_array():
        return actual_is_lvalue
    else:
        assert False, f"unexpected node for mutable test: {cstr}"


def is_compatible(actual: cwast.CanonType, expected: cwast.CanonType,
                  actual_is_lvalue=False) -> bool:
    if actual == expected:
        return True

    if actual.is_slice() and expected.is_slice():
        if (actual.underlying_slice_type() == expected.underlying_slice_type() and
                actual.is_mutable() or not expected.is_mutable()):
            return True

    if actual.is_array() and expected.is_slice():
        # TODO: check "ref"
        return actual.underlying_array_type() == expected.underlying_slice_type() and (not expected.is_mutable() or actual_is_lvalue)

    if actual.is_pointer() and expected.is_pointer():
        # TODO: check "ref"
        return actual.underlying_pointer_type() == expected.underlying_pointer_type() and (not expected.is_mutable())

    if not expected.is_sum():
        return False

    expected_children = set([x.name for x in expected.sum_types()])
    if actual.is_sum():
        return set([x.name for x in actual.sum_types()]).issubset(expected_children)
    else:
        return actual.name in expected_children


def is_proper_lhs(node) -> bool:
    # TODO: this needs to be rethought and cleaned up
    # x =  (x must be mutable definition)
    # ^x = (x must have type mutable pointer)
    #
    if is_mutable_def(node):
        return True
    elif isinstance(node, cwast.ExprDeref):
        return node.expr.x_type.is_mutable()
        # isinstance(node, cwast.ExprDeref) and types.is_mutable_def(node.expr) or
    elif isinstance(node, cwast.ExprField):
        return is_proper_lhs(node.container)
    elif isinstance(node, cwast.ExprIndex):
        return is_proper_lhs(node.container) or is_mutable(node.container.x_type)
    else:
        return False


def is_mutable_container(node) -> bool:
    ct: cwast.CanonType = node.x_type
    if ct.is_slice():
        return ct.mut
    elif ct.is_array():
        return is_proper_lhs(node)
    else:
        assert False


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
    cwast.BASE_TYPE_KIND.TYPEID: ["U16"],
    #
    cwast.BASE_TYPE_KIND.VOID: [],
    cwast.BASE_TYPE_KIND.NORET: [],
}


def _get_size_and_offset_for_sum_type(tc: cwast.CanonType, ptr_size):
    assert tc.node is cwast.TypeSum
    num_void = 0
    num_pointer = 0
    num_other = 0
    max_size = 0
    max_alignment = 1
    for t in tc.sum_types():
        if t.is_wrapped():
            t = t.children[0]
        if t.is_void():
            num_void += 1
        elif t.is_pointer():
            num_pointer += 1
            max_size = max(max_size, ptr_size)
            max_alignment = max(max_alignment, ptr_size)
        else:
            num_other += 1
            max_size = max(max_size, t.size)
            max_alignment = max(max_alignment, t.alignment)
    if num_other == 0 and num_pointer == 1:
        # special hack for pointer + error-code
        return ptr_size, ptr_size
    max_alignment = max(max_alignment, 2)
    size = align(2, max_alignment)
    return size + max_size, max_alignment


TYPE_ID_REG_TYPE = "U16"


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

        for kind in cwast.BASE_TYPE_KIND:
            if kind.name in ("INVALID", "UINT", "SINT"):
                continue
            self.insert_base_type(kind)

    def convert_int(self, kind):
        if kind is cwast.BASE_TYPE_KIND.UINT:
            return self.uint_kind
        elif kind is cwast.BASE_TYPE_KIND.SINT:
            return self.sint_kind
        else:
            return kind

    def _get_register_type_for_sum_type(self, tc: cwast.CanonType):
        assert tc.node is cwast.TypeSum
        num_void = 0
        scalars: List[cwast.CanonType] = []
        largest_by_kind = {}
        largest = 0
        for t in tc.sum_types():
            if t.is_wrapped():
                t = t.children[0]
            if t.is_void():
                num_void += 1
                continue
            regs = t.register_types
            if regs is None or len(regs) > 1:
                return None
            scalars.append(t)
            k = regs[0][0]
            size = int(regs[0][1:])
            largest_by_kind[k] = max(largest_by_kind.get(k, 0), size)
            largest = max(largest, size)
        # special hack for pointer + error-code
        if len(scalars) == 1 and scalars[0].is_pointer():
            return scalars[0].register_types

        k = next(iter(largest_by_kind)) if len(largest_by_kind) == 1 else "U"
        return [f"U{largest}", TYPE_ID_REG_TYPE]

    def get_register_type(self, tc: cwast.CanonType) -> Optional[List[str]]:
        """As long as a type can fit into no more than two regs it will have
        register representation which is also how it will be past in function calls.
        """
        if tc.node is cwast.TypeBase:
            return _BASE_TYPE_MAP.get(tc.base_type_kind)
        elif tc.node is cwast.TypePtr:
            return [self._addr_reg_type]
        elif tc.node is cwast.TypeSlice:
            return [self._addr_reg_type] + _BASE_TYPE_MAP[self.uint_kind]
        elif tc.node is cwast.DefRec:
            fields = [f for f in tc.ast_node.fields]
            if len(fields) == 1:
                return self.get_register_type(fields[0].type.x_type)
            elif len(fields) == 2:
                a = self.get_register_type(fields[0].type.x_type)
                b = self.get_register_type(fields[1].type.x_type)
                if a is not None and b is not None and len(a) + len(b) <= 2:
                    return a + b
            else:
                return None
        elif tc.node is cwast.TypeArray:
            return None
        elif tc.node is cwast.DefEnum:
            return _BASE_TYPE_MAP[tc.base_type_kind]
        elif tc.node is cwast.TypeSum:
            return self._get_register_type_for_sum_type(tc)
        elif tc.node is cwast.DefType:
            return self.get_register_type(tc.children[0])
        elif tc.node is cwast.TypeFun:
            return [self._code_reg_type]
        else:
            assert False, f"unknown type {tc.name}"

    def _get_size_and_alignment_and_set_offsets_for_rec_type(self, tc: cwast.CanonType):
        size = 0
        alignment = 1
        assert isinstance(tc.ast_node, cwast.DefRec)
        def_rec: cwast.DefRec = tc.ast_node
        for rf in def_rec.fields:
            assert isinstance(rf, cwast.RecField)
            field_ct: cwast.CanonType = rf.type.x_type
            size = align(size, field_ct.alignment)
            rf.x_offset = size
            size += field_ct.size
            alignment = max(alignment, field_ct.alignment)
        return size, alignment

    def finalize_rec_type(self, tc: cwast.CanonType):
        tc.size, tc.alignment = self._get_size_and_alignment_and_set_offsets_for_rec_type(
            tc)
        tc.register_types = self.get_register_type(tc)

    def get_size_and_alignment(self, tc: cwast.CanonType):
        if tc.node is cwast.TypeBase:
            size = cwast.BASE_TYPE_KIND_TO_SIZE[tc.base_type_kind]
            return size, size
        elif tc.node is cwast.TypePtr:
            size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
            return size, size
        elif tc.node is cwast.TypeSlice:
            size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
            return size * 2, size
        elif tc.node is cwast.TypeArray:
            alignment = tc.children[0].alignment
            size = tc.children[0].size
            # somtimes we need to round up. e.g. struct {int32, int8} needs 3 bytes padding
            size = align(size, alignment)
            return size * tc.dim, alignment
        elif tc.node is cwast.TypeSum:
            return _get_size_and_offset_for_sum_type(
                tc, cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind])
        elif tc.node is cwast.DefEnum:
            size = cwast.BASE_TYPE_KIND_TO_SIZE[tc.base_type_kind]
            return size, size
        elif tc.node is cwast.TypeFun:
            size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
            return size, size
        elif tc.node is cwast.DefType:
            return self.get_size_and_alignment(tc.children[0])
        else:
            # Note, DefRec is not handled here
            assert False, f"unknown type {tc}"

    def _insert(self, ct: cwast.CanonType, finalize=True) -> cwast.CanonType:
        if ct.name in self.corpus:
            return self.corpus[ct.name]
        self.corpus[ct.name] = ct
        self.topo_order.append(ct)
        assert STRINGIFIEDTYPE_RE.fullmatch(
            ct.name), f"bad type name [{ct.name}]"
        if finalize:
            ct.size, ct.alignment = self.get_size_and_alignment(ct)
            ct.register_types = self.get_register_type(ct)
        return ct

    def insert_base_type(self, kind: cwast.BASE_TYPE_KIND) -> cwast.CanonType:
        kind = self.convert_int(kind)
        return self._insert(cwast.CanonType(cwast.TypeBase, kind.name.lower(), base_type_kind=kind))

    def insert_ptr_type(self, mut: bool, ct: cwast.CanonType) -> cwast.CanonType:
        if mut:
            name = f"ptr_mut<{ct.name}>"
        else:
            name = f"ptr<{ct.name}>"
        return self._insert(cwast.CanonType(cwast.TypePtr, name, mut=mut, children=[ct]))

    def insert_slice_type(self, mut: bool, ct: cwast.CanonType) -> cwast.CanonType:
        if mut:
            name = f"slice_mut<{ct.name}>"
        else:
            name = f"slice<{ct.name}>"
        return self._insert(cwast.CanonType(cwast.TypeSlice, name, mut=mut, children=[ct]))

    def insert_array_type(self, dim: int, ct: cwast.CanonType) -> cwast.CanonType:
        name = f"array<{ct.name},{dim}>"
        return self._insert(cwast.CanonType(cwast.TypeArray, name, dim=dim, children=[ct]))

    def lookup_rec_field(self, tc: cwast.CanonType, field_name) -> cwast.RecField:
        """Oddball since the node returned is NOT inside corpus

        See implementation of insert_rec_type
        """
        assert tc.node is cwast.DefRec
        assert isinstance(tc.ast_node, cwast.DefRec)
        for x in tc.ast_node.fields:
            if isinstance(x, cwast.RecField) and x.name == field_name:
                return x
        return None

    def insert_rec_type(self, name: str, ast_node: cwast.DefRec) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        assert isinstance(ast_node, cwast.DefRec)
        name = f"rec<{name}>"
        return self._insert(cwast.CanonType(cwast.DefRec, name, ast_node=ast_node), finalize=False)

    def insert_enum_type(self, name: str, ast_node: cwast.DefEnum) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        assert isinstance(ast_node, cwast.DefEnum)
        name = f"enum<{name}>"
        return self._insert(cwast.CanonType(cwast.DefEnum, name,
                                            base_type_kind=ast_node.base_type_kind, ast_node=ast_node))

    def insert_sum_type(self, components: List[cwast.CanonType]) -> cwast.CanonType:
        assert len(components) > 1
        pieces = []
        for c in components:
            if c.node is cwast.TypeSum:
                for cc in c.children:
                    pieces.append(cc)
            else:
                pieces.append(c)
        pp = sorted(p.name for p in pieces)
        name = f"sum<{','.join(pp)}>"
        return self._insert(cwast.CanonType(cwast.TypeSum, name, children=pieces))

    def insert_fun_type(self, params: List[cwast.CanonType],
                        result: cwast.CanonType) -> cwast.CanonType:
        x = [p.name for p in params]
        x.append(result.name)
        name = f"fun<{','.join(x)}>"
        return self._insert(cwast.CanonType(cwast.TypeFun, name, children=params + [result]))

    def insert_wrapped_type(self, tc: cwast.CanonType) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        uid = self.wrapped_curr
        self.wrapped_curr += 1
        name = f"wrapped<{uid},{tc.name}>"
        assert name not in self.corpus
        return self._insert(cwast.CanonType(cwast.DefType, name, children=[tc]))

    def insert_sum_complement(self, all: cwast.CanonType, part: cwast.CanonType) -> cwast.CanonType:
        assert all.node is cwast.TypeSum, f"expect sum type: {all.name}"
        if part.node is cwast.TypeSum:
            part_children = part.children
        else:
            part_children = [part]
        out = []
        for x in all.children:
            if x not in part_children:
                out.append(x)
        if len(out) == 1:
            return out[0]
        return self.insert_sum_type(out)
