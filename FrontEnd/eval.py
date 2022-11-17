#!/usr/bin/python3

"""Value annotator for Cwerg AST

"""

import logging

from FrontEnd import cwast
from FrontEnd import symtab
from FrontEnd import types
from FrontEnd import meta

from typing import List, Dict, Set, Optional, Union, Any

logger = logging.getLogger(__name__)

_UNDEF = cwast.ValUndef()
_VOID = cwast.ValVoid()


def _EvalDefEnum(node: cwast.DefEnum) -> bool:
    out = False
    val = 0
    for c in node.items:
        if not isinstance(c, cwast.EnumVal):
            continue
        v = c.x_value
        if v is not None:
            val = v + 1
            continue
        init = c.value_or_auto
        if not isinstance(init, cwast.ValAuto):
            _EvalNode(init)
            val = init.x_value

        if val is not None:
            init.x_value = val
            c.x_value = val
            val += 1
    return out


def _EvalValRec(node: cwast.ValRec) -> bool:
    out = False
    num_unknown = 0
    for c in node.inits_rec:
        if not isinstance(c, cwast.FieldVal):
            continue
        if c.value.x_value is None:
            num_unknown += 1
    for c in node.x_type.fields:
        if not isinstance(c, cwast.RecField):
            continue
        if not isinstance(c.initial_or_undef, cwast.ValUndef):
            if c.initial_or_undef.x_value is None:
                num_unknown += 1

    if num_unknown > 0:
        return out

    fields: List[cwast.RecField] = [
        f for f in node.x_type.fields if isinstance(f, cwast.RecField)]
    values: List[cwast.FieldVal] = [
        v for v in node.inits_rec if isinstance(v, cwast.FieldVal)]

    rec = {}
    for f in fields:
        if values and (f.name == values[0].init_field or values[0].init_field == ""):
            rec[f.name] = values[0].x_value
            values.pop(0)
        else:
            rec[f.name] = f.x_value

    node.x_value = rec
    return True


def _EvalValArray(node: cwast.ValArray) -> bool:
    out = False
    num_unknown = 0
    for c in node.inits_array:
        if not isinstance(c, cwast.IndexVal):
            continue
        if not isinstance(c.init_index, cwast.ValAuto):
            if c.init_index.x_value is None:
                out |= _EvalNode(c.init_index)
                if c.init_index.x_value is None:
                    num_unknown += 1
        if not isinstance(c.value_or_undef, cwast.ValUndef):
            if c.value_or_undef.x_value is None:
                out |= _EvalNode(c.value_or_undef)
                if c.value_or_undef.x_value is None:
                    num_unknown += 1
    if num_unknown > 0:
        return out
    curr_val = _UNDEF
    array = []
    for c in node.inits_array:
        if not isinstance(c, cwast.IndexVal):
            continue
        if isinstance(c.init_index, cwast.ValAuto):
            c.init_index.x_value = len(array)
        else:
            index = c.init_index.x_value
            while len(array) < index:
                array.append(curr_val)
        curr_val = _UNDEF
        if not isinstance(c.value_or_undef, cwast.ValUndef):
            curr_val = c.value_or_undef.x_value
        array.append(curr_val)
        c.x_value = curr_val

    while len(array) < node.x_type.size.x_value:
        array.append(curr_val)
    node.x_value = array
    return True


def _eval_not(node) -> bool:
    assert types.is_bool(node.x_type)
    return not node.x_value


def _eval_neg(node) -> int:
    assert types.is_uint(node.x_type)
    return ~node.x_value


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
    node.x_value = _EVAL1[node.unary_expr_kind](node.expr)
    return True


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
        node.x_value = _EVAL2_ANY[op](node.expr1, node.expr2)
        return True
    elif types.is_real(node.x_type):
        if op in _EVAL2_REAL:
            node.x_value = _EVAL2_REAL[op](node.expr1, node.expr2)
            return True
    elif types.is_int(node.x_type):
        if op in _EVAL2_INT:
            node.x_value = _EVAL2_INT[op](node.expr1, node.expr2)
            return True
    elif types.is_real(node.x_type):
        if op in _EVAL2_UINT:
            node.x_value = _EVAL2_UINT[op](node.expr1, node.expr2)
            return True
    return False


def _EvalExpr3(node: cwast.Expr3) -> bool:
    if node.cond.x_value is None:
        return False
    if node.cond.x_value:
        if node.expr_t.x_value is not None:
            node.x_value = node.expr_t.x_value
            return True
    else:
        if node.expr_f.x_value is not None:
            node.x_value = node.expr_f.x_value
            return True
    return False


def _EvalNode(node: cwast.ALL_NODES) -> bool:

    if isinstance(node, cwast.Id):
        # this case is why we need the sym_tab
        def_node = node.x_symbol
        assert def_node is not None
        if cwast.NF.VALUE_ANNOTATED in def_node.__class__.FLAGS and def_node.x_value:
            node.x_value = def_node.x_value
            return True
        return False
    elif isinstance(node, cwast.RecField):
        if node.initial_or_undef.x_value is not None:
            node.x_value = node.initial_or_undef.x_value
            return True
        return False
    elif isinstance(node, cwast.EnumVal):
        return False  # handles as part of DefEnum
    elif isinstance(node, cwast.DefEnum):
        return _EvalDefEnum(node)
    elif isinstance(node, cwast.ValTrue):
        node.x_value = True
        return True
    if isinstance(node, cwast.ValFalse):
        node.x_value = False
        return True
    elif isinstance(node, cwast.ValVoid):
        node.x_value = _VOID
        return True
    elif isinstance(node, cwast.ValUndef):
        node.x_value = _UNDEF
        return True
    elif isinstance(node, cwast.ValNum):
        node.x_value = meta.ParseNum(node.number)
        return True
    elif isinstance(node, cwast.ValAuto):
        return False
    elif isinstance(node, cwast.DefConst):
        if node.value.x_value is not None:
            node.x_value = node.value.x_value
            return True
        return False
    elif isinstance(node, cwast.IndexVal):
        return False  # handled by ValArray
    elif isinstance(node, cwast.ValArray):
        return _EvalValArray(node)
    elif isinstance(node, cwast.FieldVal):
        if node.value.x_value is not None:
            node.x_value = node.value.x_value
            return True
        return False
    elif isinstance(node, cwast.ValRec):
        return _EvalValRec(node)
    elif isinstance(node, cwast.ValString):
        node.x_value = node.string
        return True
    elif isinstance(node, cwast.ExprIndex):
        if node.container.x_value is not None and node.expr_index.x_value is not None:
            assert type(node.container.x_value) is list
            node.x_value = node.container.x_value[node.expr_index.x_value]
            return True
        return False
    elif isinstance(node, cwast.ExprField):
        if node.container.x_value is not None:
            assert node.field in node.container.x_value
            node.x_value = node.container.x_value[node.field]
            return True
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
    elif isinstance(node, (cwast.ExprAs, cwast.ExprBitCast, cwast.ExprUnsafeCast)):
        # TODO
        return False
    elif isinstance(node, cwast.ExprIs):
        # TODO
        return False
    elif isinstance(node, cwast.ExprLen):
        # TODO
        return False
    elif isinstance(node, cwast.ExprChop):
        # TODO
        return False
    elif isinstance(node, cwast.ExprAddrOf):
        return False
    elif isinstance(node, cwast.ExprOffsetof):
        # TODO FIXME
        node.x_value = 666
        return True
    elif isinstance(node, cwast.ExprSizeof):
        # TODO
        return False
    elif isinstance(node, cwast.ExprDeref):
        # TODO maybe track symbolic addresses
        return False
    elif isinstance(node, cwast.ExprAddrOf):
        # TODO maybe track symbolic addresses
        return False 
    else:
        assert False, f"unexpected node {node}"


def EvalRecursively(node) -> bool:
    logger.info(f"EVAL: {node}")
    if cwast.NF.VALUE_ANNOTATED in node.__class__.FLAGS and node.x_value is not None:
        return False
    seen_change = False
    # post order traversal works best
    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            seen_change = EvalRecursively(getattr(node, c))
        elif nfd.kind is cwast.NFK.LIST:
            for cc in getattr(node, c):
                seen_change |= EvalRecursively(cc)
    if cwast.NF.VALUE_ANNOTATED in node.__class__.FLAGS:
        seen_change |= _EvalNode(node)
        logger.info(f"RESULT: {node.x_value} {node}")
    if seen_change:
        logger.info(f"SEEN CHANGE {node}")
    return seen_change


def PartialEvaluation(mod_topo_order: List[cwast.DefMod],
                      mod_map: Dict[str, cwast.DefMod]):
    """
    """
    iteration = 0
    seen_change = True
    while seen_change:
        iteration += 1
        logger.info("Eval Iteration %d", iteration)
        seen_change = False
        for m in mod_topo_order:
            for node in mod_map[m].body_mod:
                seen_change |= EvalRecursively(node)


def VerifyEvalRecursively(node, is_const) -> bool:
    logger.info(f"EVAL-VERIFY: {node}")

    if is_const and cwast.NF.VALUE_ANNOTATED in node.__class__.FLAGS:
        if isinstance(node, cwast.Id):
            def_node = node.x_symbol
            if cwast.NF.VALUE_ANNOTATED in def_node.__class__.FLAGS:
                assert def_node.x_value is not None, f"unevaluated const node: {def_node}"
        else:
            assert node.x_value is not None, f"unevaluated const node: {node}"

    if isinstance(node, cwast.DefConst):
        is_const = True
    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            VerifyEvalRecursively(getattr(node, c), is_const)
        elif nfd.kind is cwast.NFK.LIST:
            for cc in getattr(node, c):
                VerifyEvalRecursively(cc, is_const)


def VerifyPartialEvaluation(mod_topo_order: List[cwast.DefMod],
                            mod_map: Dict[str, cwast.DefMod]):
    for m in mod_topo_order:
        for node in mod_map[m].body_mod:
            VerifyEvalRecursively(node, False)


if __name__ == "__main__":
    import sys

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

    mod_topo_order, mod_map = symtab.ModulesInTopologicalOrder(asts)
    symtab_map = symtab.ExtractAllSymTabs(mod_topo_order, mod_map)
    meta.ExtractTypeTab(mod_topo_order, mod_map)
    PartialEvaluation(mod_topo_order, mod_map)
    VerifyPartialEvaluation(mod_topo_order, mod_map)
