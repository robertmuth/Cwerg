#!/usr/bin/python3

"""Translator from AST to Cwerg IR

"""

import sys
import logging

from typing import List, Dict, Set, Optional, Union, Any, Tuple


from FrontEnd import canonicalize
from FrontEnd import symbolize
from FrontEnd import types
from FrontEnd import cwast
from FrontEnd import typify
from FrontEnd import eval
from FrontEnd import identifier
from FrontEnd import parse
from FrontEnd import pp

from Util.parse import BytesToEscapedString


logger = logging.getLogger(__name__)

TAB = "  "

ZEROS = b"\0" * 1024


def _InitDataForBaseType(x_type, x_value) -> bytes:
    assert isinstance(x_type, cwast.TypeBase)
    byte_width = x_type.x_size
    if x_value is None or isinstance(x_value, cwast.ValUndef):
        return ZEROS[0:byte_width]
    elif types.is_int(x_type):
        return x_value.to_bytes(byte_width, 'little')
    assert False


def RenderList(items):
    return "[" + " ".join(items) + "]"


def StringifyOneType(node, type_corpus: types.TypeCorpus):
    t = type_corpus.register_types(node)
    assert len(t) == 1
    return t[0]


def _EmitFunctionHeader(fun: cwast.DefFun, type_corpus: types.TypeCorpus):
    sig: cwast.TypeFun = fun.x_type
    ins = []
    for p in sig.params:
        ins += type_corpus.register_types(p.type)
    print(
        f"\n\n.fun {fun.name} NORMAL [{StringifyOneType(sig.result, type_corpus)}] = [{' '.join(ins)}]")


def _EmitFunctionProlog(fun: cwast.DefFun, type_corpus: types.TypeCorpus,
                        id_gen: identifier.IdGen):
    print(f".bbl {id_gen.NewName('entry')}")
    for p in fun.params:
        p.name = id_gen.NewName(p.name)
        reg_types = type_corpus.register_types(p.type.x_type)
        if len(reg_types) == 1:
            print(f"{TAB}poparg {p.name}:{reg_types[0]}")
        else:
            assert len(reg_types) == 2
            print(f"{TAB}poparg {p.name}.1:{reg_types[0]}")
            print(f"{TAB}poparg {p.name}.2:{reg_types[1]}")


def RLE(data: bytes):
    last = None
    count = 0
    for d in data:
        if d != last:
            if last is not None:
                yield count, last
            last = d
            count = 1
        else:
            count += 1
    else:
        yield count, last


def _EmitMem(name, align, rw, data):
    print(f"\n.mem {name} {align} {'RW' if rw else 'RO'}")
    if isinstance(data, bytes):
        if len(data) < 100:
            print(f'.data 1 "{BytesToEscapedString(data)}"')
        else:
            for count, value in RLE(data):
                print(f".data {count} [{value}]")
    else:
        assert False


ZERO_INDEX = "0"


def _GetLValueAddress(node, tc: types.TypeCorpus, id_gen: identifier.IdGen) -> Any:
    if isinstance(node, cwast.ExprIndex):
        x_type = node.container.x_type
        assert isinstance(x_type, cwast.TypeArray), f"{x_type}"
        container = _GetLValueAddress(node.container, tc, id_gen)
        if node.expr_index.x_value == 0:
            return container
        else:
            index = EmitIRExpr(node.expr_index, tc, id_gen)
            if x_type.type.x_size == 1:
                res = id_gen.NewName("at")
                kind = "A64"
                print(f"{TAB}lea {res}:{kind} = {container} {index}")
                return res
            else:
                assert False
    elif isinstance(node, cwast.ExprDeref):
        return EmitIRExpr(node.expr, tc, id_gen)
    elif isinstance(node, cwast.ExprField):
        assert False
    elif isinstance(node, cwast.Id):
        name = node.x_symbol.name
        res = id_gen.NewName("lhsaddr")
        # TODO
        kind = "A64"
        print(f"{TAB}lea.mem {res}:{kind} = {name} 0")
        return res
    else:
        assert False, f"unsupported node for lvalue {node}"


_MAP_COMPARE = {
    cwast.BINARY_EXPR_KIND.NE: "bne",
    cwast.BINARY_EXPR_KIND.EQ: "beq",
    cwast.BINARY_EXPR_KIND.LT: "blt",
    cwast.BINARY_EXPR_KIND.LE: "ble",
}


def EmitIRConditional(cond, label_t: str, label_f: str, id_gen: identifier.IdGen):
    if isinstance(cond, cwast.Expr1):
        assert cond.unary_expr_kind is cwast.UNARY_EXPR_KIND.NOT
        EmitIRConditional(cond.expr, label_f, label_t, id_gen)
    elif isinstance(cond, cwast.Expr2):
        kind = cond.binary_expr_kind
        if kind is cwast.BINARY_EXPR_KIND.ANDSC:
            label_and = id_gen.next("br_and")
            EmitIRConditional(cond.expr1, label_and, label_f, id_gen)
            print(f".bbl {label_and}")
            EmitIRConditional(cond.expr2, label_t, label_f, id_gen)
        elif kind is cwast.BINARY_EXPR_KIND.ORSC:
            label_or = id_gen.next("br_or")
            EmitIRConditional(cond.expr1, label_t, label_or, id_gen)
            print(f".bbl {label_or}")
            EmitIRConditional(cond.expr2, label_t, label_f, id_gen)
        else:
            op1 = EmitIRExpr(cond.expr1, tc, id_gen)
            op2 = EmitIRExpr(cond.expr2, tc, id_gen)

            if kind is cwast.BINARY_EXPR_KIND.GT:
                kind = cwast.BINARY_EXPR_KIND.LT
                op1, op2 = op2, op1
            elif kind is cwast.BINARY_EXPR_KIND.GE:
                kind = cwast.BINARY_EXPR_KIND.LE
                op1, op2 = op2, op1
            print(f"{TAB}{_MAP_COMPARE[kind]} {op1} {op2} {label_t}")
            print(f"{TAB}bra {label_f}")

    elif isinstance(cond, cwast.Id):
        assert types.is_bool(cond.x_type)
        assert isinstance(cond.x_symbol, (cwast.DefVar, cwast.FunParam))
        print(f"{TAB}bne {cond.name} 0 {label_t}")
        print(f"{TAB}bra {label_f}")
    else:
        assert False, f"unexpected expression {cond}"


_BIN_OP_MAP = {
    cwast.BINARY_EXPR_KIND.MUL: "mul",
    cwast.BINARY_EXPR_KIND.ADD: "add",
    cwast.BINARY_EXPR_KIND.SUB: "sub",
    cwast.BINARY_EXPR_KIND.DIV: "div",
    cwast.BINARY_EXPR_KIND.REM: "rem",
    cwast.BINARY_EXPR_KIND.SHL: "shl",
    cwast.BINARY_EXPR_KIND.SHR: "shr",
    cwast.BINARY_EXPR_KIND.XOR: "xor",
    cwast.BINARY_EXPR_KIND.OR: "or",
    cwast.BINARY_EXPR_KIND.AND: "and",
}


def EmitIRExpr(node, tc: types.TypeCorpus, id_gen: identifier.IdGen) -> Any:
    if isinstance(node, cwast.ExprCall):
        sig = node.callee.x_type
        assert isinstance(sig, cwast.TypeFun)
        args = [EmitIRExpr(a, tc, id_gen) for a in node.args]
        for a in reversed(args):
            print(f"{TAB}pusharg {a}")
        if isinstance(node.callee, cwast.Id):
            print(f"{TAB}bsr {node.callee.x_symbol.name}")
        else:
            assert False
        if types.is_void(sig.result):
            return None
        else:
            res = id_gen.NewName("call")
            print(f"{TAB}poparg {res}:{StringifyOneType(sig.result, tc)}")
            return res
    elif isinstance(node, cwast.ValNum):
        return f"{node.number}:{StringifyOneType(node.x_type, tc)}"
    elif isinstance(node, cwast.ValFalse):
        return f"0:U8"
    elif isinstance(node, cwast.ValTrue):
        return f"1:U8"
    elif isinstance(node, cwast.ExprLen):
        if isinstance(node.container.x_type, cwast.TypeArray):
            assert False, f"{node} {node.x_value}"
        else:
            assert False, f"{node} {node.container}"
    elif isinstance(node, cwast.Id):
        assert isinstance(node.x_type, cwast.TypeBase)
        def_node = node.x_symbol
        if isinstance(def_node, cwast.DefGlobal):
            res = id_gen.NewName("globread")
            print(
                f"{TAB}ld.mem {res}:{StringifyOneType(node.x_type, tc)} = {node.x_symbol.name} 0")
            return res
        else:
            return node.x_symbol.name
    elif isinstance(node, cwast.ExprAddrOf):
        return _GetLValueAddress(node.lhs, tc, id_gen)
    elif isinstance(node, cwast.Expr2):
        op1 = EmitIRExpr(node.expr1, tc, id_gen)
        op2 = EmitIRExpr(node.expr2, tc, id_gen)
        res = id_gen.NewName("expr2")
        op = _BIN_OP_MAP.get(node.binary_expr_kind)
        if op is not None:
            print(
                f"{TAB}{op} {res}:{StringifyOneType(node.x_type, tc)} = {op1} {op2}")
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.INCP:
            assert isinstance(node.expr1.x_type, cwast.TypePtr)
            assert node.expr1.x_type.type.x_size == 1
            # TODO assumed 64
            print(f"{TAB}lea {res}:A64 = {op1} {op2}")
        else:
            assert False, f"unsupported expression {node}"
        return res
    elif isinstance(node, cwast.ExprBitCast):
        res = id_gen.NewName("bitcast")
        expr = EmitIRExpr(node.expr, tc, id_gen)
        print(f"{TAB}bitcast {res}:{StringifyOneType(node.type.x_type, tc)} = {expr}")
        return res
    elif isinstance(node, cwast.ExprAs):
        if (isinstance(node.expr.x_type, cwast.TypeBase) and isinstance(node.type.x_type, cwast.TypeBase)):
            # more compatibility checking needed
            expr = EmitIRExpr(node.expr, tc, id_gen)
            res = id_gen.NewName("as")
            print(
                f"{TAB}conv {res}:{StringifyOneType(node.type.x_type, tc)} = {expr}")
            return res
        elif (isinstance(node.expr.x_type, cwast.TypeArray) and
                isinstance(node.type.x_type, cwast.TypeSlice)):
            addr = _GetLValueAddress(node.expr, tc, id_gen)
            size = node.expr.x_type.size.x_value
            return addr, f"{size}:U64"
        else:
            assert False, f"unsupported cast {node.expr} -> {node.type}"
    elif isinstance(node, cwast.ExprDeref):
        addr = EmitIRExpr(node.expr, tc, id_gen)
        res = id_gen.NewName("deref")
        print(
            f"{TAB}ld {res}:{StringifyOneType(node.expr.x_type, tc)} = {addr} 0")
        return res
    elif isinstance(node, cwast.ExprStmt):
        result = id_gen.NewName("expr")
        for c in node.body:
            EmitIRStmt(c, result, tc, id_gen)
    elif isinstance(node, cwast.ExprIndex):
        addr = _GetLValueAddress(node, tc, id_gen)
        res = id_gen.NewName("at")
        print(f"{TAB}ld {res}:{StringifyOneType(node.x_type, tc)} = {addr} 0")
        return res
    else:
        assert False, f"unsupported expression {node}"

# TODO: support stack allocated objects
def _AssignmentLhsIsInReg(lhs):
    if not isinstance(lhs, cwast.Id):
        return False
    def_node = lhs.x_symbol
    # TODO: support stack allocated objects
    if isinstance(def_node, cwast.DefGlobal):
        return False
    return True


def EmitIRStmt(node, result, type_corpus: types.TypeCorpus, id_gen: identifier.IdGen):
    if isinstance(node, cwast.DefVar):
        def_type = node.x_type
        node.name = id_gen.NewName(node.name)
        assert type_corpus.register_types(
            def_type) is not None, f"unsupported type {def_type}"
        out = EmitIRExpr(node.initial_or_undef, type_corpus, id_gen)
        print(
            f"{TAB}mov {node.name}:{StringifyOneType(node.x_type, type_corpus)} = {out}")
    elif isinstance(node, cwast.StmtBlock):
        continue_label = id_gen.NewName(node.label)
        break_label = id_gen.NewName(node.label)
        node.label = (continue_label, break_label)

        print(f".bbl {continue_label}")
        for c in node.body:
            EmitIRStmt(c, result, type_corpus, id_gen)
        print(f".bbl {break_label}")

    elif isinstance(node, cwast.StmtReturn):
        out = EmitIRExpr(node.expr_ret, type_corpus, id_gen)
        if isinstance(node.x_target, cwast.ExprStmt):
            print(f"{TAB}mov {result} {out}")
        else:
            if node.expr_ret:
                print(f"{TAB}pusharg {out}")
            print(f"{TAB}ret")
    elif isinstance(node, cwast.StmtBreak):
        block = node.x_target.label[1]
        print(f"{TAB}bra {block}")
    elif isinstance(node, cwast.StmtContinue):
        block = node.x_target.label[0]
        print(f"{TAB}bra {block}")
    elif isinstance(node, cwast.StmtExpr):
        EmitIRExpr(node.expr, type_corpus, id_gen)
    elif isinstance(node, cwast.StmtIf):
        label_t = id_gen.NewName("br_t")
        label_f = id_gen.NewName("br_f")
        EmitIRConditional(node.cond, label_t, label_f, id_gen)
        if node.body_t and node.body_f:
            label_n = id_gen.NewName("br_n")
            print(f".bbl {label_t}")
            for c in node.body_t:
                EmitIRStmt(c, result, type_corpus, id_gen)
            print(f"{TAB}bra {label_n}")
            print(f".bbl {label_f}")
            for c in node.body_f:
                EmitIRStmt(c, result, type_corpus, id_gen)
            print(f".bbl {label_n}")
        elif node.body_t:
            print(f".bbl {label_t}")
            for c in node.body_t:
                EmitIRStmt(c, result, type_corpus, id_gen)
            print(f".bbl {label_f}")
        elif node.body_f:
            print(f".bbl {label_f}")
            for c in node.body_t:
                EmitIRStmt(c, result, type_corpus, id_gen)
            print(f".bbl {label_t}")
        else:
            print(f".bbl {label_t}")
            print(f".bbl {label_f}")
    elif isinstance(node, cwast.StmtAssignment):
        assert isinstance(node.lhs.x_type, cwast.TypeBase)
        out = EmitIRExpr(node.expr_rhs, type_corpus, id_gen)
        if _AssignmentLhsIsInReg(node.lhs):
            # because of the canonicalization step only register promotable
            # scalars will be naked like this
            print(f"{TAB}mov {node.lhs.x_symbol.name} = {out}")
        else:
            lhs = _GetLValueAddress(node.lhs, tc, id_gen)
            print(f"{TAB}st {lhs} 0 = {out}")
    elif isinstance(node, cwast.StmtTrap):
        print(f"{TAB}trap")
    else:
        assert False, f"cannot generate code for {node}"


def EmitIRDefGlobal(node: cwast.DefGlobal):
    def_type = node.x_type
    if isinstance(def_type, cwast.TypeBase):
        _EmitMem(node.name, def_type.x_alignment, node.mut,
                 _InitDataForBaseType(node.initial_or_undef.x_type, node.initial_or_undef.x_value))
    elif isinstance(def_type, cwast.TypeArray):
        init = node.initial_or_undef.x_value
        if isinstance(init, bytes):
            assert isinstance(def_type.type, cwast.TypeBase)
            _EmitMem(node.name, 1, node.mut, init)
        else:
            size = def_type.size.x_value
            x_type = def_type.type
            x_value = node.initial_or_undef.x_value
            assert isinstance(x_type, cwast.TypeBase)
            assert size == len(x_value)
            out = b"".join(_InitDataForBaseType(x_type, v) for v in x_value)
            _EmitMem(node.name, node.x_type.x_alignment, node.mut, out)
    else:
        assert False


def EmitIRDefFun(node, type_corpus: types.TypeCorpus, id_gen: identifier.IdGen):
    if not node.extern:
        _EmitFunctionHeader(node, type_corpus)
        _EmitFunctionProlog(node, type_corpus, id_gen)
        for c in node.body:
            EmitIRStmt(c, None, type_corpus, id_gen)


def FindFunSigsWithLargeArgs(tc: types.TypeCorpus) -> Dict[Any, Any]:
    out = {}
    for fun_sig in list(tc.corpus.values()):
        if not isinstance(fun_sig, cwast.TypeFun):
            continue
        change = False
        params = [p.type for p in fun_sig.params]
        for n, p in enumerate(params):
            reg_type = tc.register_types(p)
            if reg_type is None or len(reg_type) > 1:
                params[n] = tc.insert_ptr_type(False, p)
                change = True
        result = fun_sig.result
        reg_type = tc.register_types(result)
        if not types.is_void(result) and reg_type is None or len(reg_type) > 1:
            change = True
            params.append(tc.insert_ptr_type(True, result))
            result = tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID)
        if change:
            out[fun_sig] = tc.insert_fun_type(params, result)
    return out


def MakeTypeVoid(tc, srcloc):
    return cwast.TypeBase(cwast.BASE_TYPE_KIND.VOID, x_srcloc=srcloc,
                          x_type=tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID))


def RewriteLargeArgsCallerSide(fun: cwast.DefFun, fun_sigs_with_large_args, id_gen: identifier.IdGen):

    def replacer(call, field) -> Optional[Any]:
        if isinstance(call, cwast.ExprCall) and call.callee.x_type in fun_sigs_with_large_args:
            old_sig: cwast.TypeFun = call.callee.x_type
            new_sig:  cwast.TypeFun = fun_sigs_with_large_args[old_sig]
            expr_body = []
            expr = cwast.ExprStmt(
                expr_body, x_srcloc=call.x_srcloc, x_type=call.x_type)
            # note: new_sig might be longer if the result type was changed
            for n, (old, new) in enumerate(zip(old_sig.params, new_sig.params)):
                if old.type != new.type:
                    new_def = cwast.DefVar(False, id_gen.NewName("param"),
                                           cwast.TypeAuto(
                                               x_srcloc=call.x_srcloc), call.args[n],
                                           x_srcloc=call.x_srcloc, x_type=old.type)
                    expr_body.append(new_def)
                    name = cwast.Id(new_def.name, "",
                                    x_srcloc=call.x_srcloc, x_type=old.type, x_symbol=new_def)
                    call.args[n] = cwast.ExprAddrOf(
                        False, name, x_srcloc=call.x_srcloc, x_type=new.type)
            if len(old_sig.params) != len(new_sig.params):
                new_def = cwast.DefVar(True, id_gen.NewName("result"),
                                       cwast.TypeAuto(x_srcloc=call.x_srcloc),
                                       cwast.ValUndef(x_srcloc=call.x_srcloc),
                                       x_srcloc=call.x_srcloc, x_type=old_sig.result)
                name = cwast.Id(new_def.name, "",
                                x_srcloc=call.x_srcloc, x_type=old_sig.result, x_symbol=new_def)
                call.args.append(cwast.ExprAddrOf(
                    True, name, x_srcloc=call.x_srcloc, x_type=new_sig.params[-1].type))
                call.x_type = tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID)
                call.callee.x_type = new_sig
                expr_body.append(new_def)
                expr_body.append(cwast.StmtExpr(
                    False, call, x_srcloc=call.x_srcloc))
                expr_body.append(cwast.StmtReturn(
                    expr_ret=name, x_srcloc=call.x_srcloc, x_target=expr))
            else:
                expr_body.append(cwast.StmtReturn(
                    expr_ret=call, x_srcloc=call.x_srcloc, x_target=expr))
            return expr
        return None
    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def _FixupFunctionPrototypeForLargArgs(fun: cwast.DefFun, new_sig: cwast.TypeFun,
                                       tc: types.TypeCorpus, id_gen: identifier.IdGen):
    old_sig: cwast.TypeFun = fun.x_type
    fun.x_type = new_sig
    result_changes = old_sig.result != new_sig.result
    if result_changes:
        assert types.is_void(new_sig.result)
        assert len(new_sig.params) == 1 + len(old_sig.params)
        result_type = cwast.TypePtr(
            True, fun.result, x_srcloc=fun.x_srcloc, x_type=new_sig.params[-1].type)
        result_param = cwast.FunParam(id_gen.NewName(
            "result"), result_type, x_srcloc=fun.x_srcloc, x_type=new_sig.params[-1].type)
        fun.params.append(result_param)
        fun.result = MakeTypeVoid(tc, fun.x_srcloc)
    changing_params = {}

    for p, old, new in zip(fun.params, old_sig.params, new_sig.params):
        if old.type != new.type:
            changing_params[p] = new.type
            p.type = cwast.TypePtr(
                False, p.type, x_srcloc=p.x_srcloc, x_type=new.type)
    assert result_changes or changing_params
    return changing_params, result_changes


def RewriteLargeArgsCalleeSide(fun: cwast.DefFun, new_sig: cwast.TypeFun,
                               tc: types.TypeCorpus, id_gen: identifier.IdGen):
    changing_params, result_changes = _FixupFunctionPrototypeForLargArgs(
        fun, new_sig, tc, id_gen)

    # print([k.name for k, v in changing_params.items()], result_changes)

    def replacer(node, field) -> Optional[Any]:

        if isinstance(node, cwast.Id) and node.x_symbol in changing_params:
            new_node = cwast.ExprDeref(
                node, x_srcloc=node.x_srcloc, x_type=node.x_type)
            node.x_type = changing_params[node.x_symbol]
            return new_node
        elif isinstance(node, cwast.StmtReturn) and node.x_target == fun and result_changes:
            result_param: cwast.FunParam = fun.params[-1]
            lhs = cwast.ExprDeref(
                cwast.Id(result_param.name, "", x_srcloc=node.x_srcloc,
                         x_type=result_param.type.x_type, x_symbol=result_param),
                x_srcloc=node.x_srcloc, x_type=node.expr_ret.x_type)
            assign = cwast.StmtAssignment(
                lhs, node.expr_ret, x_srcloc=node.x_srcloc)
            node.expr_ret = cwast.ValVoid(
                x_srcloc=node.x_srcloc, x_type=tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID))
            return cwast.EphemeralList([assign, node], x_srcloc=node.x_srcloc)
        return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)
    cwast.EliminateEphemeralsRecursively(fun)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = parse.ReadModsFromStream(sys.stdin)

    mod_topo_order, mod_map = symbolize.ModulesInTopologicalOrder(asts)
    symbolize.MacroExpansionDecorateASTWithSymbols(mod_topo_order, mod_map)
    for mod in mod_topo_order:
        cwast.StripNodes(mod, cwast.Comment)
        cwast.StripNodes(mod, cwast.DefMacro)
    tc: types.TypeCorpus = types.TypeCorpus(
        cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    typify.DecorateASTWithTypes(mod_topo_order, tc)
    eval.DecorateASTWithPartialEvaluation(mod_topo_order)

    # Legalize so that code emitter works
    mod_gen = cwast.DefMod("$generated", [], [])
    id_gen = identifier.IdGen()
    str_val_map = {}
    fun_sigs_with_large_args = FindFunSigsWithLargeArgs(tc)
    # for key, val in fun_sigs_with_large_args.items():
    #    print (tc.canon_name(key), " -> ", tc.canon_name(val))
    for mod in mod_topo_order:
        canonicalize.ReplaceConstExpr(mod)
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            canonicalize.CanonicalizeStringVal(fun, str_val_map, id_gen)
            typify.VerifyTypesRecursively(fun, tc)

            canonicalize.CanonicalizeBoolExpressionsNotUsedForConditionals(fun, tc)
            typify.VerifyTypesRecursively(fun, tc)

            canonicalize.CanonicalizeTernaryOp(fun, id_gen)
            RewriteLargeArgsCallerSide(fun, fun_sigs_with_large_args, id_gen)
            if fun.x_type in fun_sigs_with_large_args:
                RewriteLargeArgsCalleeSide(
                    fun, fun_sigs_with_large_args[fun.x_type], tc, id_gen)
            canonicalize.CanonicalizeCompoundAssignments(fun, tc, id_gen)
            symbolize.VerifyASTSymbolsRecursively(fun)
            typify.VerifyTypesRecursively(fun, tc)

    mod_gen.body_mod += list(str_val_map.values())
    mod_topo_order = [mod_gen] + mod_topo_order

    # for mod in mod_topo_order:
    #    pp.PrettyPrint(mod)
    # exit(0)

    # Fully qualify names
    for mod in mod_topo_order:
        mod_name = "" if mod.name == "main" else mod.name + "/"
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun, cwast.DefGlobal)):
                node.name = mod_name + node.name
                if isinstance(node, cwast.DefFun):
                    id_gen = identifier.IdGen()

    # Emit Cwert IR
    for mod in mod_topo_order:
        id_gen.ClearGlobalNames()
        id_gen.LoadGlobalNames(mod)
        for node in mod.body_mod:
            if isinstance(node, cwast.DefGlobal):
                EmitIRDefGlobal(node)
        for node in mod.body_mod:

            if isinstance(node, cwast.DefFun):
                id_gen.ClearLocalNames()
                id_gen.UniquifyLocalNames(node)
                EmitIRDefFun(node, tc, id_gen)
