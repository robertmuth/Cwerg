"""Canonicalize Misc

"""
from typing import Any, Optional


from FE import cwast
from FE import type_corpus
from FE import eval
from FE import typify

############################################################
#
############################################################


def _DoesFunSigNeedReplacementType(fun_sig: cwast.CanonType) -> bool:
    if fun_sig.result_type().replacement_type is not None:
        return True
    for p in fun_sig.parameter_types():
        if p.replacement_type is not None:
            return True
    return False


def MaybeMakeFunSigReplacementType(fun_sig: cwast.CanonType,
                                   tc: type_corpus.TypeCorpus) -> Optional[cwast.CanonType]:
    if not _DoesFunSigNeedReplacementType(fun_sig):
        return None

    def new_or_old(ct: cwast.CanonType) -> cwast.CanonType:
        if ct.replacement_type:
            return ct.replacement_type
        return ct

    assert fun_sig.is_fun()
    result = new_or_old(fun_sig.result_type())
    params = [new_or_old(p) for p in fun_sig.parameter_types()]
    return tc.InsertFunType(params, result)


def MakeDefRec(name: str, fields_desc, tc: type_corpus.TypeCorpus, srcloc) -> cwast.DefRec:
    fields = []
    for field_name, field_ct in fields_desc:
        field_type = cwast.TypeAuto(x_srcloc=srcloc, x_type=field_ct)
        fields.append(cwast.RecField(
            field_name, field_type, x_srcloc=srcloc, x_type=field_ct))
    rec = cwast.DefRec(cwast.NAME.Make(
        name), fields, pub=True, x_srcloc=srcloc)
    rec_ct: cwast.CanonType = tc.InsertRecType(f"{name}", rec)
    typify.AnnotateNodeType(rec, rec_ct)
    return rec


def _IdNodeFromDef(def_node: cwast.DefVar, x_srcloc):
    assert def_node.type_or_auto.x_type is not None
    return cwast.Id(def_node.name, None, x_srcloc=x_srcloc, x_type=def_node.type_or_auto.x_type,
                    x_eval=def_node.initial_or_undef_or_auto.x_eval, x_symbol=def_node)


def IdNodeFromRecField(recfield: cwast.RecField, srcloc):
    return cwast.Id(recfield.name, None, x_srcloc=srcloc, x_type=recfield.x_type,
                    x_symbol=recfield)


def _ShouldBeBoolExpanded(node, parent):
    # these nodes do not represent a complex boolean expression
    if not isinstance(node, (cwast.Expr1, cwast.Expr2)):
        return False
    # the field condition ensures that the node
    # * is not part of a conditional
    # * has a x_type
    return node.x_type.is_bool() and isinstance(parent, cwast.TOP_LEVEL_EXPRESSION_NODES)


def FunCanonicalizeBoolExpressionsNotUsedForConditionals(fun: cwast.DefFun):
    """transform a complex bool expression e into "e ? true : false"

    This will make it eligible for CanonicalizeTernaryOp which is the only way currently
    to materialize boolean values. All other boolean expressions are assumed to be part
    of conditionals and are converrted directly to jumps in the IR.
     """
    def replacer(node, parent):
        if not _ShouldBeBoolExpanded(node, parent):
            return None
        ct_bool = node.x_type
        return cwast.Expr3(node,
                           cwast.ValNum(eval.EVAL_STR, x_srcloc=node.x_srcloc,
                                        x_type=ct_bool, x_eval=eval.VAL_TRUE),
                           cwast.ValNum(eval.EVAL_STR, x_srcloc=node.x_srcloc,
                                        x_type=ct_bool, x_eval=eval.VAL_FALSE),
                           x_srcloc=node.x_srcloc, x_type=ct_bool, x_eval=node.x_eval)

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def _RewriteExprIs(node: cwast.ExprIs, typeid_ct: cwast.CanonType):
    src_ct: cwast.CanonType = node.expr.x_type
    dst_ct: cwast.CanonType = node.type.x_type
    bool_ct = node.x_type
    sl = node.x_srcloc
    # if src_ct is not a tagged union ExprIs has been compile time evaluated
    if not src_ct.is_union():
        val = src_ct == dst_ct or dst_ct.is_union() and dst_ct.union_contains(src_ct)
        return cwast.ValNum(eval.EVAL_STR, x_srcloc=sl, x_type=bool_ct, x_eval=eval.VAL_TRUE if val else eval.VAL_FALSE)

    assert not src_ct.untagged, f"{node.x_srcloc} {src_ct} {dst_ct}"

    typeids = []
    if dst_ct.is_union():
        for ct in dst_ct.union_member_types():
            if src_ct.union_contains(ct):
                typeids.append(ct.get_original_typeid())
    else:
        typeids.append(dst_ct.get_original_typeid())

    tag = cwast.ExprUnionTag(node.expr, x_srcloc=sl, x_type=typeid_ct)

    # TODO: store tag in a variable rather than retrieving/cloning it each time.
    #       Sadly, this requires ExprStmt
    def MakeTypeIdTest(typeid: int, tag) -> cwast.Expr2:
        val = cwast.ValNum(eval.EVAL_STR, x_srcloc=sl, x_type=typeid_ct,
                           x_eval=eval.EvalNum(typeid, typeid_ct.base_type_kind))
        return cwast.Expr2(cwast.BINARY_EXPR_KIND.EQ, tag, val, x_srcloc=sl, x_type=bool_ct)

    assert len(typeids) > 0, "expected at least one typeid"
    out = MakeTypeIdTest(typeids.pop(-1), tag)
    while typeids:
        assert IsNodeCopyableWithoutRiskOfSideEffects(
            tag.expr), f"{tag.expr} at {node.x_srcloc}"
        next_test = MakeTypeIdTest(
            typeids.pop(-1), cwast.CloneNodeRecursively(tag, {}, {}))
        out = cwast.Expr2(cwast.BINARY_EXPR_KIND.ORSC,
                          next_test, out,  x_srcloc=sl, x_type=bool_ct)
    return out


def FunDesugarExprIs(fun: cwast.DefFun, tc: type_corpus.TypeCorpus):
    """Transform ExprIs comparisons for typeids"""
    def replacer(node, _parent):
        if isinstance(node, cwast.ExprIs):
            return _RewriteExprIs(node, tc)

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def FunDesugarExpr3(fun: cwast.DefFun):
    """Convert ternary operator nodes into expr with if statements

    Note we could implement the ternary op as a macro but would lose the ability to do
    type inference, so instead we use this hardcoded rewrite"""
    def replacer(node, _parent):
        if not isinstance(node, cwast.Expr3):
            return None
        sl = node.x_srcloc
        #
        expr = cwast.ExprStmt([], x_srcloc=sl,
                              x_type=node.x_type, x_eval=node.x_eval)
        #
        val_t = node.expr_t
        if not isinstance(val_t,  (cwast.ValNum, cwast.Id)):
            at = cwast.TypeAuto(x_srcloc=sl, x_type=node.x_type)
            def_t = cwast.DefVar(cwast.NAME.Make("expr3_t"), at,
                                 node.expr_t, x_srcloc=sl, x_type=node.x_type)
            val_t = _IdNodeFromDef(def_t, sl)
            expr.body.append(def_t)
        #
        val_f = node.expr_f
        if not isinstance(val_f,  (cwast.ValNum, cwast.Id)):
            at = cwast.TypeAuto(x_srcloc=sl, x_type=node.x_type)
            def_f = cwast.DefVar(cwast.NAME.Make("expr3_f"), at,
                                 node.expr_f, x_srcloc=sl, x_type=node.x_type)
            val_f = _IdNodeFromDef(def_f, sl)
            expr.body.append(def_f)

        expr.body.append(
            cwast.StmtIf(node.cond, [
                cwast.StmtReturn(val_t, x_srcloc=sl, x_target=expr)
            ], [
                cwast.StmtReturn(val_f, x_srcloc=sl, x_target=expr)
            ],  x_srcloc=sl))

        return expr

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def _DefVarNew(name, init) -> Any:
    sl = init.x_srcloc
    at = cwast.TypeAuto(x_srcloc=sl, x_type=init.x_type)
    return cwast.DefVar(name, at, init, x_srcloc=sl, x_type=init.x_type)

############################################################
#
############################################################


def MakeNodeCopyableWithoutRiskOfSideEffects(lhs, stmts: list[Any], is_lhs: bool):
    """Ensures that the node has one of the following shapes:
    1) Id
    2) (^ Id)
    3) (. Id field_name)
    4) (. (^ Id) field_name)
    5) (. (. (...)))  where the innermost expression s 3) or 4)

    This is advantageous because we can now clone this node without having to worry about
    changing the semantics of the program.

    Note:

    * we do not have to deal with ExprIndex because that has been eliminated by
    FunReplaceExprIndex() and now looks like (^ expr)

    * this may create additional statements which will be added to stmts.
    """

    if isinstance(lhs, cwast.Id):
        return lhs
    elif isinstance(lhs, cwast.ExprDeref):
        if isinstance(lhs.expr, cwast.Id):
            return lhs
        pointer = lhs.expr
        def_node = _DefVarNew(cwast.NAME.Make("deref_assign"), pointer)
        stmts.append(def_node)
        lhs.expr = _IdNodeFromDef(def_node, pointer.x_srcloc)
        return lhs
    elif isinstance(lhs, cwast.ExprField):
        lhs.container = MakeNodeCopyableWithoutRiskOfSideEffects(
            lhs.container, stmts, is_lhs)
        return lhs
    elif isinstance(lhs, cwast.ExprIndex):
        # note we do not need to deal with  cwast.ExprIndex because that has been lowered
        # much earlier to a cwast.ExprDeref
        assert False, "this should have been eliminated by FunReplaceExprIndex()"
    else:
        assert not is_lhs
        def_node = _DefVarNew(cwast.NAME.Make("assign"), lhs)
        stmts.append(def_node)
        return _IdNodeFromDef(def_node, lhs.x_srcloc)


# this is not a very accurate analysis erring on the side of safety
def IsNodeCopyableWithoutRiskOfSideEffects(node) -> bool:
    if isinstance(node, cwast.Id):
        return True
    elif isinstance(node, cwast.ExprDeref):
        return isinstance(node.expr, cwast.Id)
    elif isinstance(node, cwast.ExprField):
        c = node.container
        while True:
            if isinstance(c, cwast.ExprField):
                c = c.container
            elif isinstance(c, cwast.Id):
                return True
            else:
                return isinstance(c, cwast.ExprDeref) and isinstance(c.expr, cwast.Id)
    else:
        return False


def FunMakeCertainNodeCopyableWithoutRiskOfSideEffects(
        fun: cwast.DefFun):
    """Currently unused """
    def replacer(node):
        if isinstance(node, cwast.ExprDeref):
            if isinstance(node.expr, cwast.Id):
                return None
            sl = node.x_srcloc
            at = cwast.TypeAuto(x_srcloc=sl, x_type=node.expr.x_type)
            def_node = cwast.DefVar(cwast.NAME.Make("assign"),
                                    at,
                                    node.expr, x_srcloc=sl, x_type=at.x_type)
            node.expr = _IdNodeFromDef(def_node, node.x_srcloc)
            return [def_node, node]
        elif isinstance(node, cwast.ExprField):
            c = node.container
            if isinstance(c, cwast.Id):
                return None
            elif isinstance(c, cwast.ExprField):
                # post order traversal
                return None
            elif isinstance(c, cwast.ExprDeref):
                # we have a post-order traversal so the deref shouls have been handles already
                return None
            else:
                # handle this like we did for ExprDeref
                assert False
        else:
            assert not isinstance(node, cwast.ExprIndex)
            return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def _AssigmemtNode(assignment_kind, lhs, expr, x_srcloc):
    assert assignment_kind.IsArithmetic()
    rhs = cwast.Expr2(assignment_kind,
                      cwast.CloneNodeRecursively(lhs, {}, {}),
                      expr, x_srcloc=x_srcloc, x_type=lhs.x_type)
    return cwast.StmtAssignment(lhs, rhs, x_srcloc=x_srcloc)


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
#    return [def_node, new_assignment]
#


def FunCanonicalizeCompoundAssignments(fun: cwast.DefFun):
    """Convert StmtCompoundAssignment to StmtAssignment"""
    def replacer(node):
        if isinstance(node, cwast.StmtCompoundAssignment):
            stmts = []
            new_lhs = MakeNodeCopyableWithoutRiskOfSideEffects(
                node.lhs, stmts, True)
            assert IsNodeCopyableWithoutRiskOfSideEffects(
                new_lhs), f"{new_lhs}"
            assignment = _AssigmemtNode(node.binary_expr_kind,
                                        new_lhs, node.expr_rhs, node.x_srcloc)
            if not stmts:
                return assignment
            stmts.append(assignment)
            return stmts

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def FunReplaceConstExpr(node: cwast.DefFun, tc: type_corpus.TypeCorpus):
    """
    Try to convert as many Nodes to ValNum as possible

    This should elminate all of ExprSizeOf and ExprOffsetOf as a side-effect
    """
    def replacer(node, parent) -> Any:
        if cwast.NF.EVAL_ANNOTATED not in node.FLAGS:
            return None

        val = node.x_eval
        if not isinstance(val, eval.EvalNum):
            return None

        if isinstance(node, (cwast.DefVar, cwast.DefGlobal, cwast.ValPoint, cwast.ValCompound,
                             cwast.ValNum, cwast.EnumVal, cwast.ValUndef)):
            return None
        if isinstance(parent, cwast.ExprAddrOf) and node is parent.expr_lhs:
            # for the case of "@id" we do not want to replace id by its value
            return None

        ct: cwast.CanonType = node.x_type.get_unwrapped()
        if ct.is_base_type():
            ct = node.x_type
        else:
            val_ct = tc.get_base_canon_type(val.kind)
            assert ct.is_union() and ct.union_contains(val_ct), f"{ct}"
            # assert False, f"@@@@@@@@@@@ {node.x_srcloc}"
            ct = val_ct
        return cwast.ValNum(eval.EVAL_STR, x_srcloc=node.x_srcloc, x_type=ct, x_eval=val)

    # no neeed to siplify interior subtrees if we we rewrite a node
    cwast.MaybeReplaceAstRecursively(node, replacer)


def FunCanonicalizeRemoveStmtCond(fun: cwast.DefFun):
    """Convert StmtCond to nested StmtIf"""
    def replacer(node, _parent):
        if not isinstance(node, cwast.StmtCond):
            return None
        if not node.cases:
            return []

        out = None
        for case in reversed(node.cases):
            assert isinstance(case, cwast.Case)
            out = cwast.StmtIf(case.cond, case.body, [] if out is None else [
                out], x_srcloc=case.x_srcloc)
        return out

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def FunOptimizeKnownConditionals(fun: cwast.DefFun):
    """Simplify If-statements where the conditional could be evaluated

    TODO: add check for side-effects
    """
    def visit(node):
        if isinstance(node, cwast.StmtIf):
            if isinstance(node.cond, cwast.ValNum):
                assert isinstance(
                    node.cond.x_eval, eval.EvalNum), f"{node.cond.x_eval} {node.cond}"
                if node.cond.x_eval.val:
                    node.body_f.clear()
                else:
                    node.body_t.clear()
        return None

    cwast.VisitAstRecursivelyPost(fun, visit)


def _CovertExprIndexToExprPoiner(container: cwast.Id, expr_index, bound, mut: bool,
                                 sl, elem_ct, tc: type_corpus.TypeCorpus):
    ptr_ct = tc.InsertPtrType(mut, elem_ct)
    start_addr = cwast.ExprFront(
        container, x_srcloc=sl, x_type=ptr_ct, mut=mut)
    return cwast.ExprPointer(
        cwast.POINTER_EXPR_KIND.INCP, start_addr, expr_index, bound,  x_srcloc=sl, x_type=ptr_ct)


def _RewriteExprIndex(node: cwast.ExprIndex, uint_type: cwast.CanonType,
                      tc: type_corpus.TypeCorpus) -> Any:
    # TODO: handle unchecked case
    container_ct: cwast.CanonType = node.container.x_type
    elem_ct = container_ct.underlying_type()
    sl = node.x_srcloc
    if container_ct.is_vec():
        mut = type_corpus.IsProperLhs(node.container)
        dim_eval = eval.EvalNum(container_ct.dim, uint_type.base_type_kind)
        bound = cwast.ValNum(eval.EVAL_STR, x_srcloc=sl,
                             x_type=uint_type, x_eval=dim_eval)
        pinc = _CovertExprIndexToExprPoiner(
            node.container, node.expr_index, bound, mut, sl, elem_ct, tc)
        return cwast.ExprDeref(pinc,  x_srcloc=sl, x_type=elem_ct, x_eval=node.x_eval)
    else:
        assert container_ct.is_span()
        mut = container_ct.is_mutable()
        if isinstance(node.container, cwast.Id):
            bound: Any = cwast.ExprLen(cwast.CloneNodeRecursively(
                node.container, {}, {}), x_srcloc=sl, x_type=uint_type)
            # TODO
            # Node_x_eval = ...
            pinc = _CovertExprIndexToExprPoiner(
                node.container, node.expr_index, bound, mut, sl, elem_ct, tc)
            return cwast.ExprDeref(pinc, x_srcloc=sl, x_type=elem_ct, x_eval=node.x_eval)
        else:
            # we materialize the container to avoid evaluating it twice
            at = cwast.TypeAuto(x_srcloc=sl, x_type=container_ct)
            new_var = cwast.DefVar(cwast.NAME.Make("val_span_tmp"), at, node.container,
                                   x_srcloc=sl, x_type=container_ct)
            bound: Any = cwast.ExprLen(_IdNodeFromDef(
                new_var, sl), x_srcloc=sl, x_type=uint_type)
            pinc = _CovertExprIndexToExprPoiner(_IdNodeFromDef(
                new_var, sl), node.expr_index, bound, mut, sl, elem_ct, tc)
            expr = cwast.ExprStmt([], sl, pinc.x_type)
            stmt_ret = cwast.StmtReturn(pinc, x_srcloc=sl, x_target=expr)
            expr.body = [new_var, stmt_ret]
            return cwast.ExprDeref(expr, x_srcloc=sl, x_type=elem_ct, x_eval=node.x_eval)


def FunReplaceExprIndex(fun: cwast.DefFun, tc: type_corpus.TypeCorpus):
    """convert index expr into pointer arithmetic"""
    uint_ct: cwast.CanonType = tc.get_uint_canon_type()

    def replacer(node, _parent):
        nonlocal tc, uint_ct
        if isinstance(node, cwast.ExprIndex):
            return _RewriteExprIndex(node, uint_ct, tc)

        return None

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


# TODO: try converting this to VisitAstRecursivelyPreAndPost
def _EliminateDeferRecursively(node: Any, scopes: list[tuple[Any, list[Any]]]):

    def handle_cfg(target):
        out = []
        for scope, defers in reversed(scopes):
            for defer in reversed(defers):
                clone = cwast.CloneNodeRecursively(defer, {}, {})
                out += clone.body
            if scope is target:
                break
        for x in out:
            assert not isinstance(x, cwast.StmtDefer)
        return out

    if isinstance(node, cwast.StmtDefer):
        scopes[-1][1].append(node)

    if cwast.NF.TARGET_ANNOTATED in node.FLAGS:
        # inject the defer bodies just before the control flow change
        return handle_cfg(node.x_target) + [node]

    for nfd in node.__class__.NODE_FIELDS:
        field = nfd.name
        if nfd.kind is cwast.NFK.NODE:
            child = getattr(node, field)
            new_child = _EliminateDeferRecursively(child, scopes)
            assert new_child is None
            if new_child:
                assert not isinstance(new_child, list)
                setattr(node, child, new_child)
        else:
            if field in cwast.NEW_SCOPE_FIELDS:
                scopes.append((node, []))
            #
            children = getattr(node, field)
            new_children = []
            change = False
            for n, child in enumerate(children):
                new_child = _EliminateDeferRecursively(child, scopes)
                if new_child is None:
                    new_children.append(child)
                else:
                    assert isinstance(new_child, list)
                    new_children += new_child
                    change = True

            #
            if field in cwast.NEW_SCOPE_FIELDS:
                # handle end of scope if the last statement was NOT a control flow change
                if not new_children or cwast.NF.TARGET_ANNOTATED not in children[-1].FLAGS:
                    out = handle_cfg(scopes[-1][0])
                    if out:
                        new_children += out
                        change = True
                scopes.pop(-1)
            #
            if change:
                setattr(node, field, new_children)

    if isinstance(node, cwast.StmtDefer):
        return []
    return None


def FunEliminateDefer(fun: cwast.DefFun):
    _EliminateDeferRecursively(fun, [])


def FunAddMissingReturnStmts(fun: cwast.DefFun):
    result_ct = fun.x_type.result_type()
    if not result_ct.get_unwrapped().is_void():
        return

    sl = fun.x_srcloc
    if fun.body:
        last = fun.body[-1]
        if isinstance(last, cwast.StmtReturn):
            return
        sl = last.x_srcloc
    void_expr = cwast.ValVoid(x_srcloc=sl, x_type=result_ct)

    fun.body.append(cwast.StmtReturn(void_expr, x_srcloc=sl, x_target=fun))


def _GetFrontTypeForVec(ct: cwast.CanonType, tc) -> cwast.CanonType:
    return tc.InsertPtrType(ct.mut, ct.underlying_type())


def _MakeValSpanFromArray(node, expected_ct: cwast.CanonType,
                          uint_type: cwast.CanonType, tc: type_corpus.TypeCorpus) -> cwast.ValSpan:
    assert node.x_type.is_vec() and expected_ct.is_span()
    ptr_ct = _GetFrontTypeForVec(expected_ct, tc)
    sym = node.x_symbol if isinstance(node, cwast.Id) else None

    # assert not isinstance(node, (cwast.ValCompound, cwast.ValString)), f"{node.x_srcloc}"
    front = cwast.ExprFront(
        node, x_srcloc=node.x_srcloc, mut=expected_ct.mut, x_type=ptr_ct,
        x_eval=eval.EvalSymAddr(sym) if sym else None)
    dim = node.x_type.array_dim()
    length = cwast.ValNum(eval.EVAL_STR, x_eval=eval.EvalNum(dim, uint_type.base_type_kind),
                          x_srcloc=node.x_srcloc, x_type=uint_type)
    # TODO: propagate content for mut=false
    v_span = eval.EvalSpan(sym if sym else None, dim, None)
    return cwast.ValSpan(front, length, x_srcloc=node.x_srcloc, x_type=expected_ct, x_eval=v_span)


def _MaybeMakeImplicitConversionExplicit(orig_node, expected_ct: cwast.CanonType, uint_type, tc):
    if isinstance(orig_node, cwast.ValUndef):
        return orig_node
    orig_type = orig_node.x_type
    if orig_type is expected_ct or type_corpus.IsDropMutConversion(orig_type, expected_ct):
        # no change
        return orig_node

    if orig_node.x_type.is_vec() and expected_ct.is_span():
        return _MakeValSpanFromArray(
            orig_node, expected_ct, uint_type, tc)
    else:
        assert expected_ct.is_union()
        sum_type = cwast.TypeAuto(
            x_type=expected_ct, x_srcloc=orig_node.x_srcloc)
        return cwast.ExprWiden(orig_node, sum_type, x_type=expected_ct,
                               x_srcloc=orig_node.x_srcloc, x_eval=orig_node.x_eval)


def FunMakeImplicitConversionsExplicit(fun: cwast.DefFun, tc: type_corpus.TypeCorpus):
    uint_type: cwast.CanonType = tc.get_uint_canon_type()

    def visitor(node: Any):
        nonlocal tc, uint_type

        if isinstance(node, cwast.ValPoint):
            node.value_or_undef = _MaybeMakeImplicitConversionExplicit(
                node.value_or_undef, node.x_type, uint_type, tc)
        elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
            node.initial_or_undef_or_auto = _MaybeMakeImplicitConversionExplicit(
                node.initial_or_undef_or_auto, node.type_or_auto.x_type, uint_type, tc)
        elif isinstance(node, cwast.ExprCall):
            fun_sig: cwast.CanonType = node.callee.x_type
            for n, (ct, a) in enumerate(zip(fun_sig.parameter_types(), node.args)):
                node.args[n] = _MaybeMakeImplicitConversionExplicit(
                    a, ct, uint_type, tc)
        elif isinstance(node, cwast.ExprWrap) and not node.x_type.is_enum():
            assert node.x_type.is_wrapped()
            node.expr = _MaybeMakeImplicitConversionExplicit(
                node.expr, node.x_type.underlying_type(), uint_type, tc)

        elif isinstance(node, cwast.StmtReturn):
            expected_ct = node.x_target
            if isinstance(expected_ct, cwast.DefFun):
                expected_ct = expected_ct.result.x_type
            else:
                assert isinstance(expected_ct, cwast.ExprStmt)
                expected_ct = expected_ct.x_type
            node.expr_ret = _MaybeMakeImplicitConversionExplicit(
                node.expr_ret, expected_ct, uint_type, tc)
        elif isinstance(node, cwast.StmtAssignment):
            node.expr_rhs = _MaybeMakeImplicitConversionExplicit(
                node.expr_rhs, node.lhs.x_type, uint_type, tc)

    cwast.VisitAstRecursivelyPost(fun, visitor)


def _CloneId(node: cwast.Id) -> cwast.Id:
    assert isinstance(node, cwast.Id)
    return cwast.Id(node.name, None, x_symbol=node.x_symbol, x_type=node.x_type,
                    x_srcloc=node.x_srcloc)


def _MakeTagCheck(union_id: cwast.Id, ct: cwast.CanonType, ct_bool: cwast.CanonType, sl) -> Any:
    type_expr = cwast.TypeAuto(x_srcloc=sl, x_type=ct)
    return cwast.ExprIs(union_id, type_expr, x_srcloc=sl, x_type=ct_bool)


def _MakeUnionNarrow(union_id: cwast.Id, ct: cwast.CanonType, sl) -> Any:
    type_expr = cwast.TypeAuto(x_srcloc=sl, x_type=ct)
    return cwast.ExprNarrow(union_id, type_expr, unchecked=True, x_type=ct, x_srcloc=sl)


def FunDesugarTaggedUnionComparisons(fun: cwast.DefFun):
    def make_cmp(cmp: cwast.Expr2, union: Any, field: Any, kind) -> Any:
        """
        (== tagged_union_val member_val)

        becomes

        (&&
            (== (uniontaggedtype tagged_union_val) (typeid member_val)))
            (== (narrowto @unchecked tagged_union_val (typeof member_val)) member_val))

        Note: tagged unions can only be compared to scalars
        """
        # TODO: for non-ids we would need to avoid double evaluation
        assert isinstance(union, cwast.Id), f"{cmp}: {union}"
        ct_field: cwast.CanonType = field.x_type
        ct_bool: cwast.CanonType = cmp.x_type
        sl = cmp.x_srcloc
        tag_check = _MakeTagCheck(union, ct_field, ct_bool, sl)
        if kind == cwast.BINARY_EXPR_KIND.EQ:
            if ct_field.get_unwrapped().is_void():
                return tag_check

            cmp.expr1 = _MakeUnionNarrow(_CloneId(union), ct_field, sl)
            cmp.expr2 = field
            return cwast.Expr2(cwast.BINARY_EXPR_KIND.ANDSC, tag_check, cmp,
                               x_srcloc=sl, x_type=ct_bool)
        else:
            assert kind == cwast.BINARY_EXPR_KIND.NE
            tag_check = cwast.Expr1(cwast.UNARY_EXPR_KIND.NOT,
                                    tag_check, x_srcloc=sl, x_type=ct_bool)
            if field.x_type.get_unwrapped().is_void():
                return tag_check
            cmp.expr1 = _MakeUnionNarrow(_CloneId(union), ct_field, sl)
            cmp.expr2 = field
            return cwast.Expr2(cwast.BINARY_EXPR_KIND.ORSC, tag_check, cmp,
                               x_srcloc=sl, x_type=ct_bool)

    def replacer(node, _parent):

        if not isinstance(node, cwast.Expr2):
            return None

        kind = node.binary_expr_kind
        if kind not in (cwast.BINARY_EXPR_KIND.EQ, cwast.BINARY_EXPR_KIND.NE):
            return None
        if node.expr1.x_type.is_tagged_union():
            return make_cmp(node, node.expr1, node.expr2, kind)
        if node.expr2.x_type.is_tagged_union():
            return make_cmp(node, node.expr2, node.expr1, kind)

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def FunReplaceTypeOfAndTypeUnionDelta(fun: cwast.DefFun):
    def replacer(node, _parent):
        if not isinstance(node, (cwast.TypeOf, cwast.TypeUnionDelta)):
            return None
        return cwast.TypeAuto(x_srcloc=node.x_srcloc, x_type=node.x_type)

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def _IsSimpleInitializer(expr) -> bool:
    if isinstance(expr, (cwast.ValUndef, cwast.ValNum, cwast.ValVoid, cwast.Id)):
        return True
    elif isinstance(expr, (cwast.ExprWiden,  cwast.ExprBitCast, cwast.ExprWrap,
                           cwast.ExprUnwrap, cwast.ExprAs)):
        return _IsSimpleInitializer(expr.expr)
    else:
        return False


def FunReplaceSpanCastWithSpanVal(node, tc: type_corpus.TypeCorpus):
    """Eliminate Array to Span casts. """
    uint_type: cwast.CanonType = tc.get_uint_canon_type()

    def replacer(node, _parent):
        nonlocal tc, uint_type
        if (isinstance(node, cwast.ExprAs) and
            node.x_type != node.expr.x_type and
                node.x_type.is_span() and
                node.expr.x_type.is_vec()):
            return _MakeValSpanFromArray(
                node.expr, node.x_type, tc, uint_type)
        return None

    cwast.MaybeReplaceAstRecursivelyWithParentPost(node, replacer)


def FunRewriteComplexAssignments(fun: cwast.DefFun, tc: type_corpus.TypeCorpus):
    """Rewrite assignments of recs (including unions and spans) and arrays

    to ensure correctness.
    Consider:

    let a_record MyRec = ...
    set a_record = MyRec{ foo(&a_record), baz(&a_record) }

    A naive code generator might translate the assignment like:
    set a_record . field1 = foo(&a_record)
    set a_record . field2 = baz(&a_record)

    This make the call to baz potentially incorrect
    This phase will rewrite problematic assignments like the one above to:

    let tmp_field1 = foo(&a_record)
    let tmp_field2 = baz(&a_record)
    set a_record = MyRec{ tmp_field1, tmp_field2 }


    Another approach is to rewrite this as:
    let tmp = MyRec{ foo(&a_record), baz(&a_record) }
    set a_record = tmp

    We reject this approach because it forces another stack variable: tmp.
    """
    def replacer(node):
        if not isinstance(node, cwast.StmtAssignment):
            return None

        rhs = node.expr_rhs
        if isinstance(rhs, cwast.ValCompound):
            extra = []
            for i in rhs.inits:
                if not _IsSimpleInitializer(i.value_or_undef):
                    sl = i.x_srcloc
                    at = cwast.TypeAuto(x_srcloc=sl, x_type=i.x_type)
                    def_tmp = cwast.DefVar(cwast.NAME.Make("val_array_tmp"),
                                           at, i.value_or_undef,
                                           x_srcloc=sl, x_type=at.x_type)
                    extra.append(def_tmp)
                    i.value_or_undef = _IdNodeFromDef(def_tmp, sl)
                    # assert False, f"{i.value_or_undef} {i.x_type}"
            if not extra:
                return None
            extra.append(node)
            return extra
        else:
            return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def FunRemoveParentheses(fun: Any):
    def replacer(node, _parent):
        if isinstance(node, cwast.ExprParen):
            return node.expr
        return None

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def FunRemoveUselessCast(fun):
    def replacer(node, _parent):
        if isinstance(node, cwast.ExprAs):
            if node.x_type is node.expr.x_type:
                return node.expr
        return None

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)
