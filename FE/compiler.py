#!/bin/env python3

"""Compiler"""

import logging
import argparse
import pathlib
import os

from typing import Any, Optional


from FE import canonicalize_large_args
from FE import canonicalize_span
from FE import canonicalize_union
from FE import canonicalize
from FE import macro
from FE import symbolize
from FE import type_corpus
from FE import cwast
from FE import typify
from FE import eval
from FE import identifier
from FE import mod_pool
from FE import dead_code
from FE import optimize
from FE import stats
from FE import checker
from FE import emit_ir

logger = logging.getLogger(__name__)


_GENERATED_MODULE_NAME = "GeNeRaTeD"


def MangledGlobalName(mod: cwast.DefMod, mod_name: str, node: Any, is_cdecl: bool) -> cwast.NAME:
    assert isinstance(node, (cwast.DefFun, cwast.DefGlobal))
    # when we emit Cwerg IR we use the "/" sepearator not "::" because
    # : is used for type annotations
    poly_suffix = ""
    if isinstance(node, (cwast.DefFun)) and node.poly:
        poly_suffix = f"<{node.x_type.parameter_types()[0].name}>"
    n = node.name
    if is_cdecl:
        return cwast.NAME.Make(f"{n}{poly_suffix}")
    else:
        return cwast.NAME.Make(f"{mod_name}/{n}{poly_suffix}")


def SanityCheckMods(phase_name: str, stage: checker.COMPILE_STAGE, args: Any,
                    mods: list[cwast.DefMod], tc: Optional[type_corpus.TypeCorpus],
                    eliminated_node_types):

    logger.info(phase_name)
    if args.emit_stats == phase_name:
        node_histo = stats.ComputeNodeHistogram(mods)
        stats.DumpCounter(node_histo)
        stats.DumpStats()

    if args.dump_ast_html == phase_name:
        from FE import pp_html
        for mod in mods:
            pp_html.PrettyPrintHTML(mod)
            # pp_sexpr.PrettyPrint(mod)
        exit(0)

    if args.dump_ast == phase_name:
        from FE import pp_ast
        import sys
        pp_ast.DumpMods(mods, sys.stdout)
        exit(0)

    if args.dump_types == phase_name:
        for m in mods:
            print(m.name)
        assert tc
        tc.Dump()
        exit(0)

    if args.stop == phase_name:
        exit(0)

    no_symbols = stage.value < checker.COMPILE_STAGE.AFTER_TYPIFY.value
    allow_type_auto = stage.value >= checker.COMPILE_STAGE.AFTER_DESUGAR.value
    for mod in mods:
        checker.CheckAST(mod, eliminated_node_types, allow_type_auto,
                         pre_symbolize=no_symbols)

        if stage.value >= checker.COMPILE_STAGE.AFTER_SYMBOLIZE.value:
            symbolize.VerifySymbols(mod)

        if stage in (checker.COMPILE_STAGE.AFTER_TYPIFY, checker.COMPILE_STAGE.AFTER_EVAL, checker.COMPILE_STAGE.AFTER_DESUGAR):
            typify.VerifyTypesRecursively(mod, tc, typify.VERIFIERS_WEAK)
        if stage.value > checker.COMPILE_STAGE.AFTER_EVAL.value:
            typify.VerifyTypesRecursively(mod, tc, typify.VERIFIERS_STRICT)

        if stage.value >= checker.COMPILE_STAGE.AFTER_EVAL.value:
            eval.VerifyASTEvalsRecursively(mod)


_ARCH_MAP = {
    "x64": type_corpus.STD_TARGET_X64,
    "a64": type_corpus.STD_TARGET_A64,
    "a32": type_corpus.STD_TARGET_A32,
}


def PhaseInitialLowering(mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus):
    # for key, val in fun_sigs_with_large_args.items():
    #    print (key.name, " -> ", val.name)
    # ct_bool = tc.get_bool_canon_type()
    typeid_ct = tc.get_typeid_canon_type()
    for mod in mod_topo_order:
        typify.ModStripTypeNodesRecursively(mod)
        for fun in mod.body_mod:
            canonicalize.FunReplaceConstExpr(fun, tc)
            canonicalize.FunMakeImplicitConversionsExplicit(fun, tc)
            canonicalize.FunReplaceExprIndex(fun, tc)
            canonicalize.FunDesugarTaggedUnionComparisons(fun)
            canonicalize.FunReplaceSpanCastWithSpanVal(fun, tc)
            if not isinstance(fun, cwast.DefFun):
                continue

            # note: ReplaceTaggedExprNarrow introduces new ExprIs nodes
            canonicalize_union.FunSimplifyTaggedExprNarrow(fun, tc)
            canonicalize.FunDesugarExprIs(fun, typeid_ct)
            canonicalize.FunEliminateDefer(fun)
            canonicalize.FunRemoveUselessCast(fun)
            # this creates TernaryOps
            canonicalize.FunCanonicalizeBoolExpressionsNotUsedForConditionals(
                fun)
            canonicalize.FunDesugarExpr3(fun)
            canonicalize.FunOptimizeKnownConditionals(fun)
            if not fun.extern:
                canonicalize.FunAddMissingReturnStmts(fun)


def PhaseOptimize(mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus):
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if isinstance(fun, cwast.DefFun):
                optimize.FunOptimize(fun)


def MakeModWithComplexConstants(mod_topo_order: list[cwast.DefMod]) -> cwast.DefMod:
    constant_pool = eval.GlobalConstantPool()
    for mod in mod_topo_order:
        constant_pool.EliminateValStringAndValCompoundOutsideOfDefGlobal(mod)
    mod_gen = cwast.DefMod(cwast.NAME.Make(_GENERATED_MODULE_NAME),
                           [], [], x_srcloc=cwast.SRCLOC_GENERATED)
    # the checker neeeds a symtab, so we add an empty one
    mod_gen.x_symtab = symbolize.SymTab()
    mod_gen.body_mod += constant_pool.GetDefGlobals()
    return mod_gen


def PhaseEliminateSpanAndUnion(mod_gen: cwast.DefMod, mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus):
    # it should not matter if we replace spans or tagged unions first
    mod_gen.body_mod.extend(
        canonicalize_span.MakeAndRegisterSpanTypeReplacements(tc))
    for mod in ([mod_gen] + mod_topo_order):
        canonicalize_span.ReplaceSpans(mod)
    #
    mod_gen.body_mod.extend(
        canonicalize_union.MakeAndRegisterUnionTypeReplacements(tc))
    for mod in ([mod_gen] + mod_topo_order):
        canonicalize_union.ReplaceUnions(mod)


def PhaseEliminateLargeArgs(mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus):
    canonicalize_large_args.MakeAndRegisterLargeArgReplacements(tc)
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if not isinstance(fun, cwast.DefFun):
                continue
            canonicalize_large_args.FunRewriteLargeArgsCallsites(fun, tc)
            new_sig = fun.x_type.replacement_type
            if new_sig:
                canonicalize_large_args.FunRewriteLargeArgsParameter(
                    fun, new_sig, tc)


def PhaseLegalize(mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus):
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if not isinstance(fun, cwast.DefFun):
                continue
            canonicalize.FunCanonicalizeCompoundAssignments(fun)
            canonicalize.FunCanonicalizeRemoveStmtCond(fun)
            canonicalize.FunRewriteComplexAssignments(fun, tc)


def main() -> int:
    parser = argparse.ArgumentParser(description='pretty_printer')
    parser.add_argument("-shake_tree",
                        action="store_true", help='remove unreachable functions')
    parser.add_argument(
        '-stdlib', help='path to stdlib directory', default="./Lib")
    parser.add_argument(
        '-arch', help='architecture to generated IR for', default="x64")
    parser.add_argument(
        '-dump_ast_html', help='stop at the given stage and dump ast in html format')
    parser.add_argument(
        '-dump_ast', help='stop at the given stage and dump ast')
    parser.add_argument(
        '-dump_types', help='stop at the given stage and dump types')
    parser.add_argument(
        '-stop', help='stop at the given stage')
    parser.add_argument(
        '-emit_stats', help='stop at the given stage and emit stats')
    parser.add_argument('files', metavar='F', type=str, nargs='+',
                        help='an input source file')
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARN)
    # typify.logger.setLevel(logging.INFO)
    logger.info("Start Parsing")
    assert len(args.files) == 1
    fn = args.files[0]
    fn, ext = os.path.splitext(fn)
    assert ext in (".cw", ".cws")
    main = str(pathlib.Path(fn).resolve())
    mp = mod_pool.ReadModulesRecursively(
        pathlib.Path(args.stdlib), [main], add_builtin=True)
    eliminated_nodes: set[Any] = set()
    eliminated_nodes.add(cwast.Import)
    eliminated_nodes.add(cwast.ModParam)
    mod_topo_order = mp.mods_in_topo_order
    main_entry_fun: cwast.DefFun = mp.main_fun

    SanityCheckMods("after_parsing", checker.COMPILE_STAGE.AFTER_PARSING,
                    args, mod_topo_order, tc=None,
                    eliminated_node_types=eliminated_nodes)

    # keeps track of those node classes which have been eliminated and hence must not
    # occur in the AST anymore
    for mod in mod_topo_order:
        canonicalize.FunRemoveParentheses(mod)
    eliminated_nodes.add(cwast.ExprParen)  # this needs more work

    #
    logger.info("Expand macros and link most IDs to their definition")
    macro.ExpandMacrosAndMacroLike(mod_topo_order)
    eliminated_nodes.update([cwast.MacroInvoke,
                             cwast.MacroId,
                             cwast.MacroFor,
                             cwast.MacroParam,
                             cwast.ExprSrcLoc,
                             cwast.ExprStringify,
                             cwast.EphemeralList,
                             cwast.DefMacro])
    symbolize.SetTargetFields(mod_topo_order)
    # global symbols have already been resolved
    symbolize.ResolveSymbolsInsideFunctions(mod_topo_order, mp.builtin_symtab)
    # Before Typing we cannot set the symbol links for rec fields
    SanityCheckMods("after_symbolizing", checker.COMPILE_STAGE.AFTER_SYMBOLIZE,
                    args, mod_topo_order, None, eliminated_nodes)

    ta: type_corpus.TargetArchConfig = _ARCH_MAP[args.arch]
    tc: type_corpus.TypeCorpus = type_corpus.TypeCorpus(ta)

    #
    logger.info("Typify the nodes")
    typify.AddTypesToAst(mod_topo_order, tc)
    SanityCheckMods("after_typing", checker.COMPILE_STAGE.AFTER_TYPIFY, args, mod_topo_order, tc=tc,
                    eliminated_node_types=eliminated_nodes)

    #
    if args.shake_tree:
        dead_code.ShakeTree(mod_topo_order, main_entry_fun)

    #
    logger.info("partial eval and static assert validation")
    eval.DecorateASTWithPartialEvaluation(mod_topo_order)
    for mod in mod_topo_order:
        cwast.RemoveNodesOfType(mod, cwast.StmtStaticAssert)
    eliminated_nodes.add(cwast.StmtStaticAssert)
    SanityCheckMods("after_partial_eval", checker.COMPILE_STAGE.AFTER_EVAL, args,
                    mod_topo_order, tc, eliminated_nodes)

    #
    logger.info("phase: initial lowering")
    PhaseInitialLowering(mod_topo_order, tc)
    eliminated_nodes.update([cwast.ExprIndex,
                             cwast.ExprIs,
                             cwast.ExprOffsetof,
                             cwast.ExprSizeof,
                             cwast.ExprTypeId,
                             cwast.StmtDefer,
                             #
                             cwast.DefType,
                             cwast.TypeBase,
                             cwast.TypeSpan,
                             cwast.TypeVec,
                             cwast.TypePtr,
                             cwast.TypeFun,
                             cwast.TypeUnion,
                             cwast.TypeOf,
                             cwast.TypeUnionDelta])
    SanityCheckMods("after_initial_lowering", checker.COMPILE_STAGE.AFTER_DESUGAR,
                    args,
                    mod_topo_order, tc,  eliminated_nodes)

    # This section coould probably happen AFTER the next phase

    #
    logger.info("phase: early cleanup and optimization")
    PhaseOptimize(mod_topo_order, tc)
    eliminated_nodes.add(cwast.Expr3)

    SanityCheckMods("after_optimization", checker.COMPILE_STAGE.AFTER_DESUGAR,
                    args, mod_topo_order, tc,  eliminated_nodes)

    #
    mod_gen = MakeModWithComplexConstants(mod_topo_order)

    #
    logger.info("phase: eliminate span and union")
    PhaseEliminateSpanAndUnion(mod_gen, mod_topo_order, tc)
    eliminated_nodes.update([cwast.ExprLen,
                             cwast.ValSpan,
                             cwast.ExprUnionTag,
                             cwast.ExprUnionUntagged])
    SanityCheckMods("after_eliminate_span_and_union", checker.COMPILE_STAGE.AFTER_DESUGAR, args,
                    [mod_gen] + mod_topo_order, tc, eliminated_nodes)

    #
    logger.info("phase: eliminate large args")
    PhaseEliminateLargeArgs(mod_topo_order, tc)
    SanityCheckMods("after_large_arg_conversion", checker.COMPILE_STAGE.AFTER_DESUGAR, args,
                    [mod_gen] + mod_topo_order, tc,  eliminated_nodes)
    #
    logger.info("phase: legalize")
    PhaseLegalize(mod_topo_order, tc)
    PhaseOptimize(mod_topo_order, tc)
    eliminated_nodes.update([cwast.StmtCompoundAssignment,
                             cwast.StmtCond,
                             cwast.Case])
    SanityCheckMods("after_legalize", checker.COMPILE_STAGE.AFTER_DESUGAR, args,
                    [mod_gen] + mod_topo_order, tc, eliminated_nodes)

    assert eliminated_nodes == cwast.ALL_NODES_NON_CORE
    mod_topo_order = [mod_gen] + mod_topo_order

    # Naming cleanup:
    # * Set fully qualified names for all module level symbols
    # * uniquify local variables so we can use them directly
    #   for codegen without having to worry about name clashes
    for mod in mod_topo_order:
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun, cwast.DefGlobal)):
                node.name = MangledGlobalName(
                    mod, str(mod.name), node, node.cdecl or node == main_entry_fun)

    SanityCheckMods("after_name_cleanup", checker.COMPILE_STAGE.AFTER_DESUGAR,
                    args,
                    mod_topo_order, tc, eliminated_nodes)

    # Emit Cwert IR
    # print ("# TOPO-ORDER")
    # for mod in mod_topo_order:
    #    print (f"# {mod.name}")

    sig_names: set[str] = set()
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if isinstance(fun, cwast.DefFun):
                sn = emit_ir.MakeFunSigName(fun.x_type)
                if sn not in sig_names:
                    emit_ir.EmitFunctionHeader(sn, "SIGNATURE", fun.x_type)
                    sig_names.add(sn)

    for mod in mod_topo_order:
        for node in mod.body_mod:
            if isinstance(node, cwast.DefGlobal):
                emit_ir.EmitIRDefGlobal(node, ta)
        for node in mod.body_mod:

            if isinstance(node, cwast.DefFun):
                emit_ir.EmitIRDefFun(node, ta, identifier.IdGenIR())
    return 0


if __name__ == "__main__":
    if 0:
        # consider using:
        # python -m cProfile -o output.pstats path/to/your/script arg1 arg2
        # gprof2dot.py -f pstats output.pstats | dot -Tpng -o output.png
        from cProfile import Profile
        from pstats import SortKey, Stats
        with Profile() as profile:
            ret = main()
            Stats(profile).strip_dirs().sort_stats(SortKey.CALLS).print_stats()
            exit(ret)
    else:
        exit(main())
