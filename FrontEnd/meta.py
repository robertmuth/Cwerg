#!/usr/bin/python3

"""Type annotator for Cwerg AST

"""

import dataclasses
from inspect import signature
from math import exp
import sys
import logging

from FrontEnd import cwast
from FrontEnd import symtab

from typing import List, Dict, Set, Optional, Union, Any

logger = logging.getLogger(__name__)


CanonType = str
NO_TYPE = "typeless"


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


class TypeContext:
    def __init__(self, symtab, mod_name):
        self.symtab: symtab.SymTab = symtab
        self.mod_name: str = mod_name
        self.enclosing_fun: Optional[cwast.DefFun] = None
        self._enclosing_rec_type: List[CanonType] = []
        self._target_type: List[CanonType] = [NO_TYPE]

    def push_target(self, cstr: CanonType):
        """use to suport limited type inference

        contains the type the current expression/type is expected to
        have or NO_TYPE
        """

        self._target_type.append(cstr)

    def pop_target(self):
        self._target_type.pop(-1)

    def get_target_type(self):
        return self._target_type[-1]


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
        self.corpus: Dict[CanonType, Any] = {}
        self._links: Dict[int, CanonType] = {}

        for kind in cwast.BASE_TYPE_KIND:
            if kind.name in ("INVALID", "UINT", "SINT"):
                continue
            self.insert_base_type(kind)

    def _insert(self, name, node):
        assert isinstance(
            node, cwast.TYPE_CORPUS_NODES), f"not a corpus node: {node}"
        assert name not in self.corpus
        self.corpus[name] = node
        assert id(node) not in self._links
        self._links[id(node)] = name

    def insert_base_type(self, kind: cwast.BASE_TYPE_KIND) -> CanonType:
        if kind == cwast.BASE_TYPE_KIND.UINT:
            kind = self.uint_kind
        elif kind == cwast.BASE_TYPE_KIND.SINT:
            kind = self.sint_kind
        name = kind.name.lower()
        if name not in self.corpus:
            self._insert(name, cwast.TypeBase(kind))
        return name

    def insert_ptr_type(self, mut: bool, cstr: CanonType) -> CanonType:
        if mut:
            name = f"ptr-mut({cstr})"
        else:
            name = f"ptr({cstr})"
        if name not in self.corpus:
            self._insert(name, cwast.TypePtr(mut, self.corpus[cstr]))
        return name

    def insert_slice_type(self, mut: bool, cstr: CanonType) -> CanonType:
        if mut:
            name = f"slice-mut({cstr})"
        else:
            name = f"slice({cstr})"
        if name not in self.corpus:
            self._insert(name, cwast.TypeSlice(mut, self.corpus[cstr]))
        return name

    def insert_array_type(self, mut: bool, size: int, cstr: CanonType) -> CanonType:
        if mut:
            name = f"array-mut({cstr},{size})"
        else:
            name = f"array({cstr},{size})"
        if name not in self.corpus:
            self._insert(name, cwast.TypeArray(size, self.corpus[cstr]))
        return name

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

    def insert_rec_type(self, name: str, node) -> CanonType:
        name = f"rec({name})"
        if name not in self.corpus:
            assert isinstance(node, cwast.DefRec), f"{name} {node}"
            self._insert(name, node)
        return name

    def insert_enum_type(self, name: str, node) -> CanonType:
        assert isinstance(node, cwast.DefEnum)
        name = f"enum({name})"
        if name not in self.corpus:
            self._insert(name, node)
        return name

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
        pp = sorted(self._links[id(p)] for p in pieces)
        name = f"sum({','.join(pp)})"
        if name not in self.corpus:
            self._insert(name, cwast.TypeSum(pieces))
        return name

    def insert_fun_type(self, params: List[CanonType], result: CanonType) -> CanonType:
        name = f"fun({','.join(params +[result])})"
        if name not in self.corpus:
            p = [cwast.FunParam("_", self.corpus[x]) for x in params]
            self._insert(name, cwast.TypeFun(p, self.corpus[result]))
        return name

    def insert_wrapped_type(self, cstr: CanonType, node) -> CanonType:
        assert isinstance(node, cwast.DefType)
        uid = self.wrapped_curr
        self.wrapped_curr += 1
        name = f"wrapped({uid},{cstr})"
        assert name not in self.corpus
        self._insert(name, node)
        return name

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


def ComputeStringSize(raw: bool, string: str) -> int:
    assert string[0] == '"'
    assert string[-1] == '"'
    string = string[1:-1]
    n = len(string)
    if raw:
        return n
    esc = False
    for c in string:
        if esc:
            esc = False
            if c == "x":
                n -= 3
            else:
                n -= 1
        elif c == "\\":
            esc = True
    return 8


def ParseInt(num: str) -> int:
    num = num.replace("_", "")
    if num[-3:] in ("u16", "u32", "u64", "s16", "s32", "s64"):
        return int(num[: -3])
    elif num[-2:] in ("u8", "s8"):
        return int(num[: -2])
    else:
        return int(num)


class TypeTab:
    """Type Table

    Requires SymTab info to resolve DefType symnbols
    """

    def __init__(self, uint_kind, sint_kind):
        self.wrapped_curr = 1
        self.corpus = TypeCorpus(uint_kind, sint_kind)
        self.dims: Dict[int, int] = {}
        # links node-ids to strings from corpus
        self._links: Dict[int, CanonType] = {}
        # links nodes with
        self._field_links: Dict[int, cwast.RecField] = {}

    def type_link(self, node) -> CanonType:
        return self._links[id(node)]

    def field_link(self, node) -> cwast.RecField:
        return self._field_links[id(node)]

    def compute_dim(self, node, ctx) -> int:
        if isinstance(node, cwast.ValNum):
            return ParseInt(node.number)
        elif isinstance(node, cwast.Id):
            node = ctx.symtab.get_definition_for_symbol(node)
            return self.compute_dim(node, ctx)
        elif isinstance(node, cwast.DefConst):
            return self.compute_dim(node.value, ctx)
        else:
            assert False, f"unexpected dim node: {node}"

    def annotate(self, node, cstr: CanonType):
        assert cstr != NO_TYPE, f"no_type for: {node}"
        assert isinstance(
            node, cwast.TYPED_ANNOTATED_NODES), f"node not meant for type annotation: {node}"
        assert cstr, f"No valid type for {node}"
        assert id(node) not in self._links, f"duplicate annotation for {node}"
        self._links[id(node)] = cstr
        return cstr

    def annotate_field(self, node, field_node):
        assert isinstance(node, (cwast.ExprField, cwast.FieldVal))
        assert isinstance(field_node, cwast.RecField)
        self._field_links[id(node)] = field_node

    def num_type(self, num: str) -> CanonType:
        for x in ("s8", "s16", "s32", "s64", "u8", "u16", "u32", "u64", "r32", "r64"):
            if num.endswith(x):
                return x
        if num.endswith("sint"):
            return cwast.BASE_TYPE_KIND.SINT.name.lower()
        elif num.endswith("uint"):
            return cwast.BASE_TYPE_KIND.UINT.name.lower()
        else:
            return NO_TYPE

    def is_compatible_for_as(self, src: CanonType, dst: CanonType) -> bool:
        if is_wrapped(src):
            pass

        if is_int(src):
            return is_int(dst) or is_real(dst)

    def typify_node(self, node,  ctx: TypeContext) -> CanonType:
        target_type = ctx.get_target_type()
        extra = "" if target_type == NO_TYPE else f"[{target_type}]"
        logger.info(f"TYPIFYING{extra} {node}")
        cstr = self._links.get(id(node))
        if cstr is not None:
            # has been typified already
            return cstr
        if isinstance(node, cwast.Comment):
            return NO_TYPE
        elif isinstance(node, cwast.Id):
            # this case is why we need the sym_tab
            def_node = ctx.symtab.get_definition_for_symbol(node)
            # assert isinstance(def_node, cwast.DefType), f"unexpected node {def_node}"
            cstr = self.typify_node(def_node, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.TypeBase):
            return self.annotate(node, self.corpus.insert_base_type(node.base_type_kind))
        elif isinstance(node, cwast.TypePtr):
            t = self.typify_node(node.type, ctx)
            return self.annotate(node, self.corpus.insert_ptr_type(node.mut, t))
        elif isinstance(node, cwast.TypeSlice):
            t = self.typify_node(node.type, ctx)
            return self.annotate(node, self.corpus.insert_slice_type(node.mut, t))
        elif isinstance(node, cwast.FunParam):
            cstr = self.typify_node(node.type, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, (cwast.TypeFun, cwast.DefFun)):
            params = [self.typify_node(p, ctx)
                      for p in node.params if not isinstance(p, cwast.Comment)]
            result = self.typify_node(node.result, ctx)
            cstr = self.corpus.insert_fun_type(params, result)
            self.annotate(node, cstr)
            if isinstance(node, cwast.DefFun) and not node.extern:
                save_fun = ctx.enclosing_fun
                ctx.enclosing_fun = node
                for c in node.body:
                    self.typify_node(c, ctx)
                ctx.enclosing_fun = save_fun
            return cstr
        elif isinstance(node, cwast.TypeArray):
            # note this is the only place where we need a comptime eval for types
            t = self.typify_node(node.type, ctx)
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT))
            self.typify_node(node.size, ctx)
            ctx.pop_target()
            dim = self.compute_dim(node.size, ctx)
            return self.annotate(node, self.corpus.insert_array_type(False, dim, t))
        elif isinstance(node, cwast.RecField):
            cstr = self.typify_node(node.type, ctx)
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                ctx.push_target(cstr)
                self.typify_node(node.initial_or_undef, ctx)
                ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.DefRec):
            # allow recursive definitions referring back to rec inside
            # the fields
            cstr = self.corpus.insert_rec_type(node.name, node)
            self.annotate(node, cstr)
            for f in node.fields:
                self.typify_node(f, ctx)
            return cstr
        elif isinstance(node, cwast.EnumVal):
            cstr = ctx.get_target_type()
            if not isinstance(node.value, cwast.Auto):
                cstr = self.typify_node(node.value, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.DefEnum):
            cstr = self.corpus.insert_enum_type(
                f"{ctx.mod_name}/{node.name}", node)
            base_type = self.corpus.insert_base_type(node.base_type_kind)
            ctx.push_target(cstr)
            for f in node.items:
                if not isinstance(f, cwast.Comment):
                    self.typify_node(f, ctx)
            ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.DefType):
            cstr = self.typify_node(node.type, ctx)
            if node.wrapped:
                cstr = self.corpus.insert_wrapped_type(cstr, node)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.TypeSum):
            # this is tricky code to ensure that children of TypeSum
            # are not TypeSum themselves on the canonical side
            pieces = [self.typify_node(f, ctx) for f in node.types]
            return self.annotate(node, self.corpus.insert_sum_type(pieces))
        if isinstance(node, (cwast.ValTrue, cwast.ValFalse)):
            return self.annotate(node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
        elif isinstance(node, cwast.ValVoid):
            return self.annotate(node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.VOID))
        elif isinstance(node, cwast.ValUndef):
            assert False, "Must not try to typify UNDEF"
        elif isinstance(node, cwast.ValNum):
            cstr = self.num_type(node.number)
            if cstr != NO_TYPE:
                return self.annotate(node, cstr)
            return self.annotate(node, ctx.get_target_type())
        elif isinstance(node, cwast.Auto):
            assert False, "Must not try to typify AUTO"
        elif isinstance(node, cwast.DefConst):
            ctx.push_target(NO_TYPE if
                            isinstance(node.type_or_auto, cwast.Auto) else
                            self.typify_node(node.type_or_auto, ctx))
            cstr = self.typify_node(node.value, ctx)
            ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.IndexVal):
            cstr = ctx.get_target_type()
            if not isinstance(node.value_or_undef, cwast.ValUndef):
                self.typify_node(node.value_or_undef, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.ValArray):
            cstr = self.typify_node(node.type, ctx)
            ctx.push_target(cstr)
            for x in node.inits_array:
                if isinstance(x, cwast.IndexVal):
                    self.typify_node(x, ctx)
            ctx.pop_target()
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT))
            self.typify_node(node.expr_size, ctx)
            ctx.pop_target()
            dim = self.compute_dim(node.expr_size, ctx)
            return self.annotate(node, self.corpus.insert_array_type(False, dim, cstr))
        elif isinstance(node, cwast.ValRec):
            cstr = self.typify_node(node.type, ctx)
            all_fields: List[cwast.RecField] = self.corpus.get_fields(cstr)
            for val in node.inits_rec:
                if not isinstance(val, cwast.FieldVal):
                    continue
                if val.init_field:
                    while True:
                        field_node = all_fields.pop(0)
                        if val.init_field == field_node.name:
                            break
                else:
                    field_node = all_fields.pop(0)
                # TODO: make sure this link is set
                field_cstr = self.type_link(field_node)
                self.annotate_field(val, field_node)
                self.annotate(val, field_cstr)
                ctx.push_target(field_cstr)
                self.typify_node(val.value, ctx)
                ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.ValString):
            dim = ComputeStringSize(node.raw, node.string)
            cstr = self.corpus.insert_array_type(
                False, dim, self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.U8))
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.ExprIndex):
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT))
            self.typify_node(node.expr_index, ctx)
            ctx.pop_target()
            cstr = self.typify_node(node.container, ctx)
            return self.annotate(node, get_contained_type(cstr))
        elif isinstance(node, cwast.ExprField):
            cstr = self.typify_node(node.container, ctx)
            field_node = self.corpus.lookup_rec_field(cstr, node.field)
            self.annotate_field(node, field_node)
            return self.annotate(node, self._links[id(field_node)])
        elif isinstance(node, cwast.DefVar):
            cstr = (NO_TYPE if isinstance(node.type_or_auto, cwast.Auto)
                    else self.typify_node(node.type_or_auto, ctx))
            initial_cstr = NO_TYPE
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                ctx.push_target(cstr)
                initial_cstr = self.typify_node(node.initial_or_undef, ctx)
                ctx.pop_target()
            # special hack for arrays: if variable is mutable and of type array,
            # this means we can update array elements but we cannot assign a new
            # array to the variable.
            if is_array(initial_cstr) and node.mut:
                cstr = get_contained_type(initial_cstr)
                dim = get_array_dim(initial_cstr)
                return self.annotate(node, self.corpus.insert_array_type(True, dim, cstr))
            return self.annotate(node, cstr if cstr != NO_TYPE else initial_cstr)
        elif isinstance(node, cwast.ExprRange):
            cstr = self.typify_node(node.end, ctx)
            if not isinstance(node.begin_or_auto, cwast.Auto):
                self.typify_node(node.begin_or_auto, ctx)
            if not isinstance(node.step_or_auto, cwast.Auto):
                self.typify_node(node.step_or_auto, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.StmtFor):
            ctx.push_target(NO_TYPE if
                            isinstance(node.type_or_auto, cwast.Auto)
                            else self.typify_node(node.type_or_auto, ctx))
            cstr = self.typify_node(node.range, ctx)
            ctx.pop_target()
            self.annotate(node, cstr)
            for c in node.body:
                self.typify_node(c, ctx)
            return cstr
        elif isinstance(node, cwast.ExprDeref):
            cstr = self.typify_node(node.expr, ctx)
            # TODO: how is mutability propagated?
            return self.annotate(node, get_pointee(cstr))
        elif isinstance(node, cwast.Expr1):
            cstr = self.typify_node(node.expr, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.Expr2):
            cstr = self.typify_node(node.expr1, ctx)
            if node.binary_expr_kind in cwast.BINOP_OPS_HAVE_SAME_TYPE:
                ctx.push_target(cstr)
                self.typify_node(node.expr2, ctx)
                ctx.pop_target()
            else:
                self.typify_node(node.expr2, ctx)

            if node.binary_expr_kind in cwast.BINOP_BOOL:
                cstr = self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.BOOL)
            elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.PDELTA:
                cstr = self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.SINT)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.Expr3):
            self.typify_node(node.cond, ctx)
            cstr = self.typify_node(node.expr_t, ctx)
            ctx.push_target(cstr)
            self.typify_node(node.expr_f, ctx)
            ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.StmtExpr):
            self.typify_node(node.expr, ctx)
            return NO_TYPE
        elif isinstance(node, cwast.ExprCall):
            cstr = self.typify_node(node.callee, ctx)
            params = get_children_types(cstr)
            cstr = params.pop(-1)
            assert len(params) == len(node.args)
            for p, a in zip(params, node.args):
                ctx.push_target(p)
                self.typify_node(a, ctx)
                ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.StmtReturn):
            cstr = self._links[id(ctx.enclosing_fun.result)]
            ctx.push_target(cstr)
            self.typify_node(node.expr_ret, ctx)
            ctx.pop_target()
            return NO_TYPE
        elif isinstance(node, cwast.StmtIf):
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
            self.typify_node(node.cond, ctx)
            ctx.pop_target()
            for c in node.body_f:
                self.typify_node(c, ctx)
            for c in node.body_t:
                self.typify_node(c, ctx)
            return NO_TYPE
        elif isinstance(node, cwast.Case):
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
            self.typify_node(node.cond, ctx)
            ctx.pop_target()
            for c in node.body:
                self.typify_node(c, ctx)
            return NO_TYPE
        elif isinstance(node, cwast.StmtCond):
            for c in node.cases:
                self.typify_node(c, ctx)
            return NO_TYPE
        elif isinstance(node, cwast.StmtBlock):
            for c in node.body:
                self.typify_node(c, ctx)
            return NO_TYPE
        elif isinstance(node, cwast.StmtBreak):
            return NO_TYPE
        elif isinstance(node, cwast.StmtContinue):
            return NO_TYPE
        elif isinstance(node, cwast.StmtAssignment):
            var_cstr = self.typify_node(node.lhs, ctx)
            ctx.push_target(var_cstr)
            self.typify_node(node.expr, ctx)
            ctx.pop_target()
            return NO_TYPE
        elif isinstance(node, cwast.StmtCompoundAssignment):
            var_cstr = self.typify_node(node.lhs, ctx)
            ctx.push_target(var_cstr)
            self.typify_node(node.expr, ctx)
            ctx.pop_target()
            return NO_TYPE
        elif isinstance(node, (cwast.ExprAs, cwast.ExprBitCast, cwast.ExprUnsafeCast)):
            cstr = self.typify_node(node.type, ctx)
            self.typify_node(node.expr, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.ExprIs):
            self.typify_node(node.type, ctx)
            self.typify_node(node.expr, ctx)
            return self.annotate(node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
        elif isinstance(node, cwast.ExprLen):
            self.typify_node(node.container, ctx)
            return self.annotate(node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT))
        elif isinstance(node, cwast.ExprChop):
            if not isinstance(node.start, cwast.Auto):
                self.typify_node(node.start, ctx)
            if not isinstance(node.width, cwast.Auto):
                self.typify_node(node.width, ctx)
            cstr_cont = self.typify_node(node.container, ctx)
            cstr = get_contained_type(cstr_cont)
            mut = is_mutable(cstr_cont)
            return self.annotate(node, self.corpus.insert_slice_type(mut, cstr))
        elif isinstance(node, cwast.ExprAddrOf):
            cstr_expr = self.typify_node(node.expr, ctx)
            return self.annotate(node, self.corpus.insert_ptr_type(node.mut, cstr_expr))
        elif isinstance(node, cwast.ExprOffsetof):
            cstr = self.typify_node(node.type, ctx)
            return self.annotate(node, self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.UINT))
        elif isinstance(node, cwast.ExprSizeof):
            cstr = self.typify_node(node.type, ctx)
            return self.annotate(node, self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.UINT))
        elif isinstance(node, cwast.Try):
            cstr = self.typify_node(node.type, ctx)
            cstr_expr = self.typify_node(node.expr, ctx)
            cstr_complement = self.corpus.insert_sum_complement(
                cstr_expr, cstr)
            ctx.push_target(cstr_complement)
            self.typify_node(node.catch, ctx)
            ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.Catch):
            cstr = self.annotate(node, ctx.get_target_type())
            for c in node.body_except:
                self.typify_node(c, ctx)
            return cstr
        elif isinstance(node, cwast.StmtWhile):
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
            self.typify_node(node.cond, ctx)
            ctx.pop_target()
            for c in node.body:
                self.typify_node(c, ctx)
            return NO_TYPE
        else:
            assert False, f"unexpected node {node}"

    def verify_node(self, node, ctx: TypeContext):
        if isinstance(node, cwast.TYPED_ANNOTATED_NODES):
            assert id(node) in self._links, f"untypified node {node}"
        if isinstance(node, cwast.ValArray):
            cstr = self.type_link(node.type)
            for x in node.inits_array:
                if not isinstance(x, cwast.Comment):
                    assert cstr == self.type_link(
                        x), f"expected {cstr} got {self.type_link(x)}"
        elif isinstance(node, cwast.ValRec):
            for x in node.inits_rec:
                if isinstance(x, cwast.IndexVal):
                    field_node = self.field_link(x)
                    assert self.type_link(field_node) == self.type_link(x)
        elif isinstance(node, cwast.RecField):
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                type_cstr = self.type_link(node.type)
                initial_cstr = self.type_link(node.initial_or_undef)
                assert is_compatible(
                    initial_cstr, type_cstr), f"{node}: {type_cstr} {initial_cstr}"
        elif isinstance(node, cwast.ExprIndex):
            cstr = self.type_link(node)
            assert cstr == get_contained_type(self.type_link(node.container))
        elif isinstance(node, cwast.ExprField):
            cstr = self.type_link(node)
            field_node = self.field_link(node)
            assert cstr == self.type_link(field_node)
        elif isinstance(node, cwast.DefVar):
            cstr = self.type_link(node)
            if node.mut and is_array(cstr):
                assert is_mutable(cstr)
                cstr = "array" + cstr[9:]  # strip "-mut"

            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                initial_cstr = self.type_link(node.initial_or_undef)
                assert is_compatible(initial_cstr, cstr)
            if not isinstance(node.type_or_auto, cwast.Auto):
                type_cstr = self.type_link(node.type_or_auto)
                assert cstr == type_cstr, f"{node}: expected {cstr} got {type_cstr}"
        elif isinstance(node, cwast.ExprRange):
            cstr = self.type_link(node)
            if not isinstance(node.begin_or_auto, cwast.Auto):
                assert cstr == self.type_link(node.begin_or_auto)
            assert cstr == self.type_link(node.end)
            if not isinstance(node.step_or_auto, cwast.Auto):
                assert cstr == self.type_link(node.step_or_auto)
        elif isinstance(node, cwast.StmtFor):
            if not isinstance(node.type_or_auto, cwast.Auto):
                assert self.type_link(
                    node.range) == self.type_link(node.type_or_auto), f"type mismatch in FOR"
        elif isinstance(node, cwast.ExprDeref):
            cstr = self.type_link(node)
            assert cstr == get_pointee(self.type_link(node.expr))
        elif isinstance(node, cwast.Expr1):
            cstr = self.type_link(node)
            assert cstr == self.type_link(node.expr)
        elif isinstance(node, cwast.Expr2):
            cstr = self.type_link(node)
            cstr1 = self.type_link(node.expr1)
            cstr2 = self.type_link(node.expr2)
            if node.binary_expr_kind in cwast.BINOP_BOOL:
                assert cstr1 == cstr2, f"binop mismatch {cstr1} != {cstr2}"
                assert is_bool(cstr)
            elif node.binary_expr_kind in (cwast.BINARY_EXPR_KIND.PADD,
                                           cwast.BINARY_EXPR_KIND.PSUB):
                assert cstr == cstr1
                assert is_int(cstr2)
            elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.PDELTA:
                assert get_pointee(cstr1) == get_pointee(cstr2)
                assert cstr == self.corpus.insert_base_type(
                    cwast.BASE_TYPE_KIND.SINT)
            else:
                assert cstr == cstr1
                assert cstr == cstr2
        elif isinstance(node, cwast.Expr3):
            cstr = self.type_link(node)
            cstr_t = self.type_link(node.expr_t)
            cstr_f = self.type_link(node.expr_f)
            cstr_cond = self.type_link(node.cond)
            assert cstr == cstr_t
            assert cstr == cstr_f
            assert is_bool(cstr_cond)
        elif isinstance(node, cwast.ExprCall):
            result = self.type_link(node)
            fun = self.type_link(node.callee)
            assert is_fun(fun)
            params = get_children_types(fun)
            assert params.pop(-1) == result
            for p, a in zip(params, node.args):
                arg_cstr = self.type_link(a)
                assert is_compatible(
                    arg_cstr, p), f"incompatible fun arg: {a} {arg_cstr} expected={p}"
        elif isinstance(node, cwast.StmtReturn):
            fun = self.type_link(ctx.enclosing_fun)
            assert is_fun(fun)
            expected = get_children_types(fun)[-1]
            actual = self.type_link(node.expr_ret)
            assert is_compatible(
                actual, expected), f"{node}: {actual} {expected}"
        elif isinstance(node, cwast.StmtIf):
            assert is_bool(self.type_link(node.cond))
        elif isinstance(node, cwast.Case):
            assert is_bool(self.type_link(node.cond))
        elif isinstance(node, cwast.StmtWhile):
            assert is_bool(self.type_link(node.cond))
        elif isinstance(node, cwast.StmtAssignment):
            var_cstr = self.type_link(node.lhs)
            expr_cstr = self.type_link(node.expr)
            assert is_compatible(expr_cstr, var_cstr)
        elif isinstance(node, cwast.StmtCompoundAssignment):
            var_cstr = self.type_link(node.lhs)
            expr_cstr = self.type_link(node.expr)
            assert is_compatible(expr_cstr, var_cstr)
        elif isinstance(node, cwast.StmtExpr):
            cstr = self.type_link(node.expr)
            assert is_void(cstr) != node.discard
        elif isinstance(node, cwast.ExprAs):
            src = self.type_link(node.expr)
            dst = self.type_link(node.type)
            # TODO
            # assert is_compatible_for_as(src, dst)
        elif isinstance(node, cwast.ExprUnsafeCast):
            src = self.type_link(node.expr)
            dst = self.type_link(node.type)
            # TODO
            # assert is_compatible_for_as(src, dst)
        elif isinstance(node, cwast.ExprBitCast):
            src = self.type_link(node.expr)
            dst = self.type_link(node.type)
            # TODO
            # assert is_compatible_for_as(src, dst)
        elif isinstance(node, cwast.ExprIs):
            assert is_bool(self.type_link(node))
        elif isinstance(node, cwast.ExprLen):
            assert self.type_link(node) == self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT)
        elif isinstance(node, cwast.ExprChop):
            cstr = self.type_link(node)
            cstr_cont = self.type_link(node.container)
            assert get_contained_type(cstr_cont) == get_contained_type(cstr)
            assert is_mutable(cstr_cont) == is_mutable(cstr)
            if not isinstance(node.start, cwast.Auto):
                assert is_int(self.type_link(node.start))
            if not isinstance(node.width, cwast.Auto):
                assert is_int(self.type_link(node.width))
        elif isinstance(node, cwast.Id):
            cstr = self.type_link(node)
            assert cstr != NO_TYPE
        elif isinstance(node, cwast.ExprAddrOf):
            cstr_expr = self.type_link(node.expr)
            cstr = self.type_link(node)
            assert is_ptr(cstr)
            assert get_pointee(cstr) == cstr_expr
        elif isinstance(node, cwast.ExprOffsetof):
            assert self.type_link(node) == self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT)
        elif isinstance(node, cwast.ExprSizeof):
            assert self.type_link(node) == self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT)
        elif isinstance(node, cwast.Try):
            all = []
            cstr = self.type_link(node)
            if is_sum(cstr):
                all += get_children_types(cstr)
            else:
                all.append(cstr)
            cstr_complement = self.type_link(node.catch)
            if is_sum(cstr_complement):
                all += get_children_types(cstr_complement)
            else:
                all.append(cstr_complement)
            assert set(all) == set(
                get_children_types(self.type_link(node.expr)))
        elif isinstance(node, cwast.Catch):
            pass
        elif isinstance(node, (cwast.Comment, cwast.DefMod, cwast.DefFun, cwast.FunParam,
                               cwast.TypeBase, cwast.TypeArray, cwast.TypePtr, cwast.Id,
                               cwast.TypeSlice, cwast.TypeSum, cwast.Auto, cwast.ValUndef,
                               cwast.ValNum, cwast.DefType, cwast.DefRec, cwast.ValTrue,
                               cwast.ValFalse, cwast.ValVoid, cwast.DefEnum, cwast.EnumVal,
                               cwast.TypeFun, cwast.DefConst, cwast.ValString,
                               cwast.IndexVal, cwast.FieldVal, cwast.StmtBlock, cwast.StmtBreak,
                               cwast.StmtContinue, cwast.StmtDefer, cwast.StmtCond)):
            pass
        else:
            assert False, f"unsupported  node type: {node.__class__} {node}"

    def verify_node_recursively(self, node, ctx: TypeContext):
        if isinstance(node, cwast.DefFun):
            ctx.enclosing_fun = node
        self.verify_node(node, ctx)
        for c in node.__class__.FIELDS:
            nfd = cwast.ALL_FIELDS_MAP[c]
            if nfd.kind is cwast.NFK.NODE:
                self.verify_node_recursively(getattr(node, c), ctx)
            elif nfd.kind is cwast.NFK.LIST:
                for cc in getattr(node, c):
                    self.verify_node_recursively(cc, ctx)


def ExtractTypeTab(asts: List, symtab: symtab.SymTab) -> TypeTab:
    """This checks types and maps them to a cananical node

    Since array type include a fixed bound this also also includes
    the evaluation of constant expressions.
    """
    typetab = TypeTab(cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    for m in asts:
        ctx = TypeContext(symtab, m.name)
        assert isinstance(m, cwast.DefMod)
        for node in m.body_mod:
            typetab.typify_node(node, ctx)
    return typetab


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = []
    try:
        while True:
            stream = cwast.ReadTokens(sys.stdin)
            t = next(stream)
            assert t == "("
            sexpr = cwast.ReadSExpr(stream)
            # print(sexpr)
            asts.append(sexpr)
    except StopIteration:
        pass
    symtab = symtab.ExtractSymTab(asts)
    typetab = ExtractTypeTab(asts, symtab)
    for node in asts:
        typetab.verify_node_recursively(node, TypeContext(None, None))
    for t in typetab.corpus.corpus:
        print(t)
