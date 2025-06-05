#!/bin/env python3
"""Concrete Syntax Pretty printer (PP) for Cwerg AST to concrete syntax

"""

import logging

from typing import Any, Callable

from FE import cwast
from FE import checker
from Util import pretty as PP


logger = logging.getLogger(__name__)


_OPS_PRECENDENCE = {
    # "->": 10,
    cwast.ExprField: 10,
    cwast.ExprAs: 10,
    #
    cwast.Expr1: 11,
    cwast.ExprDeref: 11,
    cwast.ExprAddrOf: 11,

    cwast.ExprIs: 50,
}

_DEREFERENCE_OP = "^"
_ADDRESS_OF_OP = "@"

PREC2_ORSC = 5
PREC2_ANDSC = 6
PREC2_COMPARISON = 7
PREC2_MAX = 9  # max min
PREC2_ADD = 10  # + - or xor
PREC2_MUL = 11  # * / % and
PREC2_SHIFT = 12
PREC1_NOT = 13
PREC_INDEX = 14  # &a[i] &struct^.field
# PREC_DEREF = 15


_OPS_PRECENDENCE_EXPR2 = {
    cwast.BINARY_EXPR_KIND.SHL: PREC2_SHIFT,
    cwast.BINARY_EXPR_KIND.ROTL: PREC2_SHIFT,
    cwast.BINARY_EXPR_KIND.SHR: PREC2_SHIFT,
    cwast.BINARY_EXPR_KIND.ROTR: PREC2_SHIFT,
    #
    cwast.BINARY_EXPR_KIND.MUL: PREC2_MUL,
    cwast.BINARY_EXPR_KIND.DIV: PREC2_MUL,
    cwast.BINARY_EXPR_KIND.MOD: PREC2_MUL,
    cwast.BINARY_EXPR_KIND.AND: PREC2_MUL,
    #
    cwast.BINARY_EXPR_KIND.ADD: PREC2_ADD,
    cwast.BINARY_EXPR_KIND.SUB: PREC2_ADD,
    cwast.BINARY_EXPR_KIND.XOR: PREC2_ADD,
    cwast.BINARY_EXPR_KIND.OR: PREC2_ADD,
    #
    cwast.BINARY_EXPR_KIND.MAX: PREC2_MAX,
    cwast.BINARY_EXPR_KIND.MIN: PREC2_MAX,
    #
    cwast.BINARY_EXPR_KIND.GE: PREC2_COMPARISON,
    cwast.BINARY_EXPR_KIND.GT: PREC2_COMPARISON,
    cwast.BINARY_EXPR_KIND.LE: PREC2_COMPARISON,
    cwast.BINARY_EXPR_KIND.LT: PREC2_COMPARISON,
    cwast.BINARY_EXPR_KIND.EQ: PREC2_COMPARISON,
    cwast.BINARY_EXPR_KIND.NE: PREC2_COMPARISON,
    #
    cwast.BINARY_EXPR_KIND.ANDSC: PREC2_ANDSC,
    cwast.BINARY_EXPR_KIND.ORSC: PREC2_ORSC,
}


def _prec2(node: cwast.Expr2):
    return _OPS_PRECENDENCE_EXPR2[node.binary_expr_kind]


_FUNCTIONAL_BINOPS = (cwast.BINARY_EXPR_KIND.MAX,
                      cwast.BINARY_EXPR_KIND.MIN,
                      cwast.BINARY_EXPR_KIND.PDELTA)
_FUNCTIONAL_UNOPS = (cwast.UNARY_EXPR_KIND.ABS, cwast.UNARY_EXPR_KIND.SQRT)


def NodeNeedsParen(node, parent):
    """Do we need to add parenthesese around an expression
    so that the (naive) concrete syntax emitter does not
    produce invalid code.
    """
    if isinstance(parent, cwast.Expr2):
        if parent.binary_expr_kind in _FUNCTIONAL_BINOPS:
            return False
        if node is parent.expr1:
            if isinstance(node, cwast.Expr2):
                # parent: (expr2 node ...)
                # BAD EXAMPLES:
                # (* (+ a b ) c) =>  a + b * c
                return _prec2(node) < _prec2(parent) and node.binary_expr_kind not in _FUNCTIONAL_BINOPS
        if node is parent.expr2:
            if isinstance(node, cwast.Expr2):
                # parent: (expr2 ... node)
                # BAD EXAMPLES:
                # (* c (+ a b)) =>  c * a + b
                # (/ c (/ a b)) =>  c / a / b
                return _prec2(node) <= _prec2(parent) and node.binary_expr_kind not in _FUNCTIONAL_BINOPS
    elif isinstance(parent, cwast.Expr1):
        if parent.unary_expr_kind in _FUNCTIONAL_UNOPS:
            return False
        # BAD EXAMPLES:
        # (! (< a b)) => ! a < b
        return isinstance(node, cwast.Expr2) and node.binary_expr_kind not in _FUNCTIONAL_BINOPS

    return False


def AddMissingParens(node):
    """Add Missing Parenthesis to help with translation to concrete syntax. """
    def replacer(node, parent):
        if NodeNeedsParen(node, parent):
            return cwast.ExprParen(node, x_srcloc=node.x_srcloc, x_type=node.x_type)

        return None

    cwast.MaybeReplaceAstRecursivelyWithParentPost(node, replacer)


PP_BEG_STD = PP.Beg(PP.BreakType.INCONSISTENT, 2)
PP_BEG_NEST = PP.Beg(PP.BreakType.FORCE_LINE_BREAK, 4)


def _EmitExpr3(out, node: cwast.Expr3):
    _EmitExprOrType(out, node.cond)
    out += [PP.NoBreak(1), PP.Str("?"), PP.Brk()]
    _EmitExprOrType(out, node.expr_t)
    out += [PP.Brk(), PP.Str(":"), PP.Brk()]
    _EmitExprOrType(out, node.expr_f)


def EmitExprStmt(out, node: cwast.ExprStmt):
    out += [PP.Str("expr"), PP.Brk(0), PP.Str(":")]
    _EmitStatementsSpecial(out, node.body)


def _EmitTypeFun(out, node: cwast.TypeFun):
    out += [PP.Beg(PP.BreakType.CONSISTENT, 2),
            PP.Str("funtype"), PP.NoBreak(0)]
    _EmitParameterList(out, node.params)
    out += [PP.Brk()]
    _EmitExprOrType(out, node.result)
    out += [PP.End()]


def _GetDoc(node):
    for nfd in node.ATTRS:
        if nfd.name == "doc":
            return getattr(node, "doc")
    return None


def _MaybeEmitDoc(out, node):
    doc = _GetDoc(node)
    if doc:
        if doc.startswith('"""'):
            doc = doc[3:-3]
        else:
            doc = doc[1:-1]
        for line in doc.split("\n"):
            if not line:
                out += [PP.Str(";"), PP.LineBreak()]
            else:
                out += [PP.Str("; " + line), PP.LineBreak()]


def _MaybeEmitAnnotations(out, node):
    for nfd in node.ATTRS:
        if nfd.kind is not cwast.NFK.ATTR_BOOL:
            continue
        field = nfd.name
        if field in ("untagged", "mut", "unchecked"):
            # these are handled by the ! suffix
            continue
        val = getattr(node, field)
        if not val:
            continue
        if field not in ("pub", "wrapped", "ref", "poly"):
            field = "{{" + field + "}}"
        out += [PP.Str(field), PP.Brk()]


def WithExcl(name: str, mutable: bool) -> str:
    return name + "!" if mutable else name


def KW(node) -> str:
    return node.ALIAS


def _EmitArg(out, param, first):
    if first:
        if _GetDoc(param):
            out += [PP.Brk(0)]
        else:
            out += [PP.NoBreak(0)]
    else:
        out += [PP.NoBreak(0), PP.Str(","), PP.Brk()]
    _MaybeEmitDoc(out, param)
    out += [PP_BEG_STD]
    _EmitExprOrType(out, param)
    out += [PP.End()]


def _EmitParenList(out, lst):
    out += [PP.Str("(")]
    first = True
    for param in lst:
        _EmitArg(out, param, first)
        first = False

    out += [PP.NoBreak(0), PP.Str(")")]


def _EmitFunctional(out, node, name, nodes: list):
    out += [PP_BEG_STD]
    _MaybeEmitAnnotations(out, node)
    out += [PP.Str(name)]
    out += [PP.NoBreak(0)]
    _EmitParenList(out, nodes)
    out += [PP.End()]


def _EmitFunctionalKW(out, node, nodes: list, add_excl=False):
    _EmitFunctional(out, node, WithExcl(KW(node), add_excl), nodes)


def _EmitCall(out, name, nodes: list):
    out += [PP_BEG_STD]
    _EmitExprOrType(out, name)
    out += [PP.NoBreak(0)]
    _EmitParenList(out, nodes)
    out += [PP.End()]


def _MaybeAddCommaAndHandleComment(out, first, node, first_break):
    doc = _GetDoc(node)
    if not first:
        out += [PP.NoBreak(0), PP.Str(",")]
    if doc:
        out += [PP.LineBreak()]
        _MaybeEmitDoc(out, node)
    else:
        if first:
            out += [first_break]
        else:
            out += [PP.Brk()]


def _EmitParameterList(out, lst):
    out += [PP.Beg(PP.BreakType.INCONSISTENT, 1), PP.Str("(")]
    first = True
    for param in lst:
        _MaybeAddCommaAndHandleComment(out, first, param, PP.NoBreak(0))
        first = False
        #
        out += [PP.Beg(PP.BreakType.INCONSISTENT, 2)]
        _MaybeEmitAnnotations(out, param)
        out += [PP.Str(str(param.name)), PP.Brk()]
        if isinstance(param, cwast.FunParam):
            _EmitExprOrType(out, param.type)
        elif isinstance(param, cwast.ModParam):
            out += [PP.Str(param.mod_param_kind.name)]
        elif isinstance(param, cwast.MacroParam):
            out += [PP.Str(param.macro_param_kind.name)]
        else:
            assert False
        out += [PP.End()]
    out += [PP.Brk(0), PP.Str(")"), PP.End()]


def _EmitUnary(out, a, b):
    if isinstance(a, str):
        out += [PP.Str(a)]
    else:
        _EmitExprOrType(out, a)

    out += [PP.Brk(0)]
    if isinstance(b, str):
        out += [PP.Str(b)]
    else:
        _EmitExprOrType(out, b)


def _EmitExpr1(out, node: cwast.Expr1):
    kind = node.unary_expr_kind
    sym = cwast.UNARY_EXPR_SHORTCUT_CONCRETE_INV[kind]
    if kind in _FUNCTIONAL_UNOPS:
        _EmitFunctional(out, node, sym, [node.expr])
    else:
        _EmitUnary(out, sym, node.expr)


def _EmitBinary(out, node, expr1, width1: int, op: str, width2: int, expr2):
    _EmitExprOrType(out, expr1)
    # we do not want a break here
    out += [PP.NoBreak(width1)]
    _MaybeEmitAnnotations(out, node)
    out += [PP.Str(op), PP.Brk(width2)]
    _EmitExprOrType(out, expr2)


def _EmitExpr2(out, node: cwast.Expr2):
    kind = node.binary_expr_kind
    sym = cwast.BINARY_EXPR_SHORTCUT_INV[kind]
    if kind in _FUNCTIONAL_BINOPS:
        _EmitFunctional(out, node, sym, [node.expr1, node.expr2])
    else:
        _EmitBinary(out, node, node.expr1, 1, sym, 1, node.expr2)


def _EmitExprIndex(out, node: cwast.ExprIndex):
    out += [PP_BEG_STD]
    _EmitExprOrType(out, node.container)
    out += [PP.NoBreak(0), PP.Str(WithExcl("[", node.unchecked)), PP.Brk(0)]
    _EmitExprOrType(out, node.expr_index)
    out += [PP.Brk(0), PP.Str("]"), PP.End()]


def _EmitVecType(out, size, type):
    out += [PP_BEG_STD, PP.Str("["), PP.Brk(0)]
    _EmitExprOrType(out, size)
    out += [PP.Brk(0), PP.Str("]")]
    _EmitExprOrType(out, type)
    out += [PP.End()]


def _EmitParenGrouping(out, node: cwast.ExprParen):
    out += [PP_BEG_STD, PP.Str("("), PP.Brk(0)]
    _EmitExprOrType(out, node.expr)
    out += [PP.Brk(0), PP.Str(")"), PP.End()]


def _IsComplexValCompound(node: cwast.ValCompound) -> bool:
    if len(node.inits) > 10:
        return True
    if node.inits and isinstance(node.inits[0].value_or_undef,
                                 cwast.ValCompound):

        return True
    return False


def _EmitValCompound(out, node: cwast.ValCompound):
    out += [PP.Beg(PP.BreakType.INCONSISTENT, 1),
            PP.Str("{"), PP.NoBreak(0)]
    if not isinstance(node.type_or_auto, cwast.TypeAuto):
        _EmitExprOrType(out, node.type_or_auto)
        out += [PP.NoBreak(0)]
    out += [PP.Str(":")]
    first = True
    first_break = PP.NoBreak(1)
    if _IsComplexValCompound(node):
        first_break = PP.LineBreak()
    for e in node.inits:
        _MaybeAddCommaAndHandleComment(out, first, e, first_break)
        first = False
        out += [PP_BEG_STD]
        _MaybeEmitAnnotations(out, e)
        assert isinstance(e, cwast.ValPoint)
        if not isinstance(e.point_or_undef, cwast.ValUndef):
            _EmitExprOrType(out, e.point_or_undef)
            out += [PP.NoBreak(1), PP.Str("="), PP.Brk()]
        _EmitExprOrType(out, e.value_or_undef)
        out += [PP.End()]
    out += [PP.Brk(0), PP.Str("}"), PP.End()]


_EMITTER_TAB: dict[Any, Callable[[Any, Any], None]] = {
    cwast.Id: lambda out, n:  out.extend([PP.Str(n.FullName())]),
    cwast.MacroId: lambda out, n: out.extend([PP.Str(str(n.name))]),
    #
    cwast.ValTrue: lambda out, n: out.append(PP.Str(KW(n))),
    cwast.ValFalse: lambda out, n: out.append(PP.Str(KW(n))),
    cwast.ValUndef: lambda out, n: out.append(PP.Str(KW(n))),
    cwast.ValVoid: lambda out, n: out.append(PP.Str(KW(n))),
    cwast.ValAuto: lambda out, n: out.append(PP.Str(KW(n))),
    cwast.TypeAuto: lambda out, n: out.append(PP.Str(KW(n))),
    #
    cwast.ValNum: lambda out, n: out.append(PP.Str(n.number)),
    cwast.TypeBase: lambda out, n: out.append(
        PP.Str(cwast.BaseTypeKindToKeyword(n.base_type_kind))),
    #
    cwast.ExprLen: lambda out, n: _EmitFunctionalKW(out, n, [n.container]),
    #
    cwast.ExprOffsetof: lambda out, n: _EmitFunctionalKW(out, n, [n.type, n.field]),
    cwast.TypeUnionDelta: lambda out, n: _EmitFunctionalKW(out, n, [n.type, n.subtrahend]),
    cwast.ValSpan: lambda out, n: _EmitFunctionalKW(out, n, [n.pointer, n.expr_size]),
    #
    cwast.ExprAs: lambda out, n: _EmitFunctionalKW(out, n, [n.expr, n.type]),
    cwast.ExprIs: lambda out, n: _EmitFunctionalKW(out, n, [n.expr, n.type]),
    cwast.ExprWiden: lambda out, n: _EmitFunctionalKW(out, n, [n.expr, n.type]),
    cwast.ExprWrap: lambda out, n: _EmitFunctionalKW(out, n, [n.expr, n.type]),
    cwast.ExprBitCast: lambda out, n: _EmitFunctionalKW(out, n, [n.expr, n.type]),
    #
    cwast.ExprSizeof: lambda out, n: _EmitFunctionalKW(out, n, [n.type]),
    cwast.ExprTypeId: lambda out, n: _EmitFunctionalKW(out, n, [n.type]),
    #
    cwast.ExprUnionTag: lambda out, n: _EmitFunctionalKW(out, n, [n.expr]),
    cwast.ExprUnwrap: lambda out, n: _EmitFunctionalKW(out, n, [n.expr]),
    cwast.ExprStringify: lambda out, n: _EmitFunctionalKW(out, n, [n.expr]),
    cwast.ExprSrcLoc: lambda out, n: _EmitFunctionalKW(out, n, [n.expr]),
    cwast.TypeOf: lambda out, n: _EmitFunctionalKW(out, n, [n.expr]),
    #
    cwast.TypeUnion: lambda out, n: _EmitFunctionalKW(out, n, n.types, n.untagged),
    cwast.TypeSpan: lambda out, n: _EmitFunctionalKW(out, n, [n.type], n.mut),
    cwast.ExprFront: lambda out, n: _EmitFunctionalKW(out, n, [n.container], n.mut),
    cwast.ExprNarrow: lambda out, n: _EmitFunctionalKW(out, n, [n.expr, n.type], n.unchecked),
    #
    cwast.ExprPointer: lambda out, n: _EmitFunctional(
        out, n, cwast.POINTER_EXPR_SHORTCUT_INV[n.pointer_expr_kind],
        [n.expr1, n.expr2] if isinstance(n.expr_bound_or_undef, cwast.ValUndef) else
        [n.expr1, n.expr2, n.expr_bound_or_undef]),
    #
    cwast.MacroInvoke: lambda out, n: _EmitFunctional(out, n, n.name.name, n.args),

    #
    cwast.ExprCall: lambda out, n: _EmitCall(out, n.callee, n.args),
    #

    #
    cwast.Expr1: _EmitExpr1,
    cwast.Expr2: _EmitExpr2,
    cwast.Expr3: _EmitExpr3,
    #
    cwast.ExprDeref: lambda out, n: _EmitUnary(out, n.expr, "^"),
    cwast.ExprAddrOf: lambda out, n: _EmitUnary(out, WithExcl(_ADDRESS_OF_OP, n.mut), n.expr_lhs),
    cwast.TypePtr: lambda out, n: _EmitUnary(out, WithExcl("^", n.mut), n.type),
    #
    cwast.ExprField: lambda out, n: _EmitBinary(
        out, n, n.container, 0, ".", 0, n.field),
    cwast.ExprIndex: _EmitExprIndex,
    cwast.TypeVec: lambda out, n: _EmitVecType(out, n.size, n.type),
    cwast.TypeFun:  _EmitTypeFun,
    cwast.ExprParen: lambda out, n: _EmitParenGrouping(out, n),
    cwast.ValCompound: _EmitValCompound,
    cwast.ExprStmt: EmitExprStmt,
    #
    cwast.ValString: lambda out, n:  out.extend([PP.Str(n.render())]),
}


def _EmitExprOrType(out, node):
    emitter = _EMITTER_TAB.get(node.__class__)
    assert emitter, f"unsupported {node}"
    emitter(out, node)


def _EmitStmtSet(out, kind, lhs, rhs):
    out += [PP.Str("set"), PP.Brk()]
    _EmitExprOrType(out, lhs)
    out += [PP.Brk(), PP.Str(kind),
            PP.Brk()]
    _EmitExprOrType(out, rhs)


def _EmitStmtLetOrGlobal(out, kind: str, name: str, type_or_auto, init_or_auto):
    out += [PP.Str(kind), PP.NoBreak(1),
            PP.Str(str(name))]
    if not isinstance(type_or_auto, cwast.TypeAuto):
        out += [PP.NoBreak(1)]
        _EmitExprOrType(out, type_or_auto)
    if not isinstance(init_or_auto, cwast.ValAuto):
        out += [PP.NoBreak(1), PP.Str("="), PP.NoBreak(1)]
        _EmitExprOrType(out, init_or_auto)


def _IsColonEmphemeral(node) -> bool:
    return isinstance(node, cwast.EphemeralList) and node.colon


def _IsMacroWithBlock(node: cwast.MacroInvoke) -> bool:
    if node.args:
        last = node.args[-1]
        if _IsColonEmphemeral(last):
            return True
    return False


def _EmitIdList(out, lst):
    out += [PP.Beg(PP.BreakType.CONSISTENT, 2), PP.Str("[")]
    first = True
    for gen_id in lst:
        if first:
            out += [PP.Brk(0)]
        else:
            out += [PP.NoBreak(0), PP.Str(","), PP.Brk()]
        first = False
        assert isinstance(gen_id, cwast.MacroId)
        out += [PP.Str(gen_id.name.name)]
    out += [PP.Brk(0), PP.Str("]"), PP.End()]


def _EmitStmtMacroInvoke(out, node: cwast.MacroInvoke):
    """Handle  Macro Invocation in Stmt Context"""
    name = node.name.name
    out += [PP.Str(str(name))]
    is_block_like = name in cwast.BUILT_IN_STMT_MACROS or _IsMacroWithBlock(
        node)
    if not is_block_like:
        out += [PP.NoBreak(0),
                PP.Beg(PP.BreakType.INCONSISTENT, 1),
                PP.Str("(")]
    args = node.args
    if name == "for" or name == "tryset":
        out += [PP.Brk()]
        _EmitExprOrType(out, args[0])
        out += [PP.Brk(), PP.Str("=")]
        args = args[1:]
    elif name == "trylet" or name == "trylet!":
        out += [PP.Brk()]
        _EmitExprOrType(out, args[0])
        out += [PP.Brk()]
        _EmitExprOrType(out, args[1])
        out += [PP.Brk(), PP.Str("=")]
        args = args[2:]
    # "while" does not require special handling
    first = True
    for a in args:
        if _IsColonEmphemeral(a):
            out += [PP.Brk(0), PP.Str(":")]
            _EmitStatementsSpecial(out, a.args)
            continue
        elif first:
            out += [PP.Brk(1 if is_block_like else 0)]
        else:
            out += [PP.NoBreak(0), PP.Str(","), PP.Brk()]
        first = False
        #
        if isinstance(a, cwast.EphemeralList):
            out += [PP.Str("TODO-LIST")]
        else:
            _EmitExprOrType(out, a)

    if not is_block_like:
        out += [PP.Brk(0), PP.Str(")"), PP.End()]


def _EmitStatementsSpecial(out, lst):
    if not lst:
        return
    out += [PP.End(), PP_BEG_NEST]
    first = True
    for child in lst:
        if not first:
            out += [PP.Brk()]
        first = False
        _EmitStatement(out, child)


def _EmitStatement(out, n):
    _MaybeEmitDoc(out, n)
    out += [PP_BEG_STD]
    _MaybeEmitAnnotations(out, n)
    #
    if isinstance(n, cwast.StmtContinue):
        out += [PP.Str("continue")]
        if n.target.name:
            out += [PP.NoBreak(1), PP.Str(n.target.name)]
    elif isinstance(n, cwast.StmtBreak):
        out += [PP.Str("break")]
        if n.target.name:
            out += [PP.NoBreak(1), PP.Str(n.target.name)]
    elif isinstance(n, cwast.StmtReturn):
        out += [PP.Str("return")]
        if not isinstance(n.expr_ret, cwast.ValVoid):
            out += [PP.NoBreak(1)]
            _EmitExprOrType(out, n.expr_ret)
    elif isinstance(n, cwast.StmtTrap):
        out += [PP.Str("trap")]
    elif isinstance(n, cwast.StmtAssignment):
        _EmitStmtSet(out, "=", n.lhs, n.expr_rhs)
    elif isinstance(n, cwast.StmtCompoundAssignment):
        _EmitStmtSet(out,
                     cwast.ASSIGNMENT_SHORTCUT_INV[n.assignment_kind],
                     n.lhs, n.expr_rhs)
    elif isinstance(n, cwast.DefVar):
        _EmitStmtLetOrGlobal(out, WithExcl("let", n.mut),
                             n.name, n.type_or_auto, n.initial_or_undef_or_auto)
    elif isinstance(n, cwast.StmtExpr):
        out += [PP.Str("do"), PP.NoBreak(1)]
        _EmitExprOrType(out, n.expr)
    elif isinstance(n, cwast.StmtDefer):
        out += [PP.Str("defer"), PP.Brk(0), PP.Str(":")]
        _EmitStatementsSpecial(out, n.body)
    elif isinstance(n, cwast.StmtCond):
        out += [PP.Str("cond"), PP.Brk(0), PP.Str(":")]
        _EmitStatementsSpecial(out, n.cases)
    elif isinstance(n, cwast.Case):
        out += [PP.Str("case"), PP.Brk()]
        _EmitExprOrType(out, n.cond)
        out += [PP.Brk(0), PP.Str(":")]
        _EmitStatementsSpecial(out, n.body)
    elif isinstance(n, cwast.MacroInvoke):
        _EmitStmtMacroInvoke(out, n)
    elif isinstance(n, cwast.MacroId):
        out += [PP.Str(str(n.name))]
    elif isinstance(n, cwast.StmtBlock):
        out += [PP.Str("block"), PP.Brk(), PP.Str(str(n.label)),
                PP.Brk(0), PP.Str(":")]
        _EmitStatementsSpecial(out, n.body)
    elif isinstance(n, cwast.StmtIf):
        out += [PP.Str("if"), PP.Brk()]
        _EmitExprOrType(out, n.cond)
        out += [PP.Brk(0), PP.Str(":")]
        _EmitStatementsSpecial(out, n.body_t)
        if n.body_f:
            out += [PP.End(), PP.Brk(), PP_BEG_STD,
                    PP.Str("else"), PP.Brk(0), PP.Str(":")]
            _EmitStatementsSpecial(out, n.body_f)
    elif isinstance(n, cwast.MacroFor):
        out += [PP.Str("mfor"), PP.Brk(), PP.Str(str(n.name)),
                PP.Brk(), PP.Str(str(n.name_list)),   PP.Brk(0), PP.Str(":")]
        # we know the content of body of the MacroFor must be stmts
        # since it occurs in a stmt context
        _EmitStatementsSpecial(out, n.body_for)

    else:
        assert False, f"{n}"
    out += [PP.End()]


def _EmitTokensExprMacroBlockSpecial(out, stmts):
    out += [PP.End(), PP_BEG_NEST]
    first = True
    for child in stmts:
        if not first:
            out += [PP.Brk()]
        first = False
        _MaybeEmitDoc(out, child)
        out += [PP_BEG_STD]
        _MaybeEmitAnnotations(out, child)
        _EmitExprOrType(out, child)
        out += [PP.End()]


def _EmitTokensToplevel(out, node):
    _MaybeEmitDoc(out, node)
    out += [PP_BEG_STD]
    _MaybeEmitAnnotations(out, node)

    if isinstance(node, cwast.DefGlobal):
        _EmitStmtLetOrGlobal(out, WithExcl("global", node.mut),
                             node.name, node.type_or_auto, node.initial_or_undef_or_auto)
    elif isinstance(node, cwast.Import):
        out += [PP.Str("import"),
                PP.Brk(),
                PP.Str(str(node.name))]
        path = node.path
        if path:
            out += [PP.NoBreak(1), PP.Str("="),
                    PP.Brk(), PP.Str(path)]
        if node.args_mod:
            out += [PP.NoBreak(1)]
            _EmitParenList(out, node.args_mod)
    elif isinstance(node, cwast.DefType):
        out += [PP.Str("type"),
                PP.Brk(),
                PP.Str(str(node.name)),
                PP.Brk(), PP.Str("="), PP.Brk()]
        _EmitExprOrType(out, node.type)
    elif isinstance(node, cwast.DefRec):
        out += [PP.Str("rec"),
                PP.Brk(),
                PP.Str(str(node.name)),
                PP.Brk(0),
                PP.Str(":"), PP.End()]
        out += [PP_BEG_NEST]
        first = True
        for f in node.fields:
            if not first:
                out += [PP.Brk()]
            first = False
            _MaybeEmitDoc(out, f)
            out += [PP_BEG_STD]
            _MaybeEmitAnnotations(out, f)
            out += [PP.Str(str(f.name)), PP.Brk()]
            _EmitExprOrType(out, f.type)
            out += [PP.End()]
    elif isinstance(node, cwast.StmtStaticAssert):
        out += [PP.Str("static_assert"), PP.Brk()]
        _EmitExprOrType(out, node.cond)
    elif isinstance(node, cwast.DefEnum):
        out += [PP.Str("enum"),
                PP.Brk(),
                PP.Str(str(node.name)),
                PP.Brk(),
                PP.Str(node.base_type_kind.name.lower()),
                PP.Brk(0),
                PP.Str(":"),
                PP.End()]
        out += [PP_BEG_NEST]
        first = True
        for ef in node.items:
            if not first:
                out += [PP.Brk()]
            first = False
            _MaybeEmitDoc(out, ef)
            out += [PP_BEG_STD]
            _MaybeEmitAnnotations(out, ef)
            out += [PP.Str(str(ef.name)), PP.Brk()]
            _EmitExprOrType(out, ef.value_or_auto)
            out += [PP.End()]
    elif isinstance(node, cwast.DefFun):
        out += [PP.Str("fun"),
                PP.NoBreak(1),
                PP.Str(str(node.name))]
        out += [PP.NoBreak(0)]
        _EmitParameterList(out, node.params)
        out += [PP.Brk()]
        _EmitExprOrType(out, node.result)
        out += [PP.NoBreak(0), PP.Str(":")]
        _EmitStatementsSpecial(out, node.body)
    elif isinstance(node, cwast.DefMacro):
        out += [PP.Str("macro"),
                PP.Brk(),
                PP.Str(str(node.name)),
                PP.Brk(),
                PP.Str(node.macro_result_kind.name),
                PP.NoBreak(1)]
        _EmitParameterList(out, node.params_macro)
        out += [PP.Brk()]
        _EmitIdList(out, node.gen_ids)
        out += [PP.Brk(0), PP.Str(":")]
        if node.macro_result_kind in (cwast.MACRO_RESULT_KIND.STMT, cwast.MACRO_RESULT_KIND.STMT_LIST):
            _EmitStatementsSpecial(out, node.body_macro)
        else:
            _EmitTokensExprMacroBlockSpecial(out, node.body_macro)
    else:
        assert False
    out += [PP.End()]


def EmitTokensModule(out: list[PP.Token], node: cwast.DefMod):
    _MaybeEmitDoc(out, node)
    out += [PP_BEG_STD]
    _MaybeEmitAnnotations(out, node)

    out += [PP.Str("module")]
    if node.params_mod:
        out += [PP.NoBreak(0)]
        _EmitParameterList(out, node.params_mod)
    out += [PP.Brk(0), PP.Str(":"), PP.End()]
    if node.body_mod:
        out += [PP.Beg(PP.BreakType.FORCE_LINE_BREAK, 0)]
        first = True
        for child in node.body_mod:
            out += [PP.LineBreak()]
            if not first:
                out += [PP.LineBreak()]
            first = False
            _EmitTokensToplevel(out, child)
        out += [PP.End()]

############################################################
#
############################################################


def PrettyPrint(mod: cwast.DefMod, outp):
    checker.CheckAST(mod, set(), pre_symbolize=True)
    out: list[PP.Token] = [PP.Beg(PP.BreakType.CONSISTENT, 0)]
    EmitTokensModule(out, mod)
    out += [PP.End()]
    result = PP.PrettyPrint(out, 80)
    print(result, file=outp)


############################################################
#
############################################################
if __name__ == "__main__":
    import sys

    from FE import parse

    def process_file(inp, _outp):
        mod = parse.ReadModFromStream(inp, "stdin")
        # cwast.AnnotateRoleForMacroInvoke(mod)
        # AddMissingParens(mod)
        PrettyPrint(mod, sys.stdout)

    def main():
        logging.basicConfig(level=logging.WARN)
        logger.setLevel(logging.INFO)
        process_file(sys.stdin, sys.stdout)
    main()
