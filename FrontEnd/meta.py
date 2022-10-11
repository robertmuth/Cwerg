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

UNRESOLVED_STRUCT_UNION_MEMBER = 6

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

    def _resolve_sym(self, node: cwast.Id) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""
        logging.info("resolving %s", node)
        name = node.name
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
        assert def_node is UNRESOLVED_STRUCT_UNION_MEMBER or isinstance(
            cwast.DefConst, cwast.DefFun, cwast.DefMod, cwast.DefType, cwast.DefVar)
        self._links[id_node] = def_node

    def resolve_symbols_recursively(self, node):
        if isinstance(node, cwast.DefVar):
            self._add_local_symbol(node)
        elif isinstance(node, cwast.Id):
            if not self._resolve_sym(node):
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


class TypeTab:
    """Type Table

    Requires SymTab info to resolve DefType symnbols
    """

    def __init__(self, uint_kind, sint_kind):
        self.uint_kind = uint_kind
        self.sint_kind = sint_kind

        self.wrapped_curr = 1
        self.corpus = {}
        self.dims: Dict[int, int] = {}
        self.links: Dict[int, CanonType] = {}

        for x in cwast.BASE_TYPE_KIND:
            if x.name in ("INVALID", "UINT", "SINT"):
                continue
            node = cwast.TypeBase(x)
            self.typify_type_node(node, None, None)

    def link(self, node) -> CanonType:
        return self.links[id(node)]

    def compute_dim(self, node) -> int:
        assert isinstance(node, cwast.ValNum), f"unexpected number: {node}"
        return int(node.number)

    def typify_type_node(self, node,  mod_name, sym_tab: SymTab) -> CanonType:
        logging.info(f"TYPIFYING {node}")
        assert isinstance(node, _NODES_RELATED_TO_TYPES), f"unexpected node {node}"
        cnode = node
        cstr = self.links.get(id(node))
        if cstr is not None:
            # has been typified already
            return cstr
        if isinstance(node, cwast.Id):
            # this case is why we need the sym_tab
            def_node = sym_tab.get_definition_for_symbol(node)
            #assert isinstance(def_node, cwast.DefType), f"unexpected node {def_node}"
            cstr = self.typify_type_node(def_node, mod_name, sym_tab)
        elif isinstance(node, cwast.TypeBase):
            kind = node.base_type_kind
            if kind == cwast.BASE_TYPE_KIND.UINT:
                kind = self.uint_kind
            elif kind == cwast.BASE_TYPE_KIND.SINT:
                kind = self.sint_kind
            cstr = kind.name.lower()
        elif isinstance(node, cwast.TypePtr):
            t = self.typify_type_node(node.type, mod_name, sym_tab)
            if node.mut:
                cstr = f"ptr-mut({t})"
            else:
                cstr = f"ptr({cstr})"
        elif isinstance(node, cwast.TypeSlice):
            t = self.typify_type_node(node.type, mod_name, sym_tab)
            cstr = f"slice({t})"
        elif isinstance(node, (cwast.FunParam, cwast.RecField)):
            cstr = self.typify_type_node(node.type, mod_name, sym_tab)
        elif isinstance(node, (cwast.TypeFun, cwast.DefFun)):
            x = [self.typify_type_node(p, mod_name, sym_tab)
                 for p in node.params if not isinstance(p, cwast.Comment)]
            res = self.typify_type_node(node.result, mod_name, sym_tab)
            x.append(res)
            if isinstance(node, cwast.DefFun):
                cnode = cwast.TypeFun(node.params, node.result)
            cstr = f"fun({','.join(x)})"
        elif isinstance(node, cwast.TypeArray):
            # note this is the only place where we need a comptime eval
            t = self.typify_type_node(node.type, mod_name, sym_tab)
            cstr = f"array({t},{self.compute_dim(node.size)})"
        elif isinstance(node, cwast.DefRec):
            for f in node.fields:
                if not isinstance(f, cwast.Comment):
                    t = self.typify_type_node(f.type, mod_name, sym_tab)
                    self.links[id(f)] = t
            cstr = f"rec({mod_name}/{node.name})"
        elif isinstance(node, cwast.DefEnum):
            base_type = cwast.TypeBase(node.base_type_kind)
            t = self.typify_type_node(base_type, mod_name, sym_tab)
            for f in node.items:
                if not isinstance(f, cwast.Comment):
                    self.links[id(f)] = t
            cstr = f"enum({mod_name}/{node.name})"
        elif isinstance(node, cwast.DefType):
            cstr = self.typify_type_node(node.type, mod_name, sym_tab)
            if node.wrapped:
                uid = self.wrapped_curr
                self.wrapped_curr += 1
                cstr = f"wrapped({uid},{cstr})"
        elif isinstance(node, cwast.TypeSum):
            pieces = []
            for c in node.types:
                t = self.typify_type_node(c, mod_name, sym_tab)
                # takes care of the case where c is an Id node
                c = self.corpus[t]
                if isinstance(c, cwast.TypeSum):
                    for cc in c.types:
                        pieces.append(cc)
                else:
                    pieces.append(c)
            pp = sorted(self.typify_type_node(p, mod_name, sym_tab) 
            for p in pieces)
            cstr = f"sum({','.join(pp)})"
            if cstr not in self.corpus:
                cnode = cwast.TypeSum(pieces)
                self.links[id(cnode)] = cstr
        else:
            assert False, f"unexpected node {node}"
        self.links[id(node)] = cstr
        if cstr not in self.corpus:
            assert isinstance(cnode, _ROOT_NODES_FOR_TYPE), f"unexpected node {cnode}"
            self.corpus[cstr] = cnode
        return cstr

    def typify_value_node(self, node,  target_type: Optional[CanonType], mod_name,
                          sym_tab: SymTab) -> CanonType:
        assert isinstance(node, _VALUE_NODES)
        cnode = node
        cstr = self.link.get(id(node))
        if cstr is not None:
            # has been typified already
            return cstr
        if isinstance(node, cwast.ValBool):
            base_type = cwast.TypeBase(cwast.BASE_TYPE_KIND.BOOL)
            cstr = self.typify_type(base_type, mod_name, sym_tab)
        elif isinstance(node, cwast.ValVoid):
            base_type = cwast.TypeBase(cwast.BASE_TYPE_KIND.VOID)
            cstr = self.typify_type(base_type, mod_name, sym_tab)
        elif isinstance(node, cwast.cwast.ValUndef):
            assert target_type is not None
            cstr = target_type
        elif isinstance(node, cwast.cwast.ValNum):
            pass
        elif isinstance(node, cwast.cwast.ValRec):
            pass
        elif isinstance(node, cwast.cwast.cwast.ValArray):
            pass

    def canonicalize_type(self, node) -> str:
        pass


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
        for node in m.children():
            if isinstance(node, _NODES_RELATED_TO_TYPES):
                 typetab.typify_type_node(node, m.name, symtab)
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
    for t in typetab.corpus:
        print(t)
