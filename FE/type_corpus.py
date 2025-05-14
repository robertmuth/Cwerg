"""All types have a canonical representation in the TypeCorpus"""
import logging
import re
import dataclasses

from typing import Optional

from FE import cwast


logger = logging.getLogger(__name__)


STRINGIFIEDTYPE_RE = re.compile(r"[a-zA-Z][_A-Za-z_0-9$,<>/]+")


ENABLE_UNION_OPTIMIZATIONS = False


def align(x, a):
    return (x + a - 1) // a * a


def is_compatible(actual: cwast.CanonType, expected: cwast.CanonType,
                  actual_is_lvalue=False) -> bool:
    if actual == expected:
        return True

    if actual.is_span() and expected.is_span():
        if (actual.underlying_span_type() == expected.underlying_span_type() and
                actual.is_mutable() or not expected.is_mutable()):
            return True

    if actual.is_vec() and expected.is_span():
        # TODO: check "ref"
        return actual.underlying_array_type() == expected.underlying_span_type() and (not expected.is_mutable() or actual_is_lvalue)

    if actual.is_pointer() and expected.is_pointer():
        # TODO: check "ref"
        return actual.underlying_pointer_type() == expected.underlying_pointer_type() and (not expected.is_mutable())

    if not expected.is_union():
        return False

    expected_children = set([x.name for x in expected.union_member_types()])
    if actual.is_union():
        if actual.untagged != expected.untagged:
            return False
        return set([x.name for x in actual.union_member_types()]).issubset(expected_children)
    else:
        return actual.name in expected_children


# maybe add records if all their fields are comparable?
def is_comparable(ct: cwast.CanonType) -> bool:
    return (ct.is_base_or_enum_type() or ct.is_pointer() or
            ct.is_wrapped() and is_comparable(ct.underlying_wrapped_type()))


def is_compatible_for_eq(actual: cwast.CanonType, expected: cwast.CanonType) -> bool:
    if is_comparable(actual):
        if actual == expected:
            return True

        if expected.is_tagged_union():
            return actual in expected.union_member_types()

    if actual.is_tagged_union():
        return is_comparable(expected) and expected in actual.union_member_types()

    return False


def is_compatible_for_as(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:

    if not ct_src.is_int() and not ct_src.is_real() and not ct_src.is_bool():
        return False

    if not ct_dst.is_int() and not ct_dst.is_real() and not ct_dst.is_bool():
        return False

    return True


def is_compatible_for_bitcast(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    if not ct_src.is_base_or_enum_type() and not ct_src.is_pointer():
        return False
    if not ct_dst.is_base_or_enum_type() and not ct_dst.is_pointer():
        return False
    return ct_src.aligned_size() == ct_dst.aligned_size()


def is_compatible_for_widen(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    if ct_dst.is_union():
        dst_children = set([x.name for x in ct_dst.union_member_types()])
        if ct_src.is_union():
            if ct_dst.untagged != ct_src.untagged:
                return False
            src_children = set([x.name for x in ct_src.union_member_types()])
        else:
            src_children = set(
                [ct_src.original_type.name if ct_src.original_type else ct_src.name])
        return src_children.issubset(dst_children)
    return False


def is_compatible_for_narrow(ct_src: cwast.CanonType, ct_dst: cwast.CanonType, sl: cwast.SrcLoc) -> bool:

    if ct_src.original_type is not None:
        ct_src = ct_src.original_type
    if ct_dst.original_type is not None:
        ct_dst = ct_dst.original_type
    assert ct_src.is_union(), F"{ct_src} VS {ct_dst} {sl}"
    src_children = set([x.name for x in ct_src.union_member_types()])
    if ct_dst.is_union():
        if ct_dst.untagged != ct_src.untagged:
            return False
        dst_children = set([x.name for x in ct_dst.union_member_types()])
    else:
        dst_children = set([ct_dst.name])
    return dst_children.issubset(src_children)


def is_compatible_for_wrap(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    if ct_dst.is_enum():
        return ct_src.is_base_type() and ct_dst.base_type_kind == ct_src.base_type_kind
    elif ct_dst.is_wrapped():
        wrapped_type = ct_dst.underlying_wrapped_type()
        if wrapped_type in (ct_src, ct_src.original_type):
            return True
        if ct_src.is_vec() and wrapped_type.is_span():
            return ct_src.underlying_array_type() == wrapped_type.underlying_span_type() and not ct_dst.is_mutable()

    return False


def is_proper_lhs(node) -> bool:
    if isinstance(node, cwast.Id):
        s = node.x_symbol
        if isinstance(s, (cwast.DefVar, cwast.DefGlobal)):
            return s.mut
        return False
    elif isinstance(node, cwast.ExprDeref):
        # this assert is necessary to satisfy the mypy type checker
        assert not isinstance(
            node.expr, (cwast.MacroInvoke, cwast.ExprStringify))
        return node.expr.x_type.is_mutable()
        # isinstance(node, cwast.ExprDeref) and types.is_mutable_def(node.expr) or
    elif isinstance(node, cwast.ExprField):
        return is_proper_lhs(node.container)
    elif isinstance(node, cwast.ExprIndex):
        # this assert is necessary to satisfy the mypy type checker
        assert not isinstance(
            node.container,  (cwast.MacroInvoke, cwast.ExprStringify))
        container_ct: cwast.CanonType = node.container.x_type
        if container_ct.is_span():
            return container_ct.mut
        else:
            assert container_ct.is_vec()
            return is_proper_lhs(node.container)
    elif isinstance(node, (cwast.ExprAs, cwast.ExprNarrow)):
        # this assert is necessary to satisfy the mypy type checker
        assert not isinstance(
            node.expr,  (cwast.MacroInvoke, cwast.ExprStringify))
        if node.expr.x_type.is_untagged_union():
            return is_proper_lhs(node.expr)
        else:
            return False
    else:
        return False


def is_mutable_array(node) -> bool:
    """"""
    if not node.x_type.is_vec():
        return False

    return is_proper_lhs(node)


def is_mutable_array_or_span(node) -> bool:
    """Mutable refers to the elements of the array/span"""
    ct: cwast.CanonType = node.x_type
    if ct.is_span():
        return ct.mut
    elif ct.is_vec():
        return is_proper_lhs(node)
    else:
        assert False


# maps FE types to BE names.
# Note: it would be cleaner to use the BE enum
_BASE_TYPE_MAP: dict[cwast.BASE_TYPE_KIND, list[str]] = {
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
    cwast.BASE_TYPE_KIND.R32: ["R32"],
    cwast.BASE_TYPE_KIND.R64: ["R64"],
    #
    cwast.BASE_TYPE_KIND.BOOL: ["U8"],
    cwast.BASE_TYPE_KIND.TYPEID: ["U16"],
    #
    cwast.BASE_TYPE_KIND.VOID: [],
    cwast.BASE_TYPE_KIND.NORET: [],
}


def _get_size_and_offset_for_union_type(ct: cwast.CanonType, tag_size, ptr_size):
    assert ct.node is cwast.TypeUnion
    num_void = 0
    num_pointer = 0
    num_other = 0
    max_size = 0
    max_alignment = 1
    for t in ct.union_member_types():
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
            assert t.size >= 0, f"{ct} size is not yet known"
            max_size = max(max_size, t.size)
            max_alignment = max(max_alignment, t.alignment)
    if ct.untagged:
        return max_size, max_alignment
    if ENABLE_UNION_OPTIMIZATIONS and num_other == 0 and num_pointer == 1:
        # special hack for pointer + error-code
        return ptr_size, ptr_size
    # the tag is the first component of the tagged union in memory
    max_alignment = max(max_alignment, tag_size)
    size = align(tag_size, max_alignment)
    return size + max_size, max_alignment


def _get_size_and_alignment_and_set_offsets_for_rec_type(ct: cwast.CanonType):
    size = 0
    alignment = 1
    assert isinstance(ct.ast_node, cwast.DefRec)
    def_rec: cwast.DefRec = ct.ast_node
    for rf in def_rec.fields:
        assert isinstance(rf, cwast.RecField)
        field_ct: cwast.CanonType = rf.type.x_type
        assert field_ct.alignment >= 0
        size = align(size, field_ct.alignment)
        rf.x_offset = size
        size += field_ct.size
        alignment = max(alignment, field_ct.alignment)
    return size, alignment


@dataclasses.dataclass()
class TargetArchConfig:
    """target system config"""
    uint_bitwidth: int    # also used for ptr cast to ints
    sint_bitwidth: int
    typeid_bitwidth: int
    data_addr_bitwidth: int  # it is hard to imagine: data_addr_bitwidth != uint_bitwidth
    code_addr_bitwidth: int


STD_TARGET_X64 = TargetArchConfig(64, 64, 16, 64, 64)
STD_TARGET_A64 = TargetArchConfig(64, 64, 16, 64, 64)
STD_TARGET_A32 = TargetArchConfig(32, 32, 16, 32, 32)


class TypeCorpus:
    """The type corpus uniquifies types

    It does so by representing each type with a string (basically a serialized
    version of type like "array<ptr<u32>,128>").
    That serialized version is mapped back to a structural version expressed
    using AST nodes.
    """

    def __init__(self, target_arch_config: TargetArchConfig):
        self._target_arch_config: TargetArchConfig = target_arch_config
        self._wrapped_curr = 1
        self._base_type_map: dict[cwast.BASE_TYPE_KIND, cwast.CanonType] = {}
        self._typeid_curr = 0
        # maps to ast
        self.topo_order: list[cwast.CanonType] = []
        self.corpus: dict[str, cwast.CanonType] = {}  # name to canonical type

        # VOID should get typeid zero
        ct = self._insert_base_type(cwast.BASE_TYPE_KIND.VOID)
        self._base_type_map[cwast.BASE_TYPE_KIND.VOID] = ct

        for kind in cwast.BASE_TYPE_KIND:
            if kind.name in ("INVALID", "UINT", "SINT", "TYPEID", "VOID"):
                continue
            ct = self._insert_base_type(kind)
            self._base_type_map[kind] = ct

            bitwidth = cwast.BASE_TYPE_KIND_TO_SIZE[kind] * 8
            if kind in cwast.BASE_TYPE_KIND_SINT:
                if bitwidth == target_arch_config.sint_bitwidth:
                    self._base_type_map[cwast.BASE_TYPE_KIND.SINT] = ct
            if kind in cwast.BASE_TYPE_KIND_UINT:
                if bitwidth == target_arch_config.uint_bitwidth:
                    self._base_type_map[cwast.BASE_TYPE_KIND.UINT] = ct
                if bitwidth == target_arch_config.typeid_bitwidth:
                    self._base_type_map[cwast.BASE_TYPE_KIND.TYPEID] = ct

    def get_base_canon_type(self, kind: cwast.BASE_TYPE_KIND):
        return self._base_type_map[kind]

    def get_uint_canon_type(self):
        return self._base_type_map[cwast.BASE_TYPE_KIND.UINT]

    def get_sint_canon_type(self):
        return self._base_type_map[cwast.BASE_TYPE_KIND.SINT]

    def get_typeid_canon_type(self):
        return self._base_type_map[cwast.BASE_TYPE_KIND.TYPEID]

    def get_bool_canon_type(self):
        return self._base_type_map[cwast.BASE_TYPE_KIND.BOOL]

    def get_void_canon_type(self):
        return self._base_type_map[cwast.BASE_TYPE_KIND.VOID]

    def get_data_address_reg_type(self):
        return f"A{self._target_arch_config.data_addr_bitwidth}"

    def get_uint_reg_type(self):
        return f"U{self._target_arch_config.uint_bitwidth}"

    def get_address_size(self):
        return self._target_arch_config.data_addr_bitwidth // 8

    def _get_register_type_for_union_type(self, ct: cwast.CanonType) -> Optional[list[str]]:
        assert ct.node is cwast.TypeUnion
        num_void = 0
        scalars: list[cwast.CanonType] = []
        largest_by_kind: dict[str, int] = {}
        largest = 0
        for t in ct.union_member_types():
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
        if ENABLE_UNION_OPTIMIZATIONS and len(scalars) == 1 and scalars[0].is_pointer():
            return scalars[0].register_types

        if largest == 0:
            return [f"U{self._target_arch_config.typeid_bitwidth}"]
        return [f"U{largest}", f"U{self._target_arch_config.typeid_bitwidth}"]

    def _get_register_type(self, ct: cwast.CanonType) -> Optional[list[str]]:
        """As long as a type can fit into no more than two regs it will have
        register representation which is also how it will be past in function calls.
        """
        if ct.node is cwast.TypeBase:
            return _BASE_TYPE_MAP.get(ct.base_type_kind)
        elif ct.node is cwast.TypePtr:
            return [self.get_data_address_reg_type()]
        elif ct.node is cwast.TypeSpan:
            return [self.get_data_address_reg_type(), self.get_uint_reg_type()]
        elif ct.node is cwast.DefRec:
            assert isinstance(ct.ast_node, cwast.DefRec)
            fields = ct.ast_node.fields
            if len(fields) == 1:
                return self._get_register_type(fields[0].type.x_type)
            elif len(fields) == 2:
                a = self._get_register_type(fields[0].type.x_type)
                b = self._get_register_type(fields[1].type.x_type)
                if a is not None and b is not None and len(a) + len(b) <= 2:
                    return a + b
            return None
        elif ct.node is cwast.TypeVec:
            return None
        elif ct.node is cwast.DefEnum:
            return _BASE_TYPE_MAP[ct.base_type_kind]
        elif ct.node is cwast.TypeUnion:
            return self._get_register_type_for_union_type(ct)
        elif ct.node is cwast.DefType:
            return self._get_register_type(ct.children[0])
        elif ct.node is cwast.TypeFun:
            return [f"C{self._target_arch_config.data_addr_bitwidth}"]
        else:
            assert False, f"unknown type {ct.name}"
            return None

    def _get_size_and_alignment(self, ct: cwast.CanonType):
        if ct.node is cwast.TypeBase:
            size = cwast.BASE_TYPE_KIND_TO_SIZE[ct.base_type_kind]
            return size, size
        elif ct.node is cwast.TypePtr:
            size = self._target_arch_config.code_addr_bitwidth // 8
            return size, size
        elif ct.node is cwast.TypeSpan:
            # span is converted to (pointer, length) tuple
            ptr_field_size = self._target_arch_config.data_addr_bitwidth // 8
            len_field_size = self._target_arch_config.uint_bitwidth // 8
            return ptr_field_size + len_field_size, ptr_field_size
        elif ct.node is cwast.TypeVec:
            return ct.children[0].aligned_size() * ct.dim, ct.children[0].alignment
        elif ct.node is cwast.TypeUnion:
            return _get_size_and_offset_for_union_type(
                ct, self._target_arch_config.typeid_bitwidth // 8,
                self._target_arch_config.data_addr_bitwidth // 8)
        elif ct.node is cwast.DefEnum:
            size = cwast.BASE_TYPE_KIND_TO_SIZE[ct.base_type_kind]
            return size, size
        elif ct.node is cwast.TypeFun:
            size = self._target_arch_config.code_addr_bitwidth // 8
            return size, size
        elif ct.node is cwast.DefType:
            return self._get_size_and_alignment(ct.children[0])
        else:
            # Note, DefRec is not handled here
            assert False, f"unknown type {ct}"

    def _finalize(self, ct: cwast.CanonType, size, alignment):
        if not ct.original_type:
            ct.typeid = self._typeid_curr
            self._typeid_curr += 1
        ct.finalize(size, alignment, self._get_register_type(ct))

    def _insert(self, ct: cwast.CanonType, finalize=True) -> cwast.CanonType:
        """The only type not finalized here are Recs"""
        assert ct.name not in self.corpus, f"duplicate insertion of type: {ct.name}"

        # print(f">>>>>>>> ",  ct.name,  ct.typeid, ct.original_type)
        self.corpus[ct.name] = ct
        self.topo_order.append(ct)
        assert STRINGIFIEDTYPE_RE.fullmatch(
            ct.name), f"bad type name [{ct.name}]"
        if finalize:
            size, alignment = self._get_size_and_alignment(ct)
            self._finalize(ct, size, alignment)
        return ct

    def _insert_base_type(self, kind: cwast.BASE_TYPE_KIND) -> cwast.CanonType:
        return self._insert(cwast.CanonType(
            cwast.TypeBase, cwast.BaseTypeKindToKeyword(kind), base_type_kind=kind))

    def InsertPtrType(self, mut: bool, ct: cwast.CanonType) -> cwast.CanonType:
        name = f"ptr_mut<{ct.name}>" if mut else f"ptr<{ct.name}>"
        if name in self.corpus:
            return self.corpus[name]
        return self._insert(cwast.CanonType(cwast.TypePtr, name, mut=mut, children=[ct],
                                            ))

    def InsertSpanType(self, mut: bool, ct: cwast.CanonType) -> cwast.CanonType:
        name = f"span_mut<{ct.name}>" if mut else f"span<{ct.name}>"
        if name in self.corpus:
            return self.corpus[name]
        return self._insert(cwast.CanonType(cwast.TypeSpan, name, mut=mut, children=[ct],
                                            ))

    def InsertVecType(self, dim: int, ct: cwast.CanonType) -> cwast.CanonType:
        name = f"vec<{dim},{ct.name}>"
        if name in self.corpus:
            return self.corpus[name]
        return self._insert(cwast.CanonType(cwast.TypeVec, name, dim=dim,
                                            children=[ct]))

    def lookup_rec_field(self, ct: cwast.CanonType, field_name) -> Optional[cwast.RecField]:
        """Oddball since the node returned is NOT inside corpus

        See implementation of insert_rec_type
        """
        assert ct.node is cwast.DefRec
        assert isinstance(ct.ast_node, cwast.DefRec)
        for x in ct.ast_node.fields:
            if isinstance(x, cwast.RecField) and x.name == field_name:
                return x
        return None

    def InsertRecType(self, name: str, ast_node: cwast.DefRec) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        assert isinstance(ast_node, cwast.DefRec)
        name = f"rec<{name}>"
        return self._insert(cwast.CanonType(cwast.DefRec, name, ast_node=ast_node), finalize=False)

    def FinalizeRecType(self, ct: cwast.CanonType):
        size, alignment = _get_size_and_alignment_and_set_offsets_for_rec_type(
            ct)
        self._finalize(ct, size, alignment)

    def InsertEnumType(self, name: str, ast_node: cwast.DefEnum) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        assert isinstance(ast_node, cwast.DefEnum)
        name = f"enum<{name}>"
        return self._insert(cwast.CanonType(cwast.DefEnum, name,
                                            base_type_kind=ast_node.base_type_kind, ast_node=ast_node))

    def InsertUnionType(self, untagged: bool, components: list[cwast.CanonType]) -> cwast.CanonType:
        assert len(components) > 1
        pp = set()
        for c in components:
            if c.node is cwast.TypeUnion and c.untagged == untagged:
                for cc in c.children:
                    pp.add(cc)
            else:
                pp.add(c)
        sorted_children = sorted(pp, key=lambda x: x.name)
        sorted_names = [x.name for x in sorted_children]
        extra = "_untagged" if untagged else ""
        name = f"sum{extra}<{','.join(sorted_names)}>"
        if name in self.corpus:
            return self.corpus[name]
        ct = cwast.CanonType(cwast.TypeUnion, name,
                             children=sorted_children, untagged=untagged)
        if not untagged:
            ct.set_union_kind()
        return self._insert(ct)

    def InsertFunType(self, params: list[cwast.CanonType],
                      result: cwast.CanonType) -> cwast.CanonType:
        x = [p.name for p in params]
        x.append(result.name)
        name = f"fun<{','.join(x)}>"
        if name in self.corpus:
            return self.corpus[name]
        return self._insert(cwast.CanonType(cwast.TypeFun, name, children=params + [result]))

    def InsertWrappedType(self, ct: cwast.CanonType) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        assert not ct.is_wrapped()
        uid = self._wrapped_curr
        self._wrapped_curr += 1
        name = f"wrapped<{uid},{ct.name}>"
        assert name not in self.corpus
        return self._insert(cwast.CanonType(cwast.DefType, name, children=[ct]))

    def insert_union_complement(self, all: cwast.CanonType, part: cwast.CanonType) -> cwast.CanonType:
        assert all.node is cwast.TypeUnion, f"expect sum type: {all.name}"
        if part.node is cwast.TypeUnion:
            part_children = part.children
        else:
            part_children = [part]
        out = []
        for x in all.children:
            if x not in part_children:
                out.append(x)
        if len(out) == 1:
            return out[0]
        return self.InsertUnionType(all.untagged, out)
