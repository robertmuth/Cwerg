"""Canonicalize Misc

"""

from typing import Dict, Any

from FrontEnd import identifier
from FrontEnd import cwast
from FrontEnd import type_corpus
from FrontEnd import canonicalize_slice

############################################################
#
############################################################


def _IdNodeFromDef(def_node: cwast.DefVar, x_srcloc):
    assert def_node.type_or_auto.x_type is not None
    return cwast.Id(def_node.name, x_srcloc=x_srcloc, x_type=def_node.type_or_auto.x_type,
                    x_value=def_node.initial_or_undef_or_auto.x_value, x_symbol=def_node)


def CanonicalizeStringVal(node, str_map: Dict[str, Any], id_gen_global: identifier.IdGen):
    """Move string/array values into global (un-mutable variables)"""
    def replacer(node, _parent, _field):
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
        "args", "expr_ret", "expr_rhs", "initial_or_undef_or_auto", "value",
        "value_or_undef") and node.x_type.is_bool()


def FunCanonicalizeBoolExpressionsNotUsedForConditionals(fun: cwast.DefFun, tc: type_corpus.TypeCorpus):
    """transform a complex bool expression e into "e ? true : false"

    This will make it eligible for CanonicalizeTernaryOp which is the only way currently
    to materialize boolean values
     """
    def replacer(node, _parent, field):
        if not _ShouldBeBoolExpanded(node, field):
            return None
        cstr_bool = tc.get_bool_canon_type()
        return cwast.Expr3(node,
                           cwast.ValTrue(x_srcloc=node.x_srcloc,
                                         x_type=cstr_bool, x_value=True),
                           cwast.ValFalse(
                               x_srcloc=node.x_srcloc, x_type=cstr_bool, x_value=False),
                           x_srcloc=node.x_srcloc, x_type=node.x_type, x_value=node.x_value)

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def _RewriteExprIs(node: cwast.ExprIs, tc: type_corpus.TypeCorpus):
    src_ct: cwast.CanonType = node.expr.x_type
    dst_ct: cwast.CanonType = node.type.x_type
    typeid_ct = tc.get_typeid_canon_type()
    bool_ct = tc.get_bool_canon_type()
    sl = node.x_srcloc
    # if src_ct is not a tagged union ExprIs has been compile time evaluated
    assert src_ct.is_tagged_union()
    typeids = []
    if dst_ct.is_union():
        for ct in dst_ct.union_member_types():
            typeids.append(ct.typeid)
    else:
        typeids.append(dst_ct.typeid)
    typeidvals = [cwast.ValNum(str(i), x_srcloc=sl,
                               x_type=typeid_ct, x_value=i) for i in typeids]
    # TODO: store tag in a variable rather than retrieving it each time.
    #       Sadly, this requires ExprStmt
    tag = cwast.ExprUnionTag(node.expr, x_srcloc=sl, x_type=typeid_ct)
    tests = [cwast.Expr2(cwast.BINARY_EXPR_KIND.EQ, cwast.CloneNodeRecursively(tag, {}, {}), v,
                         x_srcloc=sl, x_type=bool_ct) for v in typeidvals]
    out = tests.pop(-1)
    while tests:
        out = cwast.Expr2(cwast.BINARY_EXPR_KIND.ORSC,
                          tests.pop(-1), out,  x_srcloc=sl, x_type=bool_ct)
    return out


def FunReplaceExprIs(fun: cwast.DefFun, tc: type_corpus.TypeCorpus):
    """Transform ExprIs comparisons for typeids"""
    def replacer(node, _parent, _field):
        if isinstance(node, cwast.ExprIs):
            return _RewriteExprIs(node, tc)

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def FunCanonicalizeTernaryOp(fun: cwast.DefFun, id_gen: identifier.IdGen):
    """Convert ternary operator nodes into expr with if statements

    Note we could implement the ternary op as a macro but would lose the ability to do
    type inference, so instead we use this hardcoded rewrite"""
    def replacer(node, _parent, _field):
        if isinstance(node, cwast.Expr3):
            srcloc = node.x_srcloc
            name_t = id_gen.NewName("op_t")
            def_t = cwast.DefVar(name_t,
                                 cwast.TypeAuto(
                                     x_srcloc=srcloc, x_type=node.x_type), node.expr_t,
                                 x_srcloc=srcloc)
            name_f = id_gen.NewName("op_f")
            def_f = cwast.DefVar(name_f, cwast.TypeAuto(x_type=node.x_type, x_srcloc=srcloc),
                                 node.expr_f, x_srcloc=srcloc)

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

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


############################################################
#
############################################################


def _AssigmemtNode(assignment_kind, lhs, expr, x_srcloc):

    rhs = cwast.Expr2(cwast.COMPOUND_KIND_TO_EXPR_KIND[assignment_kind],
                      cwast.CloneNodeRecursively(lhs, {}, {}),
                      expr, x_srcloc=x_srcloc, x_type=lhs.x_type)
    return cwast.StmtAssignment(lhs, rhs, x_srcloc=x_srcloc)


def _FixUpLhs(lhs, stmts, id_gen):
    if isinstance(lhs, cwast.Id):
        return lhs
    elif isinstance(lhs, cwast.ExprDeref):
        if isinstance(lhs.expr, cwast.Id):
            return lhs
        def_node = cwast.DefVar(id_gen.NewName("assign"),
                                cwast.TypeAuto(x_srcloc=lhs.x_srcloc,
                                               x_type=lhs.expr.x_type),
                                lhs.expr, x_srcloc=lhs.x_srcloc)
        stmts.append(def_node)
        lhs.expr = _IdNodeFromDef(def_node, lhs.x_srcloc)
        return lhs
    elif isinstance(lhs, cwast.ExprField):
        lhs.container = _FixUpLhs(lhs.container, stmts, id_gen)
        return lhs
    else:
        # note we do not need to deal with  cwast.ExprIndex because that has been lowered
        assert False


# Note, the desugaring of CompoundAssignment is made more complicated because we do not want
# just take the address of an object which would mess with the ref attribute.
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


def FunCanonicalizeCompoundAssignments(fun: cwast.DefFun, id_gen: identifier.IdGen):
    """Convert StmtCompoundAssignment to StmtAssignment"""
    def replacer(node, _parent, _field):
        if isinstance(node, cwast.StmtCompoundAssignment):
            stmts = []
            new_lhs = _FixUpLhs(node.lhs, stmts, id_gen)
            assignment = _AssigmemtNode(node.assignment_kind, new_lhs,
                                        node.expr_rhs, node.x_srcloc)
            if not stmts:
                return assignment
            stmts.append(assignment)
            return cwast.EphemeralList(stmts, colon=True)

    cwast.MaybeReplaceAstRecursively(fun, replacer)
    cwast.EliminateEphemeralsRecursively(fun)


def ReplaceConstExpr(node):
    """
     This should elminate all of ExprSizeOf and ExprOffsetOf as a side-effect
    """
    def replacer(node, _parent, field):
        if isinstance(node, cwast.EnumVal) and isinstance(node.value_or_auto, cwast.ValAuto):
            assert node.x_value is not None
        if cwast.NF.VALUE_ANNOTATED not in node.FLAGS or node.x_value is None:
            return None
        if field in ("expr_lhs", "inits_array", "inits_field"):
            return
        if isinstance(node, (cwast.DefVar, cwast.DefGlobal, cwast.ValUndef, cwast.EnumVal)):
            return

        if node.x_type.is_int() and not isinstance(node, cwast.ValNum):
            return cwast.ValNum(str(node.x_value),
                                x_srcloc=node.x_srcloc, x_type=node.x_type, x_value=node.x_value)
        if node.x_type.is_bool() and not isinstance(node, (cwast.ValTrue, cwast.ValFalse)):
            # assert False, f"unimplemented opt {node}"
            # TODO
            pass
        return None

    cwast.MaybeReplaceAstRecursively(node, replacer)


def FunCanonicalizeRemoveStmtCond(fun: cwast.DefFun):
    """Convert StmtCond to nested StmtIf"""
    def replacer(node, _parent, _field):
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

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def FunOptimizeKnownConditionals(fun: cwast.DefFun):
    """Simplify If-statements where the conditional could be evaluated

    TODO: add check for side-effects
    """
    def visit(node, _field):
        if isinstance(node, cwast.StmtIf):
            if isinstance(node.cond, cwast.ValTrue):
                node.body_f.clear()
            elif isinstance(node.cond, cwast.ValFalse):
                node.body_t.clear()
        return None

    cwast.VisitAstRecursivelyPost(fun, visit)


def _ConvertIndex(node: cwast.ExprIndex, uint_type: cwast.CanonType,
                  tc: type_corpus.TypeCorpus, srcloc):
    container_type: cwast.CanonType = node.container.x_type
    bound = None
    mut = False
    if container_type.is_array():
        bound = container_type.dim
        mut = type_corpus.is_mutable_array(node.container)
    else:
        assert container_type.is_slice()
        mut = container_type.is_mutable()
    ptr_ct = tc.insert_ptr_type(
        mut, container_type.underlying_array_or_slice_type())
    bound = cwast.ExprLen(cwast.CloneNodeRecursively(
        node.container, {}, {}), x_srcloc=srcloc, x_type=uint_type, x_value=bound)
    start_addr = cwast.ExprFront(
        node.container, x_srcloc=srcloc, x_type=ptr_ct, mut=mut)
    elem_addr = cwast.ExprPointer(
        cwast.POINTER_EXPR_KIND.INCP, start_addr, node.expr_index, bound,  x_srcloc=srcloc, x_type=start_addr.x_type)
    return cwast.ExprDeref(elem_addr, x_srcloc=srcloc,
                           x_type=node.x_type, x_value=node.x_value)


def FunReplaceExprIndex(fun: cwast.DefFun, tc: type_corpus.TypeCorpus):
    uint_type = tc.get_uint_canon_type()

    def replacer(node, _parent,  _field):
        nonlocal tc, uint_type
        if isinstance(node, cwast.ExprIndex):
            return _ConvertIndex(node, uint_type, tc, node.x_srcloc)

        return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def FunCanonicalizeDefer(fun: cwast.DefFun, scopes):
    if isinstance(fun, cwast.DefFun):
        scopes.append((fun, []))

    if isinstance(fun, cwast.StmtDefer):
        scopes[-1][1].append(fun)

    def handle_cfg(target):
        out = []
        for scope, defers in reversed(scopes):
            for defer in reversed(defers):
                clone = cwast.CloneNodeRecursively(defer, {}, {})
                out += clone.body
            if scope is target:
                break
        return out

    if cwast.NF.CONTROL_FLOW in fun.FLAGS:
        return cwast.EphemeralList(handle_cfg(fun.x_target) + [fun], colon=False)

    for field, nfd in fun.__class__.FIELDS:
        if nfd.kind is cwast.NFK.NODE:
            child = getattr(fun, field)
            new_child = FunCanonicalizeDefer(child, scopes)
            if new_child:
                setattr(fun, child, new_child)
        elif nfd.kind is cwast.NFK.LIST:
            if field in cwast.NEW_SCOPE_FIELDS:
                scopes.append((fun, []))
            children = getattr(fun, field)
            for n, child in enumerate(children):
                new_child = FunCanonicalizeDefer(child, scopes)
                if new_child:
                    children[n] = new_child
            if field in cwast.NEW_SCOPE_FIELDS:
                if children and not isinstance(children[-1], cwast.EphemeralList):
                    if cwast.NF.CONTROL_FLOW not in children[-1].FLAGS:
                        out = handle_cfg(scopes[-1][0])
                        children += out
                scopes.pop(-1)

    if isinstance(fun, cwast.StmtDefer):
        return cwast.EphemeralList([], colon=False, x_srcloc=fun.x_srcloc)
    if isinstance(fun, cwast.DefFun):
        scopes.pop(-1)
    return None


def FunAddMissingReturnStmts(fun: cwast.DefFun):
    result:  cwast.CanonType = fun.x_type.result_type()
    srcloc = fun.x_srcloc
    if not result.is_void_or_wrapped_void():
        return
    if fun.body:
        last = fun.body[-1]
        if isinstance(last, cwast.StmtReturn):
            return
        srcloc = last.x_srcloc
    void_expr = cwast.ValVoid(x_srcloc=srcloc, x_type=result)
    fun.body.append(cwast.StmtReturn(void_expr, x_srcloc=srcloc, x_target=fun))


def _HandleImplicitConversion(orig_node, target_type: cwast.CanonType, uint_type, tc):
    if orig_node.x_type.is_array() and target_type.is_slice():
        return canonicalize_slice.MakeValSliceFromArray(
            orig_node, target_type, tc, uint_type)
    elif target_type.is_union():
        sum_type = cwast.TypeAuto(
            x_type=target_type, x_srcloc=orig_node.x_srcloc)
        return cwast.ExprWiden(orig_node, sum_type, x_type=target_type,
                               x_srcloc=orig_node.x_srcloc, x_value=orig_node.x_value)
    else:
        print(
            f"@@@@@@@@@@@@@@ {orig_node.x_srcloc} {orig_node.x_type.node}  {target_type.node}")
        assert False
    return orig_node


def IsSameTypeExceptMut(src: cwast.CanonType, dst: cwast.CanonType) -> bool:
    if src is dst:
        return True
    if src.node is dst.node and src.mut and not dst.mut:
        return (src.node in (cwast.TypePtr, cwast.TypeSlice, cwast.TypeArray, cwast.TypePtr) and
                src.children[0] == dst.children[0])
    return False


def EliminateImplicitConversions(mod: cwast.DefMod, tc: type_corpus.TypeCorpus):
    uint_type: cwast.CanonType = tc.get_uint_canon_type()

    def visitor(node, _):
        nonlocal tc, uint_type

        if isinstance(node, cwast.FieldVal):
            if not isinstance(node.value_or_undef, cwast.ValUndef):
                if not IsSameTypeExceptMut(node.value_or_undef.x_type, node.x_type):
                    node.value_or_undef = _HandleImplicitConversion(
                        node.value_or_undef, node.x_type, uint_type, tc)
        elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
            initial = node.initial_or_undef_or_auto
            if not isinstance(initial, cwast.ValUndef):
                if not IsSameTypeExceptMut(initial.x_type, node.type_or_auto.x_type):
                    node.initial_or_undef_or_auto = _HandleImplicitConversion(
                        initial, node.type_or_auto.x_type, uint_type, tc)
        elif isinstance(node, cwast.ExprCall):
            fun_sig: cwast.CanonType = node.callee.x_type
            for n, (p, a) in enumerate(zip(fun_sig.parameter_types(), node.args)):
                if not IsSameTypeExceptMut(a.x_type, p):
                    node.args[n] = _HandleImplicitConversion(
                        a, p, uint_type, tc)
        elif isinstance(node, cwast.ExprWrap):
            target = node.x_type.underlying_wrapped_type()
            actual = node.expr.x_type
            if not IsSameTypeExceptMut(actual, target):
                node.expr = _HandleImplicitConversion(
                    node.expr, target, uint_type, tc)
        elif isinstance(node, cwast.StmtReturn):
            target = node.x_target
            actual = node.expr_ret.x_type
            if isinstance(target, cwast.DefFun):
                expected = target.result.x_type
            else:
                assert isinstance(target, cwast.ExprStmt)
                expected = target.x_type
            if not IsSameTypeExceptMut(actual, expected):
                node.expr_ret = _HandleImplicitConversion(
                    node.expr_ret, expected, uint_type, tc)
        elif isinstance(node, cwast.StmtAssignment):
            if not IsSameTypeExceptMut(node.expr_rhs.x_type, node.lhs.x_type):
                node.expr_rhs = _HandleImplicitConversion(
                    node.expr_rhs, node.lhs.x_type, uint_type, tc)

    cwast.VisitAstRecursivelyPost(mod, visitor)


def EliminateComparisonConversionsForTaggedUnions(fun: cwast.DefFun):
    def make_cmp(cmp: cwast.Expr2, union, field):
        """
        (== tagged_union_val member_val)

        becomes

        (&&
            (== (uniontaggedtype tagged_union_val) (typeid member_val)))
            (== (narrowto @unchecked tagged_union_val (typeof member_val)) member_val))
        """
        if cmp.binary_expr_kind == cwast.BINARY_EXPR_KIND.EQ:
            type_check = cwast.ExprIs(union, cwast.TypeAuto(
                x_srcloc=field.x_srcloc, x_type=field.x_type), x_srcloc=cmp.x_srcloc)
            if field.x_type.is_void_or_wrapped_void():
                return type_check
            # for non-ids we would need to avoid double evaluation
            assert isinstance(union, cwast.Id), f"{cmp}: {union}"
            cmp.expr1 = cwast.ExprNarrow(union, cwast.TypeAuto(
                x_srcloc=field.x_srcloc, x_type=field.x_type), unchecked=True,
                x_type=field.x_type, x_srcloc=cmp.x_srcloc)
            cmp.expr2 = field
            return cwast.Expr2(cwast.BINARY_EXPR_KIND.ANDSC, type_check, cmp,
                               x_srcloc=cmp.x_srcloc, x_type=cmp.x_type)
        else:
            assert cmp.binary_expr_kind == cwast.BINARY_EXPR_KIND.NE
            type_check = cwast.Expr1(cwast.UNARY_EXPR_KIND.NOT,
                                     cwast.ExprIs(union, cwast.TypeAuto(
                                         x_srcloc=field.x_srcloc, x_type=field.x_type), x_srcloc=cmp.x_srcloc),
                                     x_srcloc=cmp.x_srcloc, x_type=cmp.x_type)
            if field.x_type.is_void_or_wrapped_void():
                return type_check
            cmp.expr1 = cwast.ExprNarrow(union, cwast.TypeAuto(
                x_srcloc=field.x_srcloc, x_type=field.x_type), unchecked=True,
                x_type=field.x_type, x_srcloc=cmp.x_srcloc)
            cmp.expr2 = field
            return cwast.Expr2(cwast.BINARY_EXPR_KIND.ORSC, type_check, cmp,
                               x_srcloc=cmp.x_srcloc, x_type=cmp.x_type)

    def replacer(node, _parent, _field):

        if not isinstance(node, cwast.Expr2):
            return None

        if node.binary_expr_kind not in (cwast.BINARY_EXPR_KIND.EQ, cwast.BINARY_EXPR_KIND.NE):
            return None
        if node.expr1.x_type.is_tagged_union():
            return make_cmp(node, node.expr1, node.expr2)
        if node.expr2.x_type.is_tagged_union():
            return make_cmp(node, node.expr2, node.expr1)

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def FunReplaceTypeOfAndTypeSumDelta(fun: cwast.DefFun):
    def replacer(node, _parent, _field):
        if not isinstance(node, (cwast.TypeOf, cwast.TypeUnionDelta)):
            return None
        return cwast.TypeAuto(x_srcloc=node.x_srcloc, x_type=node.x_type)

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)
