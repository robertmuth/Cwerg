"""All types have a canonical representation in the TypeCorpus"""
import logging
import re
import dataclasses

from typing import Optional

from FE import cwast
from IR import opcode_tab as o


logger = logging.getLogger(__name__)


STRINGIFIEDTYPE_RE = re.compile(r"[a-zA-Z][_A-Za-z_0-9$,<>/]+")


def align(x, a):
    return (x + a - 1) // a * a


def IsVecToSpanConversion(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    if not ct_src.is_vec():
        # TODO: check "ref"
        return False
    if not ct_dst.is_span():
        return False
    return ct_src.underlying_type() == ct_dst.underlying_type()


def IsDropMutConversion(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    if ct_src.original_type is not None:
        ct_src = ct_src.original_type
    if ct_dst.original_type is not None:
        ct_dst = ct_dst.original_type
    if (ct_src.is_ptr() and ct_dst.is_ptr() or
            ct_src.is_span() and ct_dst.is_span()):
        return ct_src.underlying_type() == ct_dst.underlying_type() and not ct_dst.is_mutable()
    return False


def IsSubtypeToUnionConversion(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    if ct_dst.is_union():
        dst_children = set([x.name for x in ct_dst.union_member_types()])
        if ct_src.is_union():
            if ct_dst.untagged != ct_src.untagged:
                return False
            return set([x.name for x in ct_src.union_member_types()]).issubset(dst_children)
        else:
            return ct_src.name in dst_children
    return False


def IsCompatibleType(src_ct: cwast.CanonType, dst_ct: cwast.CanonType,
                     src_is_writable) -> bool:
    if src_ct == dst_ct or src_ct.original_type == dst_ct:
        return True

    if IsDropMutConversion(src_ct, dst_ct):
        return True

    if src_is_writable or not dst_ct.mut:
        # only a write source of type vec can be converted to mutable span
        if IsVecToSpanConversion(src_ct, dst_ct):
            return True

    return IsSubtypeToUnionConversion(src_ct, dst_ct)


def UnwrapType(ct: cwast.CanonType, tc: "TypeCorpus") -> Optional[cwast.CanonType]:
    if ct.is_wrapped():
        return UnwrapType(ct.underlying_type(), tc)
    elif ct.is_enum():
        return None
    return ct


# maybe add records if all their fields are comparable?
def IsTypeForCmp(ct: cwast.CanonType) -> bool:
    unwrapped_ct = ct.get_unwrapped()
    return unwrapped_ct.is_base_type() or unwrapped_ct.is_ptr()


def IsTypeForEq(ct: cwast.CanonType) -> bool:
    unwrapped_ct = ct.get_unwrapped()
    return unwrapped_ct.is_base_type() or unwrapped_ct.is_ptr() or unwrapped_ct.is_fun()


def IsCompatibleTypeForEq(actual: cwast.CanonType, expected: cwast.CanonType) -> bool:
    if actual.original_type is not None:
        actual = actual.original_type
    if expected.original_type is not None:
        expected = expected.original_type

    if IsTypeForEq(actual):
        if actual == expected:
            return True

        if actual.is_ptr() and expected.is_ptr():
            return actual.underlying_type() == expected.underlying_type()

        if expected.tagged_union_contains(actual):
            return True

    if IsTypeForEq(expected) and actual.tagged_union_contains(expected):
        return True

    return False


def IsCompatibleTypeForCmp(actual: cwast.CanonType, expected: cwast.CanonType) -> bool:
    if not IsTypeForCmp(actual):
        return False

    return actual == expected or IsDropMutConversion(actual, expected)


def IsCompatibleTypeForAs(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    return (ct_src.is_base_type() and ct_dst.is_base_type() and
            ct_src.base_type_kind.IsNumber() and
            ct_dst.base_type_kind.IsNumber())


def IsCompatibleTypeForBitcast(ct_src: cwast.CanonType, ct_dst: cwast.CanonType) -> bool:
    unwrapped_src = ct_src.get_unwrapped()
    unwrapped_dst = ct_dst.get_unwrapped()

    if not unwrapped_src.is_base_type() and not unwrapped_src.is_ptr():
        return False
    if not unwrapped_dst.is_base_type() and not unwrapped_dst.is_ptr():
        return False
    return ct_src.aligned_size() == ct_dst.aligned_size()


def IsProperLhs(node) -> bool:
    if isinstance(node, cwast.Id):
        s = node.x_symbol
        if isinstance(s, (cwast.DefVar, cwast.DefGlobal)):
            return s.mut
        return False
    elif isinstance(node, cwast.ExprDeref):
        assert node.expr.x_type.is_ptr()
        return node.expr.x_type.is_mutable()
        # isinstance(node, cwast.ExprDeref) and types.is_mutable_def(node.expr) or
    elif isinstance(node, cwast.ExprField):
        return IsProperLhs(node.container)
    elif isinstance(node, cwast.ExprIndex):
        container_ct: cwast.CanonType = node.container.x_type
        if container_ct.is_span():
            return container_ct.mut
        else:
            assert container_ct.is_vec()
            return IsProperLhs(node.container)
    elif isinstance(node, cwast.ExprNarrow):
        return IsProperLhs(node.expr)
    else:
        return False


# maps FE types to BE names.
# Note: it would be cleaner to use the BE enum
_BASE_TYPE_MAP: dict[cwast.BASE_TYPE_KIND, o.DK] = {
    cwast.BASE_TYPE_KIND.S8: o.DK.S8,
    cwast.BASE_TYPE_KIND.S16: o.DK.S16,
    cwast.BASE_TYPE_KIND.S32: o.DK.S32,
    cwast.BASE_TYPE_KIND.S64: o.DK.S64,
    #
    cwast.BASE_TYPE_KIND.U8: o.DK.U8,
    cwast.BASE_TYPE_KIND.U16: o.DK.U16,
    cwast.BASE_TYPE_KIND.U32: o.DK.U32,
    cwast.BASE_TYPE_KIND.U64: o.DK.U64,
    #
    cwast.BASE_TYPE_KIND.R32: o.DK.R32,
    cwast.BASE_TYPE_KIND.R64: o.DK.R64,
    #
    cwast.BASE_TYPE_KIND.BOOL: o.DK.U8,
    #
    cwast.BASE_TYPE_KIND.VOID: o.DK.NONE,
    cwast.BASE_TYPE_KIND.NORET: o.DK.NONE,
}


@dataclasses.dataclass()
class TargetArchConfig:
    """target system config"""
    uint_bitwidth: int    # also used for ptr cast to ints
    sint_bitwidth: int
    typeid_bitwidth: int
    data_addr_bitwidth: int  # it is hard to imagine: data_addr_bitwidth != uint_bitwidth
    code_addr_bitwidth: int
    optimize_union_tag: bool

    def get_data_address_reg_type(self) -> o.DK:
        return o.DK.Make(o.DK_FLAVOR_A, self.data_addr_bitwidth)

    def get_code_address_reg_type(self) -> o.DK:
        return o.DK.Make(o.DK_FLAVOR_C, self.code_addr_bitwidth)

    def get_uint_reg_type(self) -> o.DK:
        return o.DK.Make(o.DK_FLAVOR_U, self.uint_bitwidth)

    def get_typeid_reg_type(self) -> o.DK:
        return o.DK.Make(o.DK_FLAVOR_U,  self.typeid_bitwidth)

    def get_sint_reg_type(self) -> o.DK:
        return o.DK.Make(o.DK_FLAVOR_S, self.sint_bitwidth)

    #
    def get_data_address_size(self) -> int:
        return self.data_addr_bitwidth // 8

    def get_code_address_size(self) -> int:
        return self.code_addr_bitwidth // 8

    def get_typeid_size(self) -> int:
        return self.typeid_bitwidth // 8


STD_TARGET_X64 = TargetArchConfig(64, 64, 16, 64, 64, False)
STD_TARGET_A64 = TargetArchConfig(64, 64, 16, 64, 64, False)
STD_TARGET_A32 = TargetArchConfig(32, 32, 16, 32, 32, False)


def _GetMachineRegsForUnion(ct: cwast.CanonType, ta: TargetArchConfig) -> o.DK:
    assert ct.node is cwast.TypeUnion
    num_void = 0
    scalars: list[cwast.CanonType] = []
    largest_by_kind: dict[str, int] = {}
    largest = 0
    for t in ct.union_member_types():
        rt = t.ir_regs
        if rt == o.DK.NONE:
            num_void += 1
            continue
        if rt == o.DK.MEM:
            return o.DK.MEM
        scalars.append(t)
        flavor = rt.flavor()
        bitwidth = rt.bitwidth()
        largest_by_kind[flavor] = max(largest_by_kind.get(flavor, 0), bitwidth)
        largest = max(largest, bitwidth)
    # special hack for pointer + error-code
    if ta.optimize_union_tag and len(scalars) == 1 and scalars[0].is_ptr():
        return scalars[0].ir_regs

    # BUG repro:
    # ./compiler.py LangTest/linked_list_gen_test.cw
    # ./compiler.py LangTest/sum_tagged_test.cw
    if ct.untagged:
        if largest == 0:
            return o.DK.NONE
        return o.DK.Make(o.DK_FLAVOR_U, largest)

    if largest == 0:
        return ta.get_typeid_reg_type()
    return o.DK.MEM


def _GetMachineRegs(ct: cwast.CanonType, ta: TargetArchConfig) -> o.DK:
    """As long as a type can fit into no more than two regs it will have
    register representation which is also how it will be past in function calls.

    Note: this will only be called for non-zero sized types
    """
    if ct.node is cwast.TypeBase:
        return _BASE_TYPE_MAP.get(ct.base_type_kind)
    elif ct.node is cwast.TypePtr:
        return ta.get_data_address_reg_type()
    elif ct.node is cwast.TypeSpan:
        return o.DK.MEM
    elif ct.node is cwast.DefRec:
        return o.DK.MEM
    elif ct.node is cwast.TypeVec:
        return o.DK.MEM
    elif ct.node is cwast.DefEnum:
        return _BASE_TYPE_MAP[ct.underlying_type().base_type_kind]
    elif ct.node is cwast.TypeUnion:
        return _GetMachineRegsForUnion(ct, ta)
    elif ct.node is cwast.DefType:
        return _GetMachineRegs(ct.underlying_type(), ta)
    elif ct.node is cwast.TypeFun:
        return ta.get_code_address_reg_type()
    else:
        assert False, f"unknown type {ct.name}"
        return cwast.MACHINE_REGS_IN_MEMORY


def _GetSizeAndAlignmentForSum(ct: cwast.CanonType, ta: TargetArchConfig) -> tuple[int, int]:
    assert ct.node is cwast.TypeUnion
    num_pointer = 0
    num_other = 0
    max_size = 0
    max_alignment = 1
    ptr_size = ta.get_data_address_size()
    for child_ct in ct.union_member_types():
        if child_ct.size == 0:
            continue
        while child_ct.is_wrapped():
            child_ct = child_ct.children[0]
        if child_ct.is_ptr():
            num_pointer += 1
            max_size = max(max_size, ptr_size)
            max_alignment = max(max_alignment, ptr_size)
        else:
            num_other += 1
            assert child_ct.size >= 0, f"{ct} size is not yet known"
            max_size = max(max_size, child_ct.size)
            max_alignment = max(max_alignment, child_ct.alignment)
    if ct.untagged:
        return max_size, max_alignment
    if ta.optimize_union_tag and num_other == 0 and num_pointer == 1:
        # special hack for pointer + error-code
        return ptr_size, ptr_size
    tag_size = ta.get_typeid_size()
    # the tag is the first component of the tagged union in memory
    max_alignment = max(max_alignment, tag_size)
    return align(tag_size, max_alignment) + max_size, max_alignment


def _GetSizeAndAlignmentForRec(ct: cwast.CanonType) -> tuple[int, int]:
    assert isinstance(ct.ast_node, cwast.DefRec)
    def_rec: cwast.DefRec = ct.ast_node
    assert ct.children, f"{def_rec}"
    size = 0
    alignment = 1
    for rf in def_rec.fields:
        assert isinstance(rf, cwast.RecField)
        field_ct: cwast.CanonType = rf.type.x_type
        size = align(size, field_ct.alignment)
        # only place where x_offset is set
        rf.x_offset = size
        size += field_ct.size
        alignment = max(alignment, field_ct.alignment)
    return size, alignment


def _GetSizeAndAlignment(ct: cwast.CanonType,  ta: TargetArchConfig):
    n = ct. node
    if n is cwast.TypeBase:
        size = ct.base_type_kind.ByteSize()
        return size, size
    elif n is cwast.TypePtr:
        size = ta.get_code_address_size()
        return size, size
    elif n is cwast.TypeSpan:
        # span is converted to (pointer, length) tuple
        ptr_field_size = ta.get_data_address_size()
        len_field_size = ta.uint_bitwidth // 8
        return ptr_field_size + len_field_size, ptr_field_size,
    elif n is cwast.TypeVec:
        ct_dep = ct.children[0]
        return ct_dep.aligned_size() * ct.dim, ct_dep.alignment,
    elif n is cwast.TypeUnion:
        return _GetSizeAndAlignmentForSum(ct, ta)
    elif n is cwast.DefEnum:
        size = ct.children[0].base_type_kind.ByteSize()
        return size, size
    elif n is cwast.TypeFun:
        size = ta.get_code_address_size()
        return size, size
    elif n is cwast.DefType:
        ct_dep = ct.children[0]
        return ct_dep.size, ct_dep.alignment
    elif n is cwast.DefRec:
        return _GetSizeAndAlignmentForRec(ct)
    else:
        assert False, f"unknown type {ct}"


def SetAbiInfoRecursively(ct: cwast.CanonType, ta: TargetArchConfig):
    if ct.alignment >= 0:
        # already processed
        return
    n = ct.node
    if n != cwast.TypePtr and n != cwast.TypeFun:
        # the size of TypePtr and cwast.TypeFun does not depend
        # on their children.
        # This also prevents infinite recursion (mostly applies to TypePtr), e.g.:
        #
        # pub rec LinkedListNode:
        #     next union(NoneType, ^!LinkedListNode)
        #     payload u32
        for ct_field in ct.children:
            SetAbiInfoRecursively(ct_field, ta)
        # Note, for records the children are empty!
        # They do NOT contain the record fields
        # This helps keeping the type graph acyclic.
        if n == cwast.DefRec:
            for rf in ct.ast_node.fields:
                assert isinstance(rf, cwast.RecField)
                SetAbiInfoRecursively(rf.type.x_type, ta)
    size, alignment = _GetSizeAndAlignment(ct, ta)
    machines_regs = o.DK.NONE if size == 0 else _GetMachineRegs(ct, ta)
    ct.Finalize(size, alignment, machines_regs)


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
        # will be set to False by SetAbiInfoForall() after which the AbiInfo
        # will be set as soon as a new CanonType is created.
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

    def InsertRecType(self, name: str, ast_node: cwast.DefRec, process_children) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        assert isinstance(ast_node, cwast.DefRec)
        name = f"rec<{name}>"
        children = []
        if process_children:
            for rf in ast_node.fields:
                assert isinstance(rf, cwast.RecField)
                assert rf.x_type is not cwast.NO_TYPE
                children.append(rf.type.x_type)
        ct = cwast.CanonType(cwast.DefRec, name,
                             ast_node=ast_node, children=children)
        return self._insert(ct)

    def InsertEnumType(self, name: str, ast_node: cwast.DefEnum) -> cwast.CanonType:
        """Note: we re-use the original ast node"""
        assert isinstance(ast_node, cwast.DefEnum)
        name = f"enum<{name}>"
        bt_kind = ast_node.base_type_kind
        assert bt_kind.IsInt()
        bt = self.get_base_canon_type(bt_kind)
        ct = cwast.CanonType(cwast.DefEnum, name,
                             ast_node=ast_node, children=[bt])
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

    def MaybeGetReplacementType(self, ct: cwast.CanonType) -> Optional[cwast.CanonType]:
        assert ct.node not in (cwast.DefRec, cwast.DefType)
        if ct.replacement_type:
            return ct.replacement_type
        for child in ct.children:
            if child.replacement_type:
                break
        else:
            return None
        replacement_children = []
        for child in ct.children:
            if child.replacement_type:
                replacement_children.append(child.replacement_type)
            else:
                replacement_children.append(child)
        if ct.node is cwast.TypePtr:
            return self.InsertPtrType(ct.mut, replacement_children[0])
        elif ct.node is cwast.TypeSpan:
            return self.InsertSpanType(ct.mut, replacement_children[0])
        elif ct.node is cwast.TypeVec:
            return self.InsertVecType(ct.array_dim(), replacement_children[0])
        elif ct.node is cwast.TypeFun:
            return self.InsertFunType(
                replacement_children[:-1], replacement_children[-1])

        elif ct.node is cwast.TypeUnion:
            return self.InsertUnionType(ct.untagged, replacement_children)
        else:
            assert False, f"cannot make replacement type for {ct.name} {ct.node}"
            return None

    def ClearReplacementInfo(self):
        for ct in self.topo_order:
            ct.replacement_type = None

    def Dump(self):
        print(f"Dump of CanonTypes: ({len(self.corpus)})")
        for name, ct in sorted((x.typeid, x) for x in self.corpus.values()):
            original = -1
            if ct.original_type:
                original = ct.original_type.typeid
            print(
                f"{ct.name} id={ct.typeid} size={ct.size} align={ct.alignment} original={original} ir={ct.ir_regs}")
