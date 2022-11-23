
import logging

from FrontEnd import cwast

from typing import List, Dict, Tuple, Set, Optional, Union, Any

logger = logging.getLogger(__name__)


CanonType = str
NO_TYPE = None


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


def is_mutable(cstr: CanonType) -> bool:
    if isinstance(cstr, cwast.TypePtr):
        return cstr.mut
    elif isinstance(cstr, cwast.TypeSlice):
        return cstr.mut
    elif isinstance(cstr, cwast.TypeArray):
        return cstr.mut
    else:
        assert False


def is_bool(cstr: CanonType) -> bool:
    assert isinstance(cstr, cwast.TypeBase)
    return cstr.base_type_kind is cwast.BASE_TYPE_KIND.BOOL


def is_void(cstr: CanonType) -> bool:
    return isinstance(cstr, cwast.TypeBase) and cstr.base_type_kind is cwast.BASE_TYPE_KIND.VOID


def is_int(cstr: CanonType) -> bool:
    assert isinstance(cstr, cwast.TypeBase)
    return cstr.base_type_kind in cwast.BASE_TYPE_KIND_INT


def is_uint(cstr: CanonType) -> bool:
    assert isinstance(cstr, cwast.TypeBase)
    return cstr.base_type_kind in cwast.BASE_TYPE_KIND_UINT


def is_real(cstr: CanonType) -> bool:
    assert isinstance(cstr, cwast.TypeBase)
    return cstr.base_type_kind in cwast.BASE_TYPE_KIND_REAL


def is_number(cstr: CanonType) -> bool:
    if not isinstance(cstr, cwast.TypeBase):
        return False
    kind = cstr.base_type_kind
    return kind in cwast.BASE_TYPE_KIND_REAL or kind in cwast.BASE_TYPE_KIND_INT


def is_compatible(actual: CanonType, expected: CanonType) -> bool:
    if actual == expected:
        return True

    if isinstance(actual, cwast.TypeSlice) and actual.mut and isinstance(expected, cwast.TypeSlice):
        if actual.type == expected.type:
            return True

    if isinstance(actual, cwast.TypeArray) and isinstance(expected, cwast.TypeSlice):
        if actual.type == expected.type:
            return True

    if not isinstance(expected, cwast.TypeSum):
        return False

    expected_children = set([id(c) for c in expected.types])

    if isinstance(actual, cwast.TypeSum):
        actual_children = set([id(c) for c in actual.types])
    else:
        actual_children = set([id(actual)])

    return actual_children.issubset(expected_children)


class TypeCorpus:
    """The type corpus uniquifies types

    It does so by representing each type with a string (basically a serialized
    version of type like "array(ptr(u32),128)").
    That serialized version is mapped back to a structural version expressed
    using AST nodes.
    """

    def __init__(self, uint_kind: cwast.BASE_TYPE_KIND, sint_kind: cwast.BASE_TYPE_KIND):
        self.uint_kind: cwast.BASE_TYPE_KIND = uint_kind  # also used for ptr cast to ints
        self.sint_kind: cwast.BASE_TYPE_KIND = sint_kind

        self.wrapped_curr = 1
        # maps to ast
        self.corpus: Dict[int, Any] = {}
        self._canon_name: Dict[int, CanonType] = {}

        for kind in cwast.BASE_TYPE_KIND:
            if kind.name in ("INVALID", "UINT", "SINT"):
                continue
            self.insert_base_type(kind)

    def _insert(self, name, node) -> CanonType:
        if name in self.corpus:
            return self.corpus[name]
        assert cwast.NF.TYPE_CORPUS in node.__class__.FLAGS, f"not a corpus node: {node}"
        self.corpus[name] = node
        assert id(node) not in self._canon_name
        self._canon_name[id(node)] = name
        return node

    def insert_base_type(self, kind: cwast.BASE_TYPE_KIND) -> CanonType:
        if kind == cwast.BASE_TYPE_KIND.UINT:
            kind = self.uint_kind
        elif kind == cwast.BASE_TYPE_KIND.SINT:
            kind = self.sint_kind
        name = kind.name.lower()
        size = cwast.BASE_TYPE_KIND_TO_SIZE[kind]
        return self._insert(name, cwast.TypeBase(kind, x_size=size, x_alignment=size))

    def canon_name(self, node):
        return self._canon_name[id(node)]

    def insert_ptr_type(self, mut: bool, cstr: CanonType) -> CanonType:
        if mut:
            name = f"ptr-mut({cstr})"
        else:
            name = f"ptr({cstr})"
        size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
        return self._insert(name, cwast.TypePtr(mut, cstr, x_size=size, x_alignment=size))

    def insert_slice_type(self, mut: bool, cstr: CanonType) -> CanonType:
        if mut:
            name = f"slice-mut({cstr})"
        else:
            name = f"slice({cstr})"
        size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
        return self._insert(name, cwast.TypeSlice(mut, cstr, x_size=2 * size, x_alignment=size))

    def insert_array_type(self, mut: bool, len: int, cstr: CanonType) -> CanonType:
        if mut:
            name = f"array-mut({cstr},{len})"
        else:
            name = f"array({cstr},{len})"
        dim = cwast.ValNum(str(len))
        dim.x_value = len
        alignment = cstr.x_alignment
        size = cstr.x_size
        size = align(size, alignment)
        return self._insert(name, cwast.TypeArray(mut, dim, cstr, x_size=len*size, x_alignment=alignment))

    def lookup_rec_field(self, rec: cwast.DefRec, field_name) -> cwast.RecField:
        """Oddball since the node returned is NOT inside corpus

        See implementation of insert_rec_type
        """
        for x in rec.fields:
            if isinstance(x, cwast.RecField) and x.name == field_name:
                return x
        assert False

    def get_fields(self, rec_cstr) -> List[str]:
        """Oddball since the node returned is NOT inside corpus

        See implementation of insert_rec_type
        """
        node = self.corpus[id(rec_cstr)]
        assert isinstance(node, cwast.DefRec)
        return [x for x in node.fields if isinstance(x, cwast.RecField)]

    def _TypeBaseAlignmentSize(self, kind: cwast.BASE_TYPE_KIND):
        size = cwast.BASE_TYPE_KIND_TO_SIZE[kind]
        return size, size

    def _TypeSumAlignmentSize(self, node: cwast.TypeSum):
        num_void = 0
        num_pointer = 0
        num_other = 0
        ptr_size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
        max_size = 0
        max_alignment = 1
        for f in node.types:
            if isinstance(f, cwast.Comment):
                continue
            t = f.x_type
            if is_void(t):
                num_void += 1
            elif isinstance(t, cwast.TypePtr):
                num_pointer += 1
                max_size = max(max_size, ptr_size)
                max_alignment = max(max_alignment, ptr_size)
            else:
                num_other += 1
                alignment, size = self._AlignmentSize(t)
                max_size = max(max_size, size)
                max_alignment = max(max_alignment, alignment)
        if num_other == 0 and num_pointer == 1:
            # special hack for pointer + error-code
            return ptr_size, ptr_size
        max_alignment = max(max_alignment, 2)
        size = align(2, max_alignment)
        return max_alignment, size + max_size


    def _DecorateRecAlignmentOffsetSize(self, node: cwast.DefRec):
        max_alignment = 1
        total_size = 0
        for f in node.fields:
            if isinstance(f, cwast.RecField):
                alignment = -1
                size = -1
                t = f.x_type
                if isinstance(t, cwast.TypeArray):
                    pass
                elif isinstance(t, cwast.TypeSlice):
                    pass
                elif isinstance(t, cwast.TypeBase):
                    alignment, size = self._TypeBaseAlignmentSize(
                        t.base_type_kind)
                elif isinstance(t, cwast.TypeFun):
                    alignment, size = self._TypeBaseAlignmentSize(
                        self.uint_kind)
                elif isinstance(t, cwast.TypeSum):
                    pass
                elif isinstance(t, cwast.TypePtr):
                    alignment, size = self._TypeBaseAlignmentSize(
                        self.uint_kind)

    def insert_rec_type(self, name: str, node: cwast.DefRec) -> CanonType:
        """Note: we re-use the original ast node"""
        self._DecorateRecAlignmentOffsetSize(node)
        name = f"rec({name})"
        return self._insert(name, node)

    def insert_enum_type(self, name: str, node: cwast.DefEnum) -> CanonType:
        """Note: we tr-use the original ast node"""
        assert isinstance(node, cwast.DefEnum)
        name = f"enum({name})"
        size = cwast.BASE_TYPE_KIND_TO_SIZE[node.base_type_kind]
        node.x_size = size
        node.x_alignment = size
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
        pp = sorted(self._canon_name[id(p)] for p in pieces)
        name = f"sum({','.join(pp)})"
        return self._insert(name, cwast.TypeSum(pieces))

    def insert_fun_type(self, params: List[CanonType], result: CanonType) -> CanonType:
        x = [self.canon_name(p) for p in params]
        x.append(self.canon_name(result))
        name = f"fun({','.join(x)})"
        p = [cwast.FunParam("_", x) for x in params]
        size = cwast.BASE_TYPE_KIND_TO_SIZE[self.uint_kind]
        return self._insert(name, cwast.TypeFun(p, result, x_size=size, x_alignment=size))

    def insert_wrapped_type(self, cstr: CanonType, node: cwast.DefType) -> CanonType:
        """Note: we tr-use the original ast node"""
        assert isinstance(node, cwast.DefType)
        uid = self.wrapped_curr
        self.wrapped_curr += 1
        name = f"wrapped({uid},{cstr})"
        assert name not in self.corpus
        return self._insert(name, node)

    def insert_sum_complement(self, all: CanonType, part: CanonType) -> CanonType:
        assert isinstance(all, cwast.TypeSum)
        if isinstance(part, cwast.TypeSum):
            part_children = [id(c) for c in part.types]
        else:
            part_children = [id(part)]
        out = []
        for x in all.types:
            if id(x) not in part_children:
                out.append(x)
        if len(out) == 1:
            return out[0]
        return self.insert_sum_type(out)

    def drop_mutability(self, cstr: CanonType) -> CanonType:
        assert isinstance(cstr, cwast.TypeArray)
        name = self.canon_name(cstr)
        node = self.corpus.get("array" + name[9:])
        if node:
            return node
        node = cwast.TypeArray(cstr.mut, cstr.size, cstr.type)
        return self._insert(name, node)

    def num_type(self, num: str) -> CanonType:
        for x in ("s8", "s16", "s32", "s64", "u8", "u16", "u32", "u64", "r32", "r64"):
            if num.endswith(x):
                return self.corpus[x]
        if num.endswith("sint"):
            return self.corpus[self.sint_kind.name.lower()]
        elif num.endswith("uint"):
            return self.corpus[self.uint_kind.name.lower()]
        else:
            return NO_TYPE
