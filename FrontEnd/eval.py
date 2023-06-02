#!/usr/bin/python3

"""Value annotator for Cwerg AST

"""

import logging

from typing import List, Dict, Set, Optional, Union, Any

from FrontEnd import cwast
from FrontEnd import symbolize
from FrontEnd import types
from FrontEnd import typify
from FrontEnd import parse

from Util.parse import EscapedStringToBytes


logger = logging.getLogger(__name__)

_UNDEF = cwast.ValUndef()
_VOID = cwast.ValVoid()


def _VerifyEvalValue(val):
    # TODO: check this recusively
    # "None" is reserve for indicating that evaluation was not possible
    #
    if isinstance(val, list):
        for x in val:
            assert x is not None
    elif isinstance(val, dict):
        for x in val.values():
            assert x is not None
    else:
        assert isinstance(val, (int, float, bytes, cwast.ValUndef,
                          cwast.ValVoid)), f"unexpected value {val}"
        assert val is not None


def _AssignValue(node, val):
    _VerifyEvalValue(val)

    if isinstance(val, list):
        logger.info(f"EVAL of {node}: {val[:8]}...")
    else:
        logger.info(f"EVAL of {node}: {val}")
    node.x_value = val
    return True


def _EvalDefEnum(node: cwast.DefEnum) -> bool:
    """TBD"""
    out = False
    val = 0
    for c in node.items:
        assert isinstance(c, cwast.EnumVal)
        if not isinstance(c.value_or_auto, cwast.ValAuto):
            assert c.value_or_auto.x_value is not None
            val = c.value_or_auto.x_value
        if c.x_value is None:
            _AssignValue(c.value_or_auto, val)
            _AssignValue(c, val)
            out = True
        val += 1
    return out


def _EvalValRec(node: cwast.ValRec) -> bool:
    # first pass if we cannot evaluate everyting, we must give up
    rec = {}
    for field, init in symbolize.IterateValRec(node, node.x_type):
        if init is None:
            rec[field.name] = _UNDEF
        else:
            assert isinstance(init, cwast.FieldVal), f"{init}"
            if init.value.x_value is None:
                return False
            rec[field.name] = init.value.x_value
    return _AssignValue(node, rec)


def _EvalValArray(node: cwast.ValArray) -> bool:
    has_unknown = False
    # first pass if we cannot evaluate everyting, we must give up
    # This could be relaxed if we allow None values in "out"
    for c in node.inits_array:
        assert isinstance(c, cwast.IndexVal)
        if not isinstance(c.init_index, cwast.ValAuto):
            if c.init_index.x_value is None:
                has_unknown = True
                break
        if not isinstance(c.value_or_undef, cwast.ValUndef):
            if c.value_or_undef.x_value is None:
                has_unknown = True
                break
    if has_unknown:
        return False
    curr_val = _UNDEF
    array = []
    for n, c in symbolize.IterateValArray(node, node.x_type.size.x_value):
        if c is None:
            array.append(curr_val)
            continue
        curr_val = c.value_or_undef.x_value
        if curr_val is None:
            return False
        array.append(curr_val)
    return _AssignValue(node, array)


def _eval_not(node) -> bool:
    assert types.is_bool(node.x_type)
    return not node.x_value


def _eval_neg(node) -> int:
    assert types.is_uint(node.x_type)
    return ~node.x_value & ((1 << (node.x_type.x_size * 8)) - 1)


def _eval_minus(node) -> Any:
    return - node.x_value


_EVAL1 = {
    cwast.UNARY_EXPR_KIND.NOT: _eval_not,
    cwast.UNARY_EXPR_KIND.NEG: _eval_neg,
    cwast.UNARY_EXPR_KIND.MINUS: _eval_minus,
}


def _EvalExpr1(node: cwast.Expr1) -> bool:
    if node.expr.x_value is None:
        return False
    return _AssignValue(node, _EVAL1[node.unary_expr_kind](node.expr))


# TODO: naive implementation -> needs a lot more scrutiny
_EVAL2_ANY = {
    cwast.BINARY_EXPR_KIND.ADD: lambda x, y: x.x_value + y.x_value,
    cwast.BINARY_EXPR_KIND.SUB: lambda x, y: x.x_value - y.x_value,
    cwast.BINARY_EXPR_KIND.MUL: lambda x, y: x.x_value * y.x_value,
    cwast.BINARY_EXPR_KIND.EQ: lambda x, y: x.x_value == y.x_value,
    cwast.BINARY_EXPR_KIND.NE: lambda x, y: x.x_value != y.x_value,
    cwast.BINARY_EXPR_KIND.LT: lambda x, y: x.x_value < y.x_value,
    cwast.BINARY_EXPR_KIND.LE: lambda x, y: x.x_value <= y.x_value,
    cwast.BINARY_EXPR_KIND.GT: lambda x, y: x.x_value > y.x_value,
    cwast.BINARY_EXPR_KIND.GE: lambda x, y: x.x_value >= y.x_value,
}

_EVAL2_REAL = {
    cwast.BINARY_EXPR_KIND.DIV: lambda x, y: x.x_value / y.x_value,
}

_EVAL2_INT = {
    cwast.BINARY_EXPR_KIND.DIV: lambda x, y: x.x_value // y.x_value,
    cwast.BINARY_EXPR_KIND.REM: lambda x, y: x.x_value % y.x_value,

}

_EVAL2_UINT = {
    cwast.BINARY_EXPR_KIND.SHL: lambda x, y: x.x_value << y.x_value,
    cwast.BINARY_EXPR_KIND.SHR: lambda x, y: x.x_value >> y.x_value,
    cwast.BINARY_EXPR_KIND.OR: lambda x, y: x.x_value | y.x_value,
    cwast.BINARY_EXPR_KIND.AND: lambda x, y: x.x_value & y.x_value,
    cwast.BINARY_EXPR_KIND.XOR: lambda x, y: x.x_value ^ y.x_value,
}


def _EvalExpr2(node: cwast.Expr2) -> bool:
    if node.expr1.x_value is None or node.expr2.x_value is None:
        return False
    op = node.binary_expr_kind
    if op in _EVAL2_ANY:
        return _AssignValue(node, _EVAL2_ANY[op](node.expr1, node.expr2))
    elif types.is_real(node.x_type):
        if op in _EVAL2_REAL:
            return _AssignValue(node, _EVAL2_REAL[op](node.expr1, node.expr2))
    elif types.is_int(node.x_type):
        if op in _EVAL2_INT:
            return _AssignValue(node, _EVAL2_INT[op](node.expr1, node.expr2))
    elif types.is_real(node.x_type):
        if op in _EVAL2_UINT:
            return _AssignValue(node, _EVAL2_UINT[op](node.expr1, node.expr2))
    return False


def _EvalExpr3(node: cwast.Expr3) -> bool:
    if node.cond.x_value is None:
        return False
    if node.cond.x_value:
        if node.expr_t.x_value is not None:
            return _AssignValue(node, node.expr_t.x_value)
    else:
        if node.expr_f.x_value is not None:
            return _AssignValue(node, node.expr_f.x_value)
    return False


def _EvalNode(node: cwast.ALL_NODES) -> bool:

    if isinstance(node, cwast.Id):
        # this case is why we need the sym_tab
        def_node = node.x_symbol
        assert def_node is not None
        if isinstance(def_node, (cwast.DefGlobal, cwast.DefVar)):
            if not def_node.mut and def_node.initial_or_undef.x_value is not None:
                return _AssignValue(node, def_node.initial_or_undef.x_value)
        elif isinstance(def_node, cwast.EnumVal):
            return _AssignValue(node, def_node.value_or_auto.x_value)
        return False
    elif isinstance(node, cwast.RecField):
        if node.initial_or_undef.x_value is not None:
            return _AssignValue(node, node.initial_or_undef.x_value)
        return False
    elif isinstance(node, cwast.EnumVal):
        return False  # handles as part of DefEnum
    elif isinstance(node, cwast.DefEnum):
        return _EvalDefEnum(node)
    elif isinstance(node, cwast.ValTrue):
        return _AssignValue(node, True)
    if isinstance(node, cwast.ValFalse):
        return _AssignValue(node, False)
    elif isinstance(node, cwast.ValVoid):
        return _AssignValue(node, _VOID)
    elif isinstance(node, cwast.ValUndef):
        return _AssignValue(node, _UNDEF)
    elif isinstance(node, cwast.ValNum):
        cstr = node.x_type
        if isinstance(cstr, cwast.TypeBase):
            return _AssignValue(node, typify.ParseNum(node.number, cstr.base_type_kind))
        elif isinstance(cstr, cwast.DefEnum):
            return _AssignValue(node, typify.ParseNum(node.number, cstr.base_type_kind))
        else:
            assert False, f"unepxected type for ValNum: {cstr}"
            return False
    elif isinstance(node, cwast.ValAuto):
        return False
    elif isinstance(node, cwast.IndexVal):
        if node.value_or_undef.x_value is not None:
            return _AssignValue(node, node.value_or_undef.x_value)
        return False
    elif isinstance(node, cwast.ValArray):
        return _EvalValArray(node)
    elif isinstance(node, cwast.FieldVal):
        if node.value.x_value is not None:
            return _AssignValue(node, node.value.x_value)
        return False
    elif isinstance(node, cwast.ValRec):
        return _EvalValRec(node)
    elif isinstance(node, cwast.ValString):
        s = node.string
        assert s[0] == '"' and s[-1] == '"', f"expected string [{s}]"
        s = s[1:-1]
        if node.raw:
            return _AssignValue(node, bytes(s, encoding="ascii"))
        return _AssignValue(node, EscapedStringToBytes(s))
    elif isinstance(node, cwast.ExprIndex):
        index_val = node.expr_index.x_value
        container_val = node.container.x_value
        if container_val is not None and index_val is not None:
            assert isinstance(container_val, (list, bytes)
                              ), f"{node.container.x_value}"
            assert index_val < len(
                container_val), f"{index_val} {container_val}"
            return _AssignValue(node, container_val[index_val])
        return False
    elif isinstance(node, cwast.ExprField):
        if node.container.x_value is not None:
            assert node.field in node.container.x_value
            return _AssignValue(node, node.container.x_value[node.field])
        return False
    elif isinstance(node, cwast.Expr1):
        return _EvalExpr1(node)
    elif isinstance(node, cwast.Expr2):
        return _EvalExpr2(node)
    elif isinstance(node, cwast.Expr3):
        return _EvalExpr3(node)
    elif isinstance(node, cwast.ExprCall):
        # TODO
        return False
    elif isinstance(node, cwast.ExprStmt):
        return False
    elif isinstance(node, cwast.ExprAs):
        # TODO: some transforms may need to be applied
        if node.expr.x_value is not None:
            return _AssignValue(node, node.expr.x_value)
            return True
        return False
    elif isinstance(node, cwast.ExprTryAs):
        # TODO: we can do better here
        return False
    elif isinstance(node, cwast.ExprAsNot):
        # TODO: we can do better here
        return False
    elif isinstance(node, (cwast.ExprBitCast, cwast.ExprUnsafeCast)):
        # TODO: we can do better here
        return False
    elif isinstance(node, cwast.ExprIs):
        # TODO: we can do better here
        return False
    elif isinstance(node, cwast.ExprPointer):
        # TODO: we can do better here
        return False
    elif isinstance(node, cwast.ExprFront):
        # TODO: we can do better here
        return False
    elif isinstance(node, cwast.ExprLen):
        if isinstance(node.container.x_type, cwast.TypeArray):
            return _AssignValue(node, node.container.x_type.size.x_value)
        elif node.container.x_value is not None:
            return _AssignValue(node, len(node.container.x_value))
        return False
    elif isinstance(node, cwast.ExprAddrOf):
        # TODO: we can do better here
        return False
    elif isinstance(node, cwast.ExprOffsetof):
        # assert node.x_field.x_offset > 0
        return _AssignValue(node, node.x_field.x_offset)
        return True
    elif isinstance(node, cwast.ExprSizeof):
        return _AssignValue(node, node.type.x_type.x_size)
    elif isinstance(node, cwast.ExprDeref):
        # TODO maybe track symbolic addresses
        return False
    elif isinstance(node, cwast.ExprAddrOf):
        # TODO maybe track symbolic addresses
        return False
    elif isinstance(node, cwast.ValSlice):
        # TODO maybe track symbolic addresses
        return False
    else:
        assert False, f"unexpected node {node}"


def EvalRecursively(node) -> bool:
    seen_change = False

    def visitor(node, _):
        nonlocal seen_change
        if cwast.NF.VALUE_ANNOTATED not in node.FLAGS:
            return
        if node.x_value is not None:
            return
        seen_change |= _EvalNode(node)

    cwast.VisitAstRecursivelyPost(node, visitor)

    if seen_change:
        logger.info(f"SEEN CHANGE {node}")
    return seen_change


def VerifyASTEvalsRecursively(node):
    is_const = False

    def visitor(node, parent, field):
        nonlocal is_const
        # logger.info(f"EVAL-VERIFY: {node}")
        if isinstance(node, cwast.ValUndef):
            return
        if cwast.NF.TOP_LEVEL in node.FLAGS:
            is_const = isinstance(
                node, (cwast.DefRec, cwast.DefGlobal, cwast.DefEnum))
            return

        if isinstance(node, (cwast.ValTrue, cwast.ValFalse, cwast.ValNum, cwast.ValString)):
            assert node.x_value is not None, f"{node}"

        if is_const and cwast.NF.VALUE_ANNOTATED in node.FLAGS:
            if isinstance(node, cwast.Id):
                def_node = node.x_symbol
                if cwast.NF.VALUE_ANNOTATED in def_node.FLAGS:

                    if def_node.x_value is None:
                        if isinstance(parent.x_type, (cwast.TypePtr, cwast.TypeSlice)):
                            # TODO: we do not track constant addresses yet
                            # for now assume they are constant
                            pass
                        else:
                            cwast.CompilerError(def_node.x_srcloc,
                                                f"expected const node: {node} inside: {parent}")
            else:
                if node.x_value is None:
                    if isinstance(node.x_type, (cwast.TypePtr, cwast.TypeSlice)):
                        # TODO: we do not track constant addresses yet
                        # for now assume they are constant
                        pass
                    elif isinstance(node, cwast.ValAuto) and field == "init_index":
                        pass
                    else:
                        cwast.CompilerError(
                            node.x_srcloc, f"expected const node: {node} inside {parent}")

        if field == "init_index":
            assert node.x_value is not None or isinstance(node,
                                                          cwast.ValAuto), f"unevaluated ValArray init index: {node}"

        if isinstance(node, cwast.StmtStaticAssert):
            assert node.cond.x_value is True, f"Failed static assert: {node} is {node.cond.x_value}"

        # Note: this info is currently filled in by the Type Decorator
        if isinstance(node, cwast.TypeArray):
            assert node.size.x_value is not None, f"unevaluated type dimension: {node}"

    cwast.VisitAstRecursivelyWithParent(node, visitor, None, None)


def DecorateASTWithPartialEvaluation(mod_topo_order: List[cwast.DefMod]):
    """
    """
    iteration = 0
    seen_change = True
    while seen_change:
        iteration += 1
        logger.info("Eval Iteration %d", iteration)
        seen_change = False
        for mod in mod_topo_order:
            for node in mod.body_mod:
                seen_change |= EvalRecursively(node)

    for mod in mod_topo_order:
        VerifyASTEvalsRecursively(mod)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = parse.ReadModsFromStream(sys.stdin)

    mod_topo_order, mod_map = symbolize.ModulesInTopologicalOrder(asts)
    symbolize.MacroExpansionDecorateASTWithSymbols(mod_topo_order, mod_map)
    for mod in mod_topo_order:
        cwast.StripFromListRecursively(mod, cwast.Comment)
        cwast.StripFromListRecursively(mod, cwast.DefMacro)
    type_corpus = types.TypeCorpus(
        cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    typify.DecorateASTWithTypes(mod_topo_order, type_corpus)
    DecorateASTWithPartialEvaluation(mod_topo_order)
