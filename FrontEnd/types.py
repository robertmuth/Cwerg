
import logging

from FrontEnd import cwast

from typing import List, Dict, Set, Optional, Union, Any

logger = logging.getLogger(__name__)


CanonType = str
NO_TYPE = "typeless"


def align(x, a):
    return (x + a - 1) // a * a


def get_children_types(cstr: CanonType) -> List[CanonType]:
    out: List[CanonType] = []
    cstr = cstr.split("(", 1)[1][:-1]
    open_paren = 0
    start = 0
    for n, c in enumerate(cstr):
        if c == ',' and open_paren == 0:
            out.append(cstr[start:n])
            start = n+1
        elif c == '(':
            open_paren += 1
        elif c == ")":
            open_paren -= 1
    out.append(cstr[start:])
    return out


def get_contained_type(cstr: CanonType) -> CanonType:
    if cstr.startswith("array("):
        return cstr[6:].rsplit(",", 1)[0]
    elif cstr.startswith("array-mut("):
        return cstr[10:].rsplit(",", 1)[0]
    elif cstr.startswith("slice("):
        return cstr[6:-1]
    elif cstr.startswith("slice-mut("):
        return cstr[10:-1]
    else:
        assert False


def get_array_dim(cstr: CanonType) -> int:
    if cstr.startswith("array(") or cstr.startswith("array-mut("):
        return int(cstr[:-1].rsplit(",", 1)[1])
    else:
        assert False


def get_pointee(cstr: CanonType) -> CanonType:
    assert cstr.startswith("ptr"), f"expected pointer got {cstr}"
    return cstr.split("(", 1)[1][:-1]


def is_array(cstr: CanonType) -> bool:
    return cstr.startswith("array")


def is_ptr(cstr: CanonType) -> bool:
    return cstr.startswith("ptr")


def is_mutable(cstr: CanonType) -> bool:
    return cstr.startswith("ptr-mut") or cstr.startswith("slice-mut") or cstr.startswith("array-mut")


def is_sum(cstr: CanonType) -> bool:
    return cstr.startswith("sum")


def is_fun(cstr: CanonType) -> bool:
    return cstr.startswith("fun")


def is_bool(cstr: CanonType) -> bool:
    return cstr == "bool"


def is_wrapped(cstr: CanonType) -> bool:
    return cstr == "wrapped"


def is_void(cstr: CanonType) -> bool:
    return cstr == "void"


def is_int(cstr: CanonType) -> bool:
    return cstr in ("u8", "u16", "u32", "u64", "s8", "s16", "s32", "s64")


def is_real(cstr: CanonType) -> bool:
    return cstr in ("r32", "r64")


def is_compatible(actual: CanonType, expected: CanonType) -> bool:
    if actual == expected:
        return True

    if actual.startswith("slice-mut(") and expected.startswith("slice("):
        if actual[10:] == expected[6:]:
            return True

    if actual.startswith("array") and expected.startswith("slice"):
        comma = actual.rfind(",")
        if actual[5:comma] == expected[5:-1]:
            return True

    expected_children = set(get_children_types(expected))
    if actual in expected_children:
        return True

    if not is_sum(expected):
        return False

    if not is_sum(actual):
        return False

    actual_children = set(get_children_types(actual))
    return actual_children.issubset(expected_children)

# def GetStructOffset(node: cwast.DefRec, field_name: str) -> int:
#     offset = 0
#     for f in node:
#         if f.name == field.name:
#             return offset
#         s, a = SizeOfAndAlignment(f.type, meta_info)
#         offset = align(offset, a) + s
#     assert False, f"GetStructOffset unknown field {struct} {field}"


# def ScalarBitSize(cstr:CanonType, ptr_size: int) -> int:


# def SizeOfAndAlignmentStruct(struct: c_ast.Struct, meta_info):
#     if struct.decls is None:
#         struct = meta_info.struct_links[struct]
#     alignment = 1
#     size = 0
#     for f in struct.decls:
#         s, a = SizeOfAndAlignment(f.type, meta_info)
#         if a > alignment:
#             alignment = a
#         size = align(size, a) + s
#         # print ("@@", s, a, size, alignment, f)

#     return size, alignment

# def SizeOfAndAlignment(node, meta_info):
#     if isinstance(node, (c_ast.Typename, c_ast.Decl, c_ast.TypeDecl)):
#         return SizeOfAndAlignment(node.type, meta_info)

#     if isinstance(node, c_ast.Struct):
#         return SizeOfAndAlignmentStruct(node, meta_info)
#     elif isinstance(node, c_ast.Union):
#         return SizeOfAndAlignmentUnion(node, meta_info)
#     elif isinstance(node, c_ast.IdentifierType):
#         type_name = TYPE_TRANSLATION[tuple(node.names)]
#         assert type_name, f"could not determine sizeof {node}"
#         bitsize = int(type_name[1:])
#         return bitsize // 8, bitsize // 8
#     elif isinstance(node, c_ast.ArrayDecl):
#         size, align = SizeOfAndAlignment(node.type, meta_info)
#         size = (size + align - 1) // align * align
#         return size * int(node.dim.value), align
#     elif isinstance(node, c_ast.PtrDecl):
#         type_name = TYPE_TRANSLATION[POINTER]
#         bitsize = int(type_name[1:])
#         return bitsize // 8, bitsize // 8
#     else:
#         assert False, node

class TypeCorpus:
    """The type corpus uniquifies types

    It does so by representing each type with a string (basically a serialized
    version of type like "array(ptr(u32),128)").
    That serialized version is mapped back to a structural version expressed
    using AST nodes.
    """

    def __init__(self, uint_kind, sint_kind):
        self.uint_kind = uint_kind
        self.sint_kind = sint_kind

        self.wrapped_curr = 1
        # maps to ast
        self.corpus: Dict[CanonType, Any] = {}
        self._canon_name: Dict[int, CanonType] = {}

        for kind in cwast.BASE_TYPE_KIND:
            if kind.name in ("INVALID", "UINT", "SINT"):
                continue
            self.insert_base_type(kind)

    def _insert(self, name, node) -> CanonType:
        if name in self.corpus:
            return name
        assert isinstance(
            node, cwast.TYPE_CORPUS_NODES), f"not a corpus node: {node}"
        assert name not in self.corpus
        self.corpus[name] = node
        assert id(node) not in self._canon_name
        self._canon_name[id(node)] = name
        return name

    def insert_base_type(self, kind: cwast.BASE_TYPE_KIND) -> CanonType:
        if kind == cwast.BASE_TYPE_KIND.UINT:
            kind = self.uint_kind
        elif kind == cwast.BASE_TYPE_KIND.SINT:
            kind = self.sint_kind
        name = kind.name.lower()
        return self._insert(name, cwast.TypeBase(kind))
    

    def insert_ptr_type(self, mut: bool, cstr: CanonType) -> CanonType:
        if mut:
            name = f"ptr-mut({cstr})"
        else:
            name = f"ptr({cstr})"
        return self._insert(name, cwast.TypePtr(mut, self.corpus[cstr]))

    def insert_slice_type(self, mut: bool, cstr: CanonType) -> CanonType:
        if mut:
            name = f"slice-mut({cstr})"
        else:
            name = f"slice({cstr})"
        return self._insert(name, cwast.TypeSlice(mut, self.corpus[cstr]))

    def insert_array_type(self, mut: bool, size: int, cstr: CanonType) -> CanonType:
        if mut:
            name = f"array-mut({cstr},{size})"
        else:
            name = f"array({cstr},{size})"
        return self._insert(name, cwast.TypeArray(size, self.corpus[cstr]))

    def lookup_rec_field(self, rec_cstr: CanonType, field_name):
        """Oddball since the node returned is NOT inside corpus

        See implementation of insert_rec_type
        """
        node = self.corpus[rec_cstr]
        assert isinstance(node, cwast.DefRec)
        for x in node.fields:
            if isinstance(x, cwast.RecField) and x.name == field_name:
                return x
        assert False

    def get_fields(self, rec_cstr) -> List[str]:
        """Oddball since the node returned is NOT inside corpus

        See implementation of insert_rec_type
        """
        node = self.corpus[rec_cstr]
        assert isinstance(node, cwast.DefRec)
        return [x for x in node.fields if isinstance(x, cwast.RecField)]

    def insert_rec_type(self, name: str, node: cwast.DefRec) -> CanonType:
        """Note: we tr-use the original ast node"""
        name = f"rec({name})"
        return self._insert(name, node)

    def insert_enum_type(self, name: str, node: cwast.DefEnum) -> CanonType:
        """Note: we tr-use the original ast node"""
        assert isinstance(node, cwast.DefEnum)
        name = f"enum({name})"
        return self._insert(name, node)

    def insert_sum_type(self, components: List[CanonType]) -> CanonType:
        assert len(components) > 1
        pieces = []
        for c in components:
            node = self.corpus[c]
            if isinstance(node, cwast.TypeSum):
                for cc in node.types:
                    pieces.append(cc)
            else:
                pieces.append(node)
        pp = sorted(self._canon_name[id(p)] for p in pieces)
        name = f"sum({','.join(pp)})"
        return self._insert(name, cwast.TypeSum(pieces))

    def insert_fun_type(self, params: List[CanonType], result: CanonType) -> CanonType:
        name = f"fun({','.join(params +[result])})"
        p = [cwast.FunParam("_", self.corpus[x]) for x in params]
        return self._insert(name, cwast.TypeFun(p, self.corpus[result]))

    def insert_wrapped_type(self, cstr: CanonType, node: cwast.DefType) -> CanonType:
        """Note: we tr-use the original ast node"""
        assert isinstance(node, cwast.DefType)
        uid = self.wrapped_curr
        self.wrapped_curr += 1
        name = f"wrapped({uid},{cstr})"
        assert name not in self.corpus
        return self._insert(name, node)

    def insert_sum_complement(self, all: CanonType, part: CanonType) -> CanonType:
        assert is_sum(all)
        if is_sum(part):
            part_children = get_children_types(part) + [None]
        else:
            part_children = [part, None]
        out = []
        i = 0
        for x in get_children_types(all):
            if x == part_children[i]:
                i += 1
            else:
                out.append(x)
        if len(out) == 1:
            return out[0]
        return self.insert_sum_type(out)

