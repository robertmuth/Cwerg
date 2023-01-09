#!/usr/bin/python3

"""Value annotator for Cwerg AST

"""

import logging

from FrontEnd import cwast
from FrontEnd import symbolize
from FrontEnd import types
from FrontEnd import typify
from Util import parse

from typing import List, Dict, Set, Optional, Union, Any

logger = logging.getLogger(__name__)

_UNDEF = cwast.ValUndef()
_VOID = cwast.ValVoid()


def _AssignValue(node, val):
    logger.info(f"EVAL of {node}: {val}")
    node.x_value = val
    return True


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
            _AssignValue(init, val)
            _AssignValue(c, val)
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

    return _AssignValue(node, rec)


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
            _AssignValue(c.init_index, len(array))
        else:
            index = c.init_index.x_value
            while len(array) < index:
                array.append(curr_val)
        curr_val = _UNDEF
        if not isinstance(c.value_or_undef, cwast.ValUndef):
            curr_val = c.value_or_undef.x_value
        array.append(curr_val)
        _AssignValue(c, curr_val)

    while len(array) < node.x_type.size.x_value:
        array.append(curr_val)
    return _AssignValue(node, array)


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
        if cwast.NF.VALUE_ANNOTATED in def_node.__class__.FLAGS and def_node.x_value is not None:
            return _AssignValue(node, def_node.x_value)
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
    elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
        if not node.mut and node.initial_or_undef.x_value is not None:
            return _AssignValue(node, node.initial_or_undef.x_value)
        return False
    elif isinstance(node, cwast.IndexVal):
        return False  # handled by ValArray
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
            return _AssignValue(node, bytes(s,encoding="ascii"))
        return _AssignValue(node, parse.EscapedStringToBytes(s))
    elif isinstance(node, cwast.ExprIndex):
        if node.container.x_value is not None and node.expr_index.x_value is not None:
            assert type(node.container.x_value) in (list, bytes), f"{node.container.x_value}"
            return _AssignValue(node, node.container.x_value[node.expr_index.x_value])
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
    elif  isinstance(node, cwast.ExprStmt):
        return False
    elif isinstance(node, cwast.ExprAs):
        # TODO: some transforms may need to be applied
        if node.expr.x_value is not None:
            return _AssignValue(node, node.expr.x_value)
            return True
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
    elif isinstance(node, cwast.ExprLen):
        # TODO:
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
    else:
        assert False, f"unexpected node {node}"


def EvalRecursively(node) -> bool:
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
    if seen_change:
        logger.info(f"SEEN CHANGE {node}")
    return seen_change


def _VerifyEvalRecursively(node, parent, is_const) -> bool:
    if isinstance(node, (cwast.Comment, cwast.DefMacro)):
        return
    # logger.info(f"EVAL-VERIFY: {node}")

    if is_const and cwast.NF.VALUE_ANNOTATED in node.__class__.FLAGS:
        if isinstance(node, cwast.Id):
            def_node = node.x_symbol
            if cwast.NF.VALUE_ANNOTATED in def_node.__class__.FLAGS:

                if def_node.x_value is None:
                    if not isinstance(parent.x_type, (cwast.TypePtr, cwast.TypeSlice)):
                        # TODO: we do not track constant addresses yet
                        cwast.CompilerError(def_node.x_srcloc,
                                            f"expected const node: {node} inside: {parent}")
        elif isinstance(node, cwast.ValUndef):
            pass
        else:
            if node.x_value is None:
                if not isinstance(node.x_type, (cwast.TypePtr, cwast.TypeSlice)):
                    # TODO: we do not track constant addresses yet
                    cwast.CompilerError(
                        node.x_srcloc, f"expected const node: {node} inside {parent}")

    # top level definition
    if isinstance(node, cwast.DefGlobal):
        is_const = True
    if isinstance(node, cwast.DefRec):
        is_const = True

    if isinstance(node, cwast.ValAuto):
        assert node.x_value is not None, f"unevaluated auto node: {node}"

    if isinstance(node, cwast.StmtStaticAssert):
        assert node.cond.x_value is True, f"Failed static assert: {node} is {node.cond.x_value}"

    # Note: this info is currently filled in by the Type Decorator
    if isinstance(node, cwast.TypeArray):
        assert node.size.x_value is not None, f"unevaluated type dimension: {node}"

    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            _VerifyEvalRecursively(getattr(node, c), node, is_const)
        elif nfd.kind is cwast.NFK.LIST:
            for cc in getattr(node, c):
                _VerifyEvalRecursively(cc, node, is_const)


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
                if not isinstance(node, (cwast.Comment, cwast.DefMacro)):
                    seen_change |= EvalRecursively(node)

    for mod in mod_topo_order:
        for node in mod.body_mod:
            _VerifyEvalRecursively(node, mod, False)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = cwast.ReadModsFromStream(sys.stdin)

    mod_topo_order, mod_map = symbolize.ModulesInTopologicalOrder(asts)
    symbolize.DecorateASTWithSymbols(mod_topo_order, mod_map)
    type_corpus = types.TypeCorpus(
        cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    typify.DecorateASTWithTypes(mod_topo_order, type_corpus)
    DecorateASTWithPartialEvaluation(mod_topo_order)
