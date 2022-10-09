#!/usr/bin/python3

"""Translator from AST to Cwerg IR

"""

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
        self.type_syms = {}
        self.const_syms = {}

        self.rec_syms = {}
        self.enum_syms = {}

        self.fun_syms = {}
        self.var_syms = {}

        self.local_var_syms = []
        #
        self.links = {}

    def add_top_level_sym(self, node):
        logging.info("recording top level symbol [%s]", node.name)
        if isinstance(node, cwast.DefFun):
            assert node.name not in self.fun_syms
            self.fun_syms[node.name] = node
        elif isinstance(node, cwast.DefVar):
            assert node.name not in self.var_syms
            self.var_syms[node.name] = node
        elif isinstance(node, cwast.DefConst):
            assert node.name not in self.const_syms
            self.const_syms[node.name] = node
        elif isinstance(node, cwast.DefRec):
            assert node.name not in self.rec_syms
            self.rec_syms[node.name] = node
        elif isinstance(node, cwast.DefEnum):
            assert node.name not in self.enum_syms
            self.enum_syms[node.name] = node
        elif isinstance(node, cwast.DefType):
            assert node.name not in self.type_syms
            self.type_syms[node.name] = node
        else:
            assert False, f"unexpected node: {node}"

    def push_scope(self):
        self.local_var_syms.append({})

    def pop_scope(self):
        self.local_var_syms.pop(-1)

    def add_local_symbol(self, node):
        if isinstance(node, (cwast.DefVar, cwast.StmtFor, cwast.FunParam)):
            self.local_var_syms[-1][node.name] = node
        else:
            assert False, f"unexpected node: {node}"

    def resolve_sym(self, node: cwast.Id):
        """We could be more specific here if we narrow down the symbol type"""
        logging.info("resolving %s", node)
        name = node.name
        for l in reversed(self.local_var_syms):
            s = l.get(name)
            if s:
                self.links[id(node)] = s
                return s
        for syms in (self.type_syms, self.const_syms, self.fun_syms,
                     self.rec_syms, self.enum_syms, self.var_syms):
            s = syms.get(name)
            if s:
                self.links[id(node)] = s
                return s
        return None

    def add_link(self, id_node: cwast.Id, def_node):
        assert isinstance(id_node, (cwast.Id))
        assert def_node is UNRESOLVED_STRUCT_UNION_MEMBER or isinstance(
            cwast.DefConst, cwast.DefFun, cwast.DefMod, cwast.DefType, cwast.DefVar)
        self.links[id_node] = def_node


def ResolveSymbols(node, symtab: SymTab):

    if isinstance(node, cwast.DefVar):
        symtab.add_local_symbol(node)
    elif isinstance(node, cwast.Id):
        if not symtab.resolve_sym(node):
            logging.error(f"cannot resolve symbol {node}")
            exit(1)
    elif isinstance(node, _NODE_SCOPE):
        logging.info("push scope for %s", type(node).__name__)
        symtab.push_scope()
        if isinstance(node, cwast.StmtFor):
            symtab.add_local_symbol(node)
        elif isinstance(node, cwast.DefFun):
            for p in node.params:
                symtab.add_local_symbol(p)

    # recurse
    for c in node.children():
        ResolveSymbols(c, symtab)

    if isinstance(node, _NODE_SCOPE):
        symtab.pop_scope()
        logging.info("pop scope for %s", type(node).__name__)


def ExtractSymbolTable(asts: List) -> SymTab:
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
                    ResolveSymbols(c, symtab)
            else:
                ResolveSymbols(node, symtab)
        #
        assert not symtab.local_var_syms
    return symtab


CanonType = str


_NODES_WITH_VALUES = (
    cwast.StmtWhen,  # value(node): bool indicating if condition is true
    cwast.TypeArray,  # value(node): uint indicating dim of array
)

_NODES_WITH_CANONICAL_TYPES = (
    cwast.FunParam,  # type(node) = node.type
    cwast.RecField,  # type(node) = node.type

    cwast.StmtFor,  # type(node) = node.type
    cwast.StmtAssignment,  cwast.StmtAssignment2,
    # if necessary: type-target(node.expr) = type(node.lhs)
    #
    cwast.DefVar, cwast.DefConst,
    # if node.type == auto:
    #  type=target(node) = type(node.initial)
    # else:
    #  type=target(node) = node.type

    cwast.DefEnum,  # type(node) = enum(node.name)
    cwast.DefFun,  # type(node) = fun-sig(node)
    cwast.DefType,
    # if wrapped:
    #   type(node) = wrapped(self)
    # else:
    #   type(node) = node.type
    cwast.ValArray,  # type(node)= array(node.type, node.size)
    cwast.ValRec,    # type(node) = rec(node.name)
    #
    cwast.ExprCastAs,  # type(node) = node.type
    cwast.ExprBitCastAs,  # type(node) = node.type
    cwast.ExprOffsetof,   # type(node) = uint
    #
    cwast.StmtReturn,   # type(node) = fun-result
    #
    cwast.TypeBase,
    cwast.TypeSum,
    cwast.TypePtr,
    cwast.TypeSlice,
    cwast.TypeArray,
    cwast.TypeFun,
)


class TypeTab:
    ""

    def link(self, node) -> CanonType:
        return self.link[id(node)]

    def dim(self, node) -> int:
        return self.dims[id(node)]

    def canonicalize_type(self, mod_name, node) -> CanonType:
        if isinstance(node, cwast.TypeBase):
            kind = node.base_type_kind
            if kind == cwast.BASE_TYPE_KIND.UINT:
                kind = self.uint_kind
            elif kind == cwast.BASE_TYPE_KIND.SINT:
                kind = self.sint_kind
            c = kind.name.lower()
        elif isinstance(node, cwast.TypePtr):
            if node.mut:
                c = f"ptr-mut({self.link(node.type)})"
            else:
                c = f"ptr({self.link(node.type)})"
        elif isinstance(node, cwast.TypeSlice):
            c = f"slice({self.link(node.type)})"
        elif isinstance(node, cwast.FunParam):
            c = self.links(node.type)
        elif isinstance(node, cwast.TypeFun):
            x = [self.links[p] for p in node.params]
            x.append(self.links(node.result))
            c = f"fun({','.join(x)})"
        elif isinstance(node, cwast.TypeArray):
            c = f"slice({self.link(node.type)},{self.dim(node)})"
        elif isinstance(node, cwast.DefRec):
            c = f"rec({mod_name}/{self.name})"
        elif isinstance(node, cwast.DefEnum):
            c = f"enum({mod_name}/{self.name})"
        elif isinstance(node, cwast.DefType):
            if node.wrapped:
                c = self.links(node.type)
            else:
                uid = self.wrapped_curr
                self.wrapped_curr += 1
                c = f"wrapped({uid},{self.link(node.type)})"
        elif isinstance(node, cwast.TypeSum):
            pass

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
            self.canonicalize_type(node)

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


def Typify(node, target_type, typetab: TypeTab) -> CanonType:
    """This checks types and maps them to a cananical node

    Since array type include a fixed bound this also also includes
    the evaluation of constant expressions.
    """
    # if isinstance(node,


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
    ExtractSymbolTable(asts)
