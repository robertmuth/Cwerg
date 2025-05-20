import logging

from typing import Tuple, Any, Optional


from FE import cwast


def _VisitAstRecursivelyWithParentAndField(node, visitor, parent, nfd=None):
    if visitor(node, parent, nfd):
        return

    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is cwast.NFK.NODE:
            child = getattr(node, f)
            _VisitAstRecursivelyWithParentAndField(child, visitor, node, nfd)
        else:
            for child in getattr(node, f):
                _VisitAstRecursivelyWithParentAndField(
                    child, visitor, node, nfd)


def _CheckMacroRecursively(node, seen_names: set[str]):
    def visitor(node):
        if isinstance(node, (cwast.MacroParam, cwast.MacroFor)):
            assert node.name.IsMacroVar()
            assert node.name not in seen_names, f"duplicate name: {node.name}"
            seen_names.add(node.name)
    cwast.VisitAstRecursively(node, visitor)


def _IsPermittedNode(node, permitted, parent, toplevel_node, node_mod: cwast.DefMod,
                     allow_type_auto: bool) -> bool:
    if node.__class__.__name__ in permitted:
        return True
    if isinstance(node, cwast.MacroInvoke):
        # this could be made stricter, i.e. only for exprs and stmts
        return True
    if isinstance(node, cwast.TypeAuto):
        return allow_type_auto
    if isinstance(node, cwast.MacroId):
        return isinstance(toplevel_node, cwast.DefMacro) or node_mod.params_mod

    if isinstance(parent, (cwast.MacroInvoke, cwast.EphemeralList)):
        return True  # refine
    if isinstance(toplevel_node, cwast.DefMacro):
        return True  # refine
    return False


def CheckAST(node_mod: cwast.DefMod, disallowed_nodes, allow_type_auto=False, pre_symbolize=False):
    """
    This check is run at various stages of compilation.

    `disallowed_nodes` contains a set of nodes that must not appear.

    `pre_symbolize` indicates that the check is running before symbolization so
    that the fields `x_symtab`, `x_target`, `x_symbol` are not yet set.


    """
    # this only works with pre-order traversal
    toplevel_node = None

    def visitor(node: Any, parent: Any, nfd: cwast.NFD):
        nonlocal disallowed_nodes
        nonlocal toplevel_node
        nonlocal node_mod
        nonlocal pre_symbolize

        if type(node) in disallowed_nodes:
            cwast.CompilerError(
                node.x_srcloc, f"Disallowed node: {type(node)} in {toplevel_node}")

        assert isinstance(
            node.x_srcloc, cwast. SrcLoc) and node.x_srcloc != cwast.INVALID_SRCLOC, f"Node without srcloc node {node} for parent={parent} field={nfd} {node.x_srcloc}"

        if cwast.NF.TOP_LEVEL in node.FLAGS:
            if not isinstance(parent, cwast.DefMod):
                cwast.CompilerError(
                    node.x_srcloc, f"only allowed at toplevel: {node}")
            toplevel_node = node
        if cwast.NF.MACRO_BODY_ONLY in node.FLAGS:
            assert isinstance(
                toplevel_node, cwast.DefMacro), f"only allowed in macros: {node}"

        if cwast.NF.LOCAL_SYM_DEF in node.FLAGS:
            assert isinstance(node.name, cwast.NAME), f"{node}"
        if cwast.NF.GLOBAL_SYM_DEF in node.FLAGS:
            if not isinstance(node, cwast.DefMod):
                assert isinstance(node.name, cwast.NAME), f"{node}"

        if isinstance(node, cwast.DefMacro):
            if not node.name.IsMacroCall() and node.name.name not in cwast.ALL_BUILT_IN_MACROS:
                cwast.CompilerError(
                    node.x_srcloc, f"macro name must end with `#`: {node.name}")
            for p in node.params_macro:
                if isinstance(p, cwast.MacroParam):
                    assert p.name.IsMacroVar()
            for i in node.gen_ids:
                assert isinstance(i, cwast.MacroId)
            _CheckMacroRecursively(node, set())
        elif isinstance(node, cwast.Id):
            assert isinstance(node.name, cwast.NAME), f"{node} {node.x_symbol}"
            if not pre_symbolize:
                assert node.x_symbol is not cwast.INVALID_SYMBOL, f"{
                    node} without valid x_symbol {node.x_srcloc}"
            if node.name.IsMacroVar():
                cwast.CompilerError(node.x_srcloc, f"{node} start with $")
        elif isinstance(node, cwast.MacroId):
            assert node.name.IsMacroVar()
        elif isinstance(node, cwast.StmtBlock):
            assert isinstance(node.label, cwast.NAME), f"{node} {node.x_srcloc}"
        elif isinstance(node, cwast.StmtBreak):
            assert isinstance(node.target,cwast. NAME), f"{node} {node.x_srcloc}"
        elif isinstance(node, cwast.StmtContinue):
            assert isinstance(node.target, cwast.NAME), f"{node} {node.x_srcloc}"
        elif isinstance(node, cwast.Import):
            if not pre_symbolize:
                assert node.x_module != cwast.INVALID_MOD
        elif isinstance(node, cwast.DefMod):
            if not pre_symbolize:
                assert node.x_symtab, f"missing x_symtab {node}"
        if nfd is not None:
            if not _IsPermittedNode(node, nfd.node_type, parent, toplevel_node,
                                    node_mod,
                                    allow_type_auto):
                cwast.CompilerError(
                    node.x_srcloc, f"unexpected node for field={nfd.name}: {node.__class__.__name__}")

    _VisitAstRecursivelyWithParentAndField(node_mod, visitor, None)
