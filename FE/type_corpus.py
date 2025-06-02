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


def IsSameTypeExceptMut(actual: cwast.CanonType, expected: cwast.CanonType) -> bool:
    if actual == expected:
        return True
    if (actual.is_pointer() and expected.is_pointer() or
            actual.is_span() and expected.is_span()):
        return actual.underlying_type() == expected.underlying_type() and (not expected.is_mutable())
    return False


def IsCompatibleType(actual: cwast.CanonType, expected: cwast.CanonType,
                     actual_is_lvalue=False) -> bool:
    if actual == expected:
        return True

    if actual.is_span() and expected.is_span():
        if (actual.underlying_type() == expected.underlying_type() and
                actual.is_mutable() or not expected.is_mutable()):
            return True

    if actual.is_vec() and expected.is_span():
        # TODO: check "ref"
        return actual.underlying_type() == expected.underlying_type() and (not expected.is_mutable() or actual_is_lvalue)

    if actual.is_pointer() and expected.is_pointer():
        # TODO: check "ref"
        return actual.underlying_type() == expected.underlying_type() and (not expected.is_mutable())

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
def IsComparableType(ct: cwast.CanonType) -> bool:
    return (ct.is_base_or_enum_type() or ct.is_pointer() or
            ct.is_wrapped() and IsComparableType(ct.underlying_type()))


def IsCompatibleTypeForEq(actual: cwast.CanonType, expected: cwast.CanonType) -> bool:
    if IsComparableType(actual) or actual.is_fun():
        if actual == expected:
            return True

        if expected.is_tagged_union():
            return actual in expected.union_member_types()

    if actual.is_tagged_union():
        return IsComparableType(expected) and expected in actual.union_member_types()

    return False


def IsCompatibleTypeForAs(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    return (ct_src.is_base_type() and ct_dst.is_base_type() and
            ct_src.base_type_kind.IsNumber() and
            ct_dst.base_type_kind.IsNumber())


def IsCompatibleTypeForBitcast(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    if not ct_src.is_base_or_enum_type() and not ct_src.is_pointer():
        return False
    if not ct_dst.is_base_or_enum_type() and not ct_dst.is_pointer():
        return False
    return ct_src.aligned_size() == ct_dst.aligned_size()


def IsCompatibleTypeForWiden(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
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


def IsCompatibleTypeForNarrow(ct_src: cwast.CanonType, ct_dst: cwast.CanonType, sl: cwast.SrcLoc) -> bool:

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


def IsCompatibleTypeForWrap(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    if ct_dst.is_enum():
        return ct_src.is_base_type() and ct_dst.base_type_kind == ct_src.base_type_kind
    elif ct_dst.is_wrapped():
        wrapped_type = ct_dst.underlying_type()
        if wrapped_type in (ct_src, ct_src.original_type):
            return True
        if ct_src.is_vec() and wrapped_type.is_span():
            return ct_src.underlying_type() == wrapped_type.underlying_type() and not ct_dst.is_mutable()

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


@dataclasses.dataclass()
class TargetArchConfig:
    """target system config"""
    uint_bitwidth: int    # also used for ptr cast to ints
    sint_bitwidth: int
    typeid_bitwidth: int
    data_addr_bitwidth: int  # it is hard to imagine: data_addr_bitwidth != uint_bitwidth
    code_addr_bitwidth: int

    def get_data_address_reg_type(self):
        return f"A{self.data_addr_bitwidth}"

    def get_uint_reg_type(self):
        return f"U{self.uint_bitwidth}"

    def get_sint_reg_type(self):
        return f"S{self.sint_bitwidth}"

    def get_address_size(self):
        return self.data_addr_bitwidth // 8


STD_TARGET_X64 = TargetArchConfig(64, 64, 16, 64, 64)
STD_TARGET_A64 = TargetArchConfig(64, 64, 16, 64, 64)
STD_TARGET_A32 = TargetArchConfig(32, 32, 16, 32, 32)


def _get_register_type_for_union_type(ct: cwast.CanonType, ta: TargetArchConfig) -> Optional[list[str]]:
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
        return [f"U{ta.typeid_bitwidth}"]
    return [f"U{largest}", f"U{ta.typeid_bitwidth}"]


def _get_register_type(ct: cwast.CanonType, ta: TargetArchConfig) -> Optional[list[str]]:
    """As long as a type can fit into no more than two regs it will have
    register representation which is also how it will be past in function calls.
    """
    if ct.node is cwast.TypeBase:
        return _BASE_TYPE_MAP.get(ct.base_type_kind)
    elif ct.node is cwast.TypePtr:
        return [ta.get_data_address_reg_type()]
    elif ct.node is cwast.TypeSpan:
        return [ta.get_data_address_reg_type(),
                ta.get_uint_reg_type()]
    elif ct.node is cwast.DefRec:
        assert isinstance(ct.ast_node, cwast.DefRec)
        fields = ct.ast_node.fields
        if len(fields) == 1:
            return _get_register_type(fields[0].type.x_type, ta)
        elif len(fields) == 2:
            a = _get_register_type(fields[0].type.x_type, ta)
            b = _get_register_type(fields[1].type.x_type, ta)
            if a is not None and b is not None and len(a) + len(b) <= 2:
                return a + b
        return None
    elif ct.node is cwast.TypeVec:
        return None
    elif ct.node is cwast.DefEnum:
        return _BASE_TYPE_MAP[ct.base_type_kind]
    elif ct.node is cwast.TypeUnion:
        return _get_register_type_for_union_type(ct, ta)
    elif ct.node is cwast.DefType:
        return _get_register_type(ct.children[0], ta)
    elif ct.node is cwast.TypeFun:
        return [f"C{ta.data_addr_bitwidth}"]
    else:
        assert False, f"unknown type {ct.name}"
        return None


def _SetAbiInfoRecursivelyForSum(ct: cwast.CanonType, ta: TargetArchConfig):
    tag_size = ta.typeid_bitwidth // 8
    ptr_size = ta.data_addr_bitwidth // 8
    assert ct.node is cwast.TypeUnion
    num_void = 0
    num_pointer = 0
    num_other = 0
    max_size = 0
    max_alignment = 1
    for t in ct.union_member_types():
        if t.is_wrapped():
            t = t.children[0]
        SetAbiInfoRecursively(t, ta)
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


def _SetAbiInfoRecursivelyForRec(ct: cwast.CanonType, ta: TargetArchConfig):
    size = 0
    alignment = 1
    assert isinstance(ct.ast_node, cwast.DefRec)
    def_rec: cwast.DefRec = ct.ast_node
    for rf in def_rec.fields:
        assert isinstance(rf, cwast.RecField)
        field_ct: cwast.CanonType = rf.type.x_type
        SetAbiInfoRecursively(field_ct, ta)
        size = align(size, field_ct.alignment)
        # only place where x_offset is set
        rf.x_offset = size
        size += field_ct.size
        alignment = max(alignment, field_ct.alignment)
    return size, alignment


def SetAbiInfoRecursively(ct: cwast.CanonType, ta: TargetArchConfig):
    if ct.alignment >= 0:
        return
    if ct.node is cwast.TypeBase:
        size = cwast.BASE_TYPE_KIND_TO_SIZE[ct.base_type_kind]
        ct.finalize(size, size, _get_register_type(ct, ta))
    elif ct.node is cwast.TypePtr:
        size = ta.code_addr_bitwidth // 8
        ct.finalize(size, size, _get_register_type(ct, ta))
    elif ct.node is cwast.TypeSpan:
        # span is converted to (pointer, length) tuple
        ptr_field_size = ta.data_addr_bitwidth // 8
        len_field_size = ta.uint_bitwidth // 8
        ct.finalize(ptr_field_size + len_field_size,
                    ptr_field_size, _get_register_type(ct, ta))

    elif ct.node is cwast.TypeVec:
        ct_dep = ct.children[0]
        SetAbiInfoRecursively(ct_dep, ta)
        ct.finalize(ct_dep.aligned_size() * ct.dim,
                    ct_dep.alignment,  _get_register_type(ct, ta))
    elif ct.node is cwast.TypeUnion:
        size, alignment = _SetAbiInfoRecursivelyForSum(ct, ta)
        ct.finalize(size, alignment, _get_register_type(ct, ta))
    elif ct.node is cwast.DefEnum:
        size = cwast.BASE_TYPE_KIND_TO_SIZE[ct.base_type_kind]
        ct.finalize(size, size, _get_register_type(ct, ta))
    elif ct.node is cwast.TypeFun:
        size = ta.code_addr_bitwidth // 8
        ct.finalize(size, size, _get_register_type(ct, ta))
    elif ct.node is cwast.DefType:
        ct_dep = ct.children[0]
        SetAbiInfoRecursively(ct_dep, ta)
        ct.finalize(ct_dep.size, ct_dep.alignment, _get_register_type(ct, ta))
    elif ct.node is cwast.DefRec:
        size, alignment = _SetAbiInfoRecursivelyForRec(ct, ta)
        ct.finalize(size, alignment, _get_register_type(ct, ta))
    else:
        assert False, f"unknown type {ct}"


class TypeCorpus:
    """The type corpus uniquifies types

    It does so by representing each type with a string (basically a serialized
    version of type like "array<ptr<u32>,128>").
    That serialized version is mapped back to a structural version expressed
    using AST nodes.
    """

    def __init__(self, target_arch_config: TargetArchConfig):
        self._target_arch_config: TargetArchConfig = target_arch_config
        self._base_type_map: dict[cwast.BASE_TYPE_KIND, cwast.CanonType] = {}
        self._typeid_curr = 0
        # maps to ast
        self.topo_order: list[cwast.CanonType] = []
        self.corpus: dict[str, cwast.CanonType] = {}  # name to canonical type
        self._initial_typing = True

        # VOID should get typeid zero
        ct = self._InsertBaseType(cwast.BASE_TYPE_KIND.VOID)
        self._base_type_map[cwast.BASE_TYPE_KIND.VOID] = ct

        for kind in cwast.BASE_TYPE_KIND:
            if kind.name in ("INVALID", "UINT", "SINT", "TYPEID", "VOID"):
                continue
            ct = self._InsertBaseType(kind)
            self._base_type_map[kind] = ct

        self._base_type_map[cwast.BASE_TYPE_KIND.SINT] = self._base_type_map[
            cwast.BASE_TYPE_KIND.MakeSint(target_arch_config.sint_bitwidth)]
        self._base_type_map[cwast.BASE_TYPE_KIND.UINT] = self._base_type_map[
            cwast.BASE_TYPE_KIND.MakeUint(target_arch_config.uint_bitwidth)]
        self._base_type_map[cwast.BASE_TYPE_KIND.TYPEID] = self._base_type_map[
            cwast.BASE_TYPE_KIND.MakeUint(target_arch_config.typeid_bitwidth)]

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

    def SetAbiInfoForall(self):
        for ct in self.corpus.values():
            SetAbiInfoRecursively(ct, self._target_arch_config)
        self._initial_typing = False

    def _insert(self, ct: cwast.CanonType) -> cwast.CanonType:
        """The only type not finalized here are Recs"""
        assert ct.name not in self.corpus, f"duplicate insertion of type: {ct.name}"

        # print(f">>>>>>>> ",  ct.name,  ct.typeid, ct.original_type)
        self.corpus[ct.name] = ct
        self.topo_order.append(ct)
        assert STRINGIFIEDTYPE_RE.fullmatch(
            ct.name), f"bad type name [{ct.name}]"
        if not self._initial_typing:
            SetAbiInfoRecursively(ct, self._target_arch_config)
        if not ct.original_type:
            ct.typeid = self._typeid_curr
            self._typeid_curr += 1
        return ct

    def _InsertBaseType(self, kind: cwast.BASE_TYPE_KIND) -> cwast.CanonType:
        ct = cwast.CanonType(
            cwast.TypeBase, cwast.BaseTypeKindToKeyword(kind), base_type_kind=kind)
        return self._insert(ct)

    def InsertPtrType(self, mut: bool, ct: cwast.CanonType) -> cwast.CanonType:
        name = f"ptr_mut<{ct.name}>" if mut else f"ptr<{ct.name}>"
        if name in self.corpus:
            return self.corpus[name]
        ct = cwast.CanonType(cwast.TypePtr, name, mut=mut, children=[ct])
        return self._insert(ct)

    def InsertSpanType(self, mut: bool, ct: cwast.CanonType) -> cwast.CanonType:
        name = f"span_mut<{ct.name}>" if mut else f"span<{ct.name}>"
        if name in self.corpus:
            return self.corpus[name]
        ct = cwast.CanonType(cwast.TypeSpan, name, mut=mut, children=[ct])
        return self._insert(ct)

    def InsertVecType(self, dim: int, ct: cwast.CanonType) -> cwast.CanonType:
        name = f"vec<{dim},{ct.name}>"
        if name in self.corpus:
            return self.corpus[name]
        ct = cwast.CanonType(cwast.TypeVec, name, dim=dim, children=[ct])
        return self._insert(ct)

    def InsertRecType(self, name: str, ast_node: cwast.DefRec) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        assert isinstance(ast_node, cwast.DefRec)
        name = f"rec<{name}>"
        ct = cwast.CanonType(cwast.DefRec, name, ast_node=ast_node)
        return self._insert(ct)

    def InsertEnumType(self, name: str, ast_node: cwast.DefEnum) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        assert isinstance(ast_node, cwast.DefEnum)
        name = f"enum<{name}>"
        ct = cwast.CanonType(cwast.DefEnum, name,
                             base_type_kind=ast_node.base_type_kind, ast_node=ast_node)
        return self._insert(ct)

    def InsertUnionType(self, untagged: bool, components: list[cwast.CanonType]) -> cwast.CanonType:
        assert len(components) > 1
        pp = set()
        for c in components:
            if c.node is cwast.TypeUnion and c.untagged == untagged:
                for cc in c.children:
                    pp.add(cc)
            else:
                pp.add(c)
        sorted_children = sorted(pp)
        sorted_names = [x.name for x in sorted(sorted_children)]
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
        ct = cwast.CanonType(cwast.TypeFun, name, children=params + [result])
        return self._insert(ct)

    def InsertWrappedTypePrep(self, name: str) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        name = f"wrapped<{name}>"
        assert name not in self.corpus
        ct = cwast.CanonType(cwast.DefType, name)
        return self._insert(ct)

    def InsertWrappedTypeFinalize(self, ct: cwast.CanonType,
                                  ct_wrapped: cwast.CanonType):
        assert not ct_wrapped.is_wrapped()
        ct.children = [ct_wrapped]

    def insert_union_complement(self, all: cwast.CanonType, part: cwast.CanonType) -> cwast.CanonType:
        assert all.node is cwast.TypeUnion, f"expect sum type: {all.name}"
        # we could use a set here but the number of union elements will be small
        if part.node is cwast.TypeUnion:
            part_children = part.children
        else:
            part_children = [part]
        out = []
        for x in all.children:
            if x not in part_children:
                out.append(x)
        assert out, "empty union complement"
        if len(out) == 1:
            return out[0]

        return self.InsertUnionType(all.untagged, out)
