"""Canonicalize Misc

"""

from typing import List, Dict, Set, Optional, Union, Any

from FrontEnd import identifier
from FrontEnd import cwast
from FrontEnd import types

############################################################
#
############################################################


def _IdNodeFromDef(def_node: cwast.DefVar, x_srcloc):
    assert def_node.type_or_auto.x_type is not None
    return cwast.Id(def_node.name, x_srcloc=x_srcloc, x_type=def_node.type_or_auto.x_type,
                    x_value=def_node.initial_or_undef_or_auto.x_value, x_symbol=def_node)


def CanonicalizeStringVal(node, str_map: Dict[str, Any], id_gen_global: identifier.IdGen):
    """Move string/array values into global (un-mutable variables)"""
    def replacer(node, field):
        # TODO: add support for ValArray
        if isinstance(node, cwast.ValString):
            assert isinstance(
                node.x_value, bytes), f"expected str got {node.x_value}"
            def_node = str_map.get(node.x_value)
            if not def_node:
                def_node = cwast.DefGlobal(id_gen_global.NewName("global_str"),
                                           cwast.TypeAuto(
                                               node.x_srcloc, x_type=node.x_type), node,
                                           pub=True,
                                           x_srcloc=node.x_srcloc)
                str_map[node.x_value] = def_node

            return _IdNodeFromDef(def_node, node.x_srcloc)
        return None

    cwast.MaybeReplaceAstRecursively(node, replacer)


def _ShouldBeBoolExpanded(node, field):
    # these nodes do not represent a complex boolean expression
    if not isinstance(node, (cwast.Expr1, cwast.Expr2)):
        return False
    # the field condition ensures that the node
    # * is not part of a conditional
    # * has a x_type
    return field in (
        "args", "expr_rhs", "initial_or_undef_or_auto", "value",
        "value_or_undef") and types.is_bool(node.x_type)


def CanonicalizeBoolExpressionsNotUsedForConditionals(node, tc: types.TypeCorpus):
    """transform a complex bool expression e into "e ? true : false"

    This will make it eligible for CanonicalizeTernaryOp which is the only way currently
    to materialize boolean values
     """
    def replacer(node, field):
        if not _ShouldBeBoolExpanded(node, field):
            return None
        cstr_bool = tc.insert_base_type(cwast.BASE_TYPE_KIND.BOOL)
        return cwast.Expr3(node,
                           cwast.ValTrue(x_srcloc=node.x_srcloc,
                                         x_type=cstr_bool, x_value=True),
                           cwast.ValFalse(
                               x_srcloc=node.x_srcloc, x_type=cstr_bool, x_value=False),
                           x_srcloc=node.x_srcloc, x_type=node.x_type, x_value=node.x_value)

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)


def CanonicalizeTernaryOp(node, id_gen: identifier.IdGen):
    """Convert ternary operator nodes into  expr with if statements

    Note we could implement the ternary op as a macro but would lose the ability to do
    type inference, so instead we use this hardcoded rewrite"""
    def replacer(node, field):
        if isinstance(node, cwast.Expr3):
            srcloc = node.x_srcloc
            name_t = id_gen.NewName("op_t")
            def_t = cwast.DefVar(name_t,
                                 cwast.TypeAuto(
                                     x_srcloc=srcloc, x_type=node.x_type), node.expr_t,
                                 x_srcloc=srcloc)
            name_f = id_gen.NewName("op_f")
            def_f = cwast.DefVar(name_f, cwast.TypeAuto(x_type=node.x_type, x_srcloc=srcloc), node.expr_f,
                                 x_srcloc=srcloc)

            expr = cwast.ExprStmt([], x_srcloc=srcloc,
                                  x_type=node.x_type, x_value=node.x_value)
            expr.body = [
                def_t,
                def_f,
                cwast.StmtIf(node.cond, [
                    cwast.StmtReturn(_IdNodeFromDef(
                        def_t, srcloc), x_srcloc=srcloc, x_target=expr)
                ], [
                    cwast.StmtReturn(_IdNodeFromDef(
                        def_f, srcloc), x_srcloc=srcloc, x_target=expr)
                ],  x_srcloc=srcloc)

            ]
            return expr
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)


############################################################
#
############################################################


def _AssigmemtNode(assignment_kind, lhs, expr, x_srcloc):

    rhs = cwast.Expr2(cwast.COMPOUND_KIND_TO_EXPR_KIND[assignment_kind],
                      cwast.CloneNodeRecursively(lhs, {}, {}),
                      expr, x_srcloc=x_srcloc, x_type=lhs.x_type)
    return cwast.StmtAssignment(lhs, rhs, x_srcloc=x_srcloc)


# Note, the desugaring of CompoundAssignment is made more complicated because we do not want
# just take the address of an object.
# Otherwise, we could just do:
#    addr_type = tc.insert_ptr_type(True, node.lhs.x_type)
#    addr = cwast.ExprAddrOf(True, node.lhs,
#                            x_srcloc=node.x_srcloc, x_type=addr_type)
#    def_node = cwast.DefVar(False, False, id_gen.NewName("assign"),
#                            cwast.TypeAuto(x_srcloc=node.x_srcloc, x_type=addr_type),
#                             addr, x_srcloc=node.x_srcloc)
#    lhs = cwast.ExprDeref(_IdNodeFromDef(
#                def_node, node.x_srcloc), x_srcloc=node.x_srcloc, x_type=node.lhs.x_type)
#    new_assignment = _AssigmemtNode(node.assignment_kind, lhs, node.expr_rhs, node.x_srcloc)
#    return cwast.EphemeralList(True, [def_node, new_assignment])
#
def _HandleCompoundAssignmentExprField(node: cwast.StmtCompoundAssignment, lhs: cwast.ExprField, id_gen):
    if isinstance(lhs.container, cwast.Id):
        return _AssigmemtNode(node.assignment_kind, lhs, node.expr_rhs, node.x_srcloc)
    elif isinstance(lhs.container, cwast.ExprDeref):
        pointer_expr = lhs.container.expr
        if isinstance(pointer_expr, cwast.Id):
            return _AssigmemtNode(node.assignment_kind, lhs, node.expr_rhs, node.x_srcloc)
        def_node = cwast.DefVar(id_gen.NewName("assign"),
                                cwast.TypeAuto(x_srcloc=node.x_srcloc,
                                               x_type=pointer_expr.x_type),
                                pointer_expr, x_srcloc=node.x_srcloc)
        deref = cwast.ExprDeref(_IdNodeFromDef(
            def_node, node.x_srcloc), x_srcloc=node.x_srcloc, x_type=node.lhs.container.x_type)
        field_access = cwast.ExprField(
            deref, lhs.field, x_field=lhs.field, x_type=lhs.x_type, x_srcloc=lhs.x_srcloc)
        new_assignment = _AssigmemtNode(
            node.assignment_kind, field_access, node.expr_rhs, node.x_srcloc)
        return cwast.EphemeralList([def_node, new_assignment], colon=True)

    else:
        assert False, "NYI"


def CanonicalizeCompoundAssignments(node, tc: types.TypeCorpus, id_gen: identifier.IdGen):
    """Convert StmtCompoundAssignment to StmtAssignment"""
    def replacer(node, field):
        if isinstance(node, cwast.StmtCompoundAssignment):
            if isinstance(node.lhs, cwast.Id):
                return _AssigmemtNode(node.assignment_kind, node.lhs, node.expr_rhs, node.x_srcloc)
            elif isinstance(node.lhs, cwast.ExprField):
                return _HandleCompoundAssignmentExprField(node, node.lhs, id_gen)
            else:
                assert False, "NYI"

    cwast.MaybeReplaceAstRecursively(node, replacer)
    cwast.EliminateEphemeralsRecursively(node)


def ReplaceConstExpr(node):
    """
     This should elminate all of ExprSizeOf and ExprOffsetOf as a side-effect
    """
    def replacer(node, field):
        if isinstance(node, cwast.EnumVal) and isinstance(node.value_or_auto, cwast.ValAuto):
            assert node.x_value is not None
        if cwast.NF.VALUE_ANNOTATED not in node.FLAGS or node.x_value is None:
            return None
        if field in ("expr_lhs", "inits_array", "inits_rec"):
            return
        if isinstance(node, (cwast.DefVar, cwast.DefGlobal, cwast.ValUndef, cwast.RecField)):
            return

        if (isinstance(node.x_type, cwast.TypeBase) and
                types.is_int(node.x_type) and not isinstance(node, cwast.ValNum)):
            return cwast.ValNum(str(node.x_value),
                                x_srcloc=node.x_srcloc, x_type=node.x_type, x_value=node.x_value)
        return None

    cwast.MaybeReplaceAstRecursively(node, replacer)


def CanonicalizeRemoveStmtCond(node):
    """Convert StmtCond to nested StmtIf"""
    def replacer(node, _):
        if not isinstance(node, cwast.StmtCond):
            return None
        if not node.cases:
            return cwast.EphemeralList([])

        out = None
        for case in reversed(node.cases):
            assert isinstance(case, cwast.Case)
            out = cwast.StmtIf(case.cond, case.body, [] if out is None else [
                out], x_srcloc=case.x_srcloc)
        return out

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)


def OptimizeKnownConditionals(node):
    def replacer(node, _):
        if isinstance(node, cwast.StmtIf):
            if isinstance(node.cond, cwast.ValTrue):
                node.body_f.clear()
            elif isinstance(node.cond, cwast.ValFalse):
                node.body_t.clear()
        return None

    cwast.VisitAstRecursivelyPost(node, replacer)


def _ConvertIndex(node: cwast.ExprIndex, is_lhs, uint_type, tc: types.TypeCorpus, srcloc):
    container_type = node.container.x_type
    bound = None
    if isinstance(container_type, cwast.TypeArray):
        bound = container_type.size.x_value
    cstr_ptr = tc.insert_ptr_type(is_lhs, container_type.type)
    bound = cwast.ExprLen(cwast.CloneNodeRecursively(
        node.container, {}, {}), x_srcloc=srcloc, x_type=uint_type, x_value=bound)
    start_addr = cwast.ExprFront(
        node.container, x_srcloc=srcloc, x_type=cstr_ptr, mut=is_lhs)
    elem_addr = cwast.ExprPointer(
        cwast.POINTER_EXPR_KIND.INCP, start_addr, node.expr_index, bound,  x_srcloc=srcloc, x_type=start_addr.x_type)
    return cwast.ExprDeref(elem_addr, x_srcloc=srcloc,
                           x_type=node.x_type, x_value=node.x_value)


def ReplaceExprIndex(node, tc):
    uint_type = tc.insert_base_type(cwast.BASE_TYPE_KIND.UINT)

    def replacer(node, field):
        nonlocal tc, uint_type
        if isinstance(node, cwast.ExprIndex):
            return _ConvertIndex(node, field == "lhs", uint_type, tc, node.x_srcloc)
        else:
            return None

    cwast.MaybeReplaceAstRecursively(node, replacer)


def CanonicalizeDefer(node, scopes):
    if isinstance(node, cwast.DefFun):
        scopes.append((node, []))

    if isinstance(node, cwast.StmtDefer):
        scopes[-1][1].append(node)

    def handle_cfg(target):
        out = []
        for scope, defers in reversed(scopes):
            for defer in reversed(defers):
                clone = cwast.CloneNodeRecursively(defer, {}, {})
                out += clone.body
            if scope is target:
                break
        return out

    if cwast.NF.CONTROL_FLOW in node.FLAGS:
        return cwast.EphemeralList(handle_cfg(node.x_target) + [node], colon=False)

    for field, nfd in node.__class__.FIELDS:
        if nfd.kind is cwast.NFK.NODE:
            child = getattr(node, field)
            new_child = CanonicalizeDefer(child, scopes)
            if new_child:
                setattr(node, child, new_child)
        elif nfd.kind is cwast.NFK.LIST:
            if field in cwast.NEW_SCOPE_FIELDS:
                scopes.append((node, []))
            children = getattr(node, field)
            for n, child in enumerate(children):
                new_child = CanonicalizeDefer(child, scopes)
                if new_child:
                    children[n] = new_child
            if field in cwast.NEW_SCOPE_FIELDS:
                if children and not isinstance(children[-1], cwast.EphemeralList):
                    if cwast.NF.CONTROL_FLOW not in children[-1].FLAGS:
                        out = handle_cfg(scopes[-1][0])
                        children += out
                scopes.pop(-1)

    if isinstance(node, cwast.StmtDefer):
        return cwast.EphemeralList([], colon=False, x_srcloc=node.x_srcloc)
    if isinstance(node, cwast.DefFun):
        scopes.pop(-1)
    return None
