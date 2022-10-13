#!/usr/bin/python3

"""Translator from AST to Cwerg IR

"""

from ast import mod
import dataclasses
import sys
import logging
from termios import CWERASE

from FrontEnd import cwast
from typing import List, Dict, Set, Optional, Union, Any


class Unresolved:
    def __init__(self):
        pass


UNRESOLVED_STRUCT_UNION_MEMBER = Unresolved()

MODULES = {}


_NODE_SCOPE = (cwast.StmtBlock, cwast.StmtWhile, cwast.StmtFor, cwast.StmtDefer,
               cwast.StmtIf, cwast.DefFun)


class SymTab:

    def __init__(self):
        self._type_syms = {}
        self._const_syms = {}

        self._rec_syms = {}
        self._enum_syms = {}

        self._fun_syms = {}
        self.var_syms = {}

        self._local_var_syms = []
        #
        self._links = {}

    def _push_scope(self):
        self._local_var_syms.append({})

    def _pop_scope(self):
        self._local_var_syms.pop(-1)

    def _add_local_symbol(self, node):
        if isinstance(node, (cwast.DefVar, cwast.StmtFor, cwast.FunParam)):
            self._local_var_syms[-1][node.name] = node
        else:
            assert False, f"unexpected node: {node}"

    def _resolve_enum_item(self, components) -> Optional[cwast.EnumEntry]:
        if len(components) != 2:
            return None
        node = self._enum_syms.get(components[0])
        assert isinstance(node, cwast.DefEnum)
        for item in node.children():
            if isinstance(item, cwast.EnumEntry) and item.name == components[1]:
                return item
        return None

    def _resolve_rec_field(self, components) -> Optional[cwast.RecField]:
        if len(components) != 2:
            return None
        node = self._enum_syms.get(components[0])
        assert isinstance(node, cwast.DefRec)
        for item in node.children():
            if isinstance(item, cwast.RecField) and item.name == components[1]:
                return item
        return None

    def resolve_sym(self, node: cwast.Id) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""
        logging.info("resolving %s", node)
        name = node.name
        components = name.split("/")
        if len(components) > 1:
            s = self._resolve_enum_item(components)
            if s:
                return s
            assert False

        for l in reversed(self._local_var_syms):
            s = l.get(name)
            if s:
                self._links[id(node)] = s
                return s
        for syms in (self._type_syms, self._const_syms, self._fun_syms,
                     self._rec_syms, self._enum_syms, self.var_syms):
            s = syms.get(name)
            if s:
                self._links[id(node)] = s
                return s
        return None

    def _add_link(self, id_node: cwast.Id, def_node):
        assert isinstance(id_node, (cwast.Id))
        assert isinstance(def_node,
                          (Unresolved, cwast.DefConst, cwast.DefFun, cwast.DefMod, cwast.DefType,
                           cwast.DefVar, cwast.EnumEntry, cwast.DefRec, cwast.DefEnum,
                           cwast.FunParam, cwast.StmtFor)), f"unpexpected node: {def_node}"
        self._links[id(id_node)] = def_node

    def resolve_symbols_recursively(self, node):
        logging.info("UNSYMBOLIZE %s", type(node).__name__)
        if isinstance(node, cwast.DefVar):
            self._add_local_symbol(node)
        elif isinstance(node, cwast.Id):
            def_node = self.resolve_sym(node)
            if def_node:
                self._add_link(node, def_node)
                return
            else:
                logging.error(f"cannot resolve symbol {node}")
                exit(1)
        elif isinstance(node, _NODE_SCOPE):
            logging.info("push scope for %s", type(node).__name__)
            self._push_scope()
            if isinstance(node, cwast.StmtFor):
                self._add_local_symbol(node)
            elif isinstance(node, cwast.DefFun):
                for p in node.params:
                    self._add_local_symbol(p)

        # recurse
        for c in node.children():
            self.resolve_symbols_recursively(c)

        if isinstance(node, _NODE_SCOPE):
            self._pop_scope()
            logging.info("pop scope for %s", type(node).__name__)

    def add_top_level_sym(self, node):
        logging.info("recording top level symbol [%s]", node.name)
        if isinstance(node, cwast.DefFun):
            assert node.name not in self._fun_syms
            self._fun_syms[node.name] = node
        elif isinstance(node, cwast.DefVar):
            assert node.name not in self.var_syms
            self.var_syms[node.name] = node
        elif isinstance(node, cwast.DefConst):
            assert node.name not in self._const_syms
            self._const_syms[node.name] = node
        elif isinstance(node, cwast.DefRec):
            assert node.name not in self._rec_syms
            self._rec_syms[node.name] = node
        elif isinstance(node, cwast.DefEnum):
            assert node.name not in self._enum_syms
            self._enum_syms[node.name] = node
        elif isinstance(node, cwast.DefType):
            assert node.name not in self._type_syms
            self._type_syms[node.name] = node
        else:
            assert False, f"unexpected node: {node}"

    def get_definition_for_symbol(self, node: cwast.Id):
        return self._links[id(node)]


def ExtractSymTab(asts: List) -> SymTab:
    global MODULES
    symtab = SymTab()
    for mod in asts:
        assert isinstance(mod, cwast.DefMod), mod
        logging.info("Processing %s", mod.name)
        MODULES[mod.name] = mod
        # pass 1: get all the top level symbols
        for node in mod.children():
            if isinstance(node, cwast.Comment):
                pass
            else:
                symtab.add_top_level_sym(node)

        # pass 2:
        for node in mod.children():
            if isinstance(node, cwast.Comment):
                continue
            logging.info("ExtractSymbolTable %s", node.name)
            if isinstance(node, cwast.DefVar):
                # we already registered the var in the previous step
                for c in node.children():
                    symtab.resolve_symbols_recursively(c)
            else:
                symtab.resolve_symbols_recursively(node)
        #
        assert not symtab._local_var_syms
    return symtab


CanonType = str
NO_TYPE = "typeless"

_NODES_WITH_VALUES = (
    # cwast.StmtWhen,  # value(node): bool indicating if condition is true
    cwast.TypeArray,  # value(node): uint indicating dim of array
)

_ROOT_NODES_FOR_TYPE = (
    cwast.DefEnum,
    cwast.DefRec,
    cwast.TypeArray,
    cwast.TypeSlice,
    cwast.TypeBase,
    cwast.TypeSum,
    cwast.TypePtr,
    cwast.TypeFun,
    cwast.DefType,  # must be wrapped=true
)

_NODES_RELATED_TO_TYPES = _ROOT_NODES_FOR_TYPE + (
    cwast.Id,
    cwast.FunParam,  # type(node) = node.type
    cwast.RecField,  # type(node) = node.type
    cwast.EnumEntry,  # type(node) = base-type(enum)
    cwast.DefFun,     # odd-ball (but better here than in values)
    # cwast.DefType,
    # if wrapped:
    #   type(node) = wrapped(self)
    # else:    #   type(node) = node.type
)


_VALUE_NODES = (
    cwast.ValBool,   # type(node) = bool
    cwast.ValVoid,   # type(node) = void
    cwast.ValUndef,  # type(node) = undef(target_kind)

    cwast.ValNum,    # type(node) = target_kind OR kind(node.value)
    cwast.ValRec,    # type(node) = rec(node.name)
    cwast.ValArray,  # type(node) = array(node.type, node.size)
    cwast.ValRec,    # type(node) = rec(node.name)
)

_TYPED_NODES = (
    cwast.StmtFor,  # type(node) = node.type
    cwast.StmtAssignment,  cwast.StmtAssignment2,
    # if necessary: type-target(node.expr) = type(node.lhs)
    #
    cwast.DefVar, cwast.DefConst,
    # if node.type == auto:
    #  type=target(node) = type(node.initial)
    # else:
    #  type=target(node) = node.type

    #
    cwast.ExprCastAs,  # type(node) = node.type
    cwast.ExprBitCastAs,  # type(node) = node.type
    cwast.ExprOffsetof,   # type(node) = uint
    #
    cwast.StmtReturn,   # type(node) = fun-result

)


class TypeContext:
    def __init__(self, symtab, mod_name):
        self.symtab: SymTab = symtab
        self.mod_name: str = mod_name
        self.enclosing_fun: Optional[cwast.DefFun] = None
        self.target_type: CanonType = NO_TYPE


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

    def insert(self, name, node):
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
            self.insert(name, cwast.TypeBase(kind))
        return name

    def insert_ptr_type(self, mut: bool, cstr: CanonType) -> CanonType:
        if mut:
            name = f"ptr-mut({cstr})"
        else:
            name = f"ptr({cstr})"
        if name not in self.corpus:
            self.insert(name, cwast.TypePtr(mut, self.corpus[cstr]))
        return name

    def insert_slice_type(self, mut: bool, cstr: CanonType) -> CanonType:
        if mut:
            name = f"slice-mut({cstr})"
        else:
            name = f"slice({cstr})"
        if name not in self.corpus:
            self.insert(name, cwast.TypeSlice(mut, self.corpus[cstr]))
        return name

    def insert_array_type(self, size: int, cstr: CanonType) -> CanonType:
        name = f"array({cstr},{size})"
        if name not in self.corpus:
            self.insert(name, cwast.TypeArray(size, self.corpus[cstr]))
        return name

    def insert_rec_type(self, name: str, node) -> CanonType:
        assert isinstance(node, cwast.DefRec)
        name = f"rec({name})"
        if name not in self.corpus:
            self.insert(name, node)
        return name

    def insert_enum_type(self, name: str, node) -> CanonType:
        assert isinstance(node, cwast.DefEnum)
        name = f"enum({name})"
        if name not in self.corpus:
            self.insert(name, node)
        return name

    def insert_sum_type(self, components: List[CanonType]) -> CanonType:
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
            self.insert(name, cwast.TypeSum(pieces))
        return name

    def insert_fun_type(self, params: List[CanonType], result: CanonType) -> CanonType:
        name = f"fun({','.join(params +[result])})"
        if name not in self.corpus:
            p = [cwast.FunParam("", self.corpus[x]) for x in params]
            self.insert(name, cwast.TypeFun(p, self.corpus[result]))
        return name

    def insert_wrapped_type(self, cstr: CanonType, node) -> CanonType:
        assert isinstance(node, cwast.DefType)
        uid = self.wrapped_curr
        self.wrapped_curr += 1
        name = f"wrapped({uid},{cstr})"
        assert name not in self.corpus
        self.insert(name, node)
        return name


class TypeTab:
    """Type Table

    Requires SymTab info to resolve DefType symnbols
    """

    def __init__(self, uint_kind, sint_kind):
        self.wrapped_curr = 1
        self.corpus = TypeCorpus(uint_kind, sint_kind)
        self.dims: Dict[int, int] = {}
        self.links: Dict[int, CanonType] = {}

    def link(self, node) -> CanonType:
        return self.links[id(node)]

    def compute_dim(self, node) -> int:
        assert isinstance(node, cwast.ValNum), f"unexpected number: {node}"
        return int(node.number)

    def annotate(self, node, cstr: CanonType):
        assert cstr
        assert id(node) not in self.links
        self.links[id(node)] = cstr
        return cstr

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

    def typify_node(self, node,  ctx: TypeContext) -> CanonType:
        extra = "" if ctx.target_type == NO_TYPE else f"[{ctx.target_type}]" 
        logging.info(f"TYPIFYING{extra} {node}")
        cstr = self.links.get(id(node))
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
        elif isinstance(node, (cwast.FunParam, cwast.RecField)):
            cstr = self.typify_node(node.type, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, (cwast.TypeFun, cwast.DefFun)):
            params = [self.typify_node(p, ctx)
                      for p in node.params if not isinstance(p, cwast.Comment)]
            result = self.typify_node(node.result, ctx)
            return self.annotate(node, self.corpus.insert_fun_type(params, result))
        elif isinstance(node, cwast.TypeArray):
            # note this is the only place where we need a comptime eval
            t = self.typify_node(node.type, ctx)
            dim = self.compute_dim(node.size)
            return self.annotate(node, self.corpus.insert_array_type(dim, t))
        elif isinstance(node, cwast.RecField):
            t = self.typify_node(f.type, ctx)
            return self.annotate(node, t)
        elif isinstance(node, cwast.DefRec):
            for f in node.fields:
                self.typify_node(f, ctx)
            cstr = self.corpus.insert_rec_type(node.name, node)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.EnumEntry):
            cstr = self.typify_node(node.value, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.DefEnum):
            base_type = self.corpus.insert_base_type(node.base_type_kind)
            saved_target_type = ctx.target_type
            ctx.target_type = base_type
            for f in node.items:
                self.typify_node(f, ctx)
            ctx.target_type = saved_target_type
            return self.annotate(node, self.corpus.insert_enum_type(
                f"{ctx.mod_name}/{node.name}", node))
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
        if isinstance(node, cwast.ValBool):
            return self.annotate(node, self.corpus.insert_base_type(
                cwast.TypeBase(cwast.BASE_TYPE_KIND.BOOL)))
        elif isinstance(node, cwast.ValVoid):
            return self.annotate(node, self.corpus.insert_base_type(
                cwast.TypeBase(cwast.BASE_TYPE_KIND.VOID)))
        elif isinstance(node, cwast.ValUndef):
            return self.annotate(node, ctx.target_type)
        elif isinstance(node, cwast.ValNum):
            cstr = self.num_type(node.number)
            if cstr != NO_TYPE:
                return self.annotate(node, cstr)
            return self.annotate(node, ctx.target_type)
        elif isinstance(node, cwast.Auto):
            return self.annotate(node, ctx.target_type)
        elif isinstance(node, cwast.DefConst):
            saved_target_type = ctx.target_type
            if not isinstance(node.type, cwast.TypeAuto):
                ctx.target_type = self.typify_node(node.type, ctx)
            cstr = self.typify_node(node.value, ctx)
            ctx.target_type = saved_target_type
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.ValArray):
            saved_target_type = ctx.target_type
            ctx.target_type = self.typify_node(node.type, ctx)
            for x in node.values:
                self.typify_node(x, ctx)
            cstr = self.typify_node(node.value, ctx)
            ctx.target_type = saved_target_type
            return self.annotate(node, cstr)
        else:
            assert False, f"unexpected node {node}"

    def canonicalize_type(self, node) -> str:
        pass


CanonConst = Any


class ConstTab:
    """Type Table

    Requires SymTab info to resolve DefType symnbols
    """

    def __init__(self):
        self.links = {}

    def link(self, node) -> CanonConst:
        return self.links[id(node)]

    def constify_value_node(self, node,  target_type: Optional[CanonType], mod_name,
                            sym_tab: SymTab) -> CanonType:
        logging.info(f"CONSTFYING {node}")
        assert isinstance(node, _VALUE_NODES), f"unexpected node {node}"
        if isinstance(node, cwast.Id):
            pass
            # this case is why we need the sym_tab
            def_node = sym_tab.get_definition_for_symbol(node)
            # assert isinstance(def_node, cwast.DefType), f"unexpected node {def_node}"
            cstr = self.typify_type_node(def_node, mod_name, sym_tab)
        elif isinstance(node, (cwast.ValBool, cwast.ValUndef, cwast.ValVoid)):
            self.links[id(node)] = node
        elif isinstance(node, cwast.ValNum):
            self.links[id(node)] = node


_TYPED_NODES = (
    #
    cwast.ValBool, cwast.ValNum,
    cwast.ValUndef, cwast.ValVoid, cwast.FieldVal, cwast.ValArray,
    cwast.ValArrayString, cwast.ValRec,
    #
    cwast.Id, cwast. ExprAddrOf, cwast.ExprDeref, cwast.ExprIndex,
    cwast.ExprField, cwast.ExprCall, cwast.ExprParen,
    cwast.Expr1, cwast.Expr2, cwast.Expr3,
    cwast.ExprUnwrap, cwast.ExprChop,
    cwast.ExprLen, cwast.ExprSizeof)


def ExtractTypeTab(asts: List, symtab: SymTab) -> TypeTab:
    """This checks types and maps them to a cananical node

    Since array type include a fixed bound this also also includes
    the evaluation of constant expressions.
    """
    typetab = TypeTab(cwast.BASE_TYPE_KIND.U32, cwast.BASE_TYPE_KIND.S32)
    for m in asts:
        ctx = TypeContext(symtab, m.name)
        for node in m.children():
            if isinstance(node, _NODES_RELATED_TO_TYPES):
                typetab.typify_node(node, ctx)
    return typetab


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
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
    symtab = ExtractSymTab(asts)
    typetab = ExtractTypeTab(asts, symtab)
    for t in typetab.corpus.corpus:
        print(t)
