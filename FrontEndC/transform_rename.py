"""
TODO
"""

from pycparser import c_ast

import common
import meta

__all__ = ["LiftStaticAndExternToGlobalScope", "UniquifyLocalVars"]


def RenameSymbol(decl, new_name, meta_info):
    decl.name = new_name
    if isinstance(decl.type, c_ast.FuncDecl):
        decl.type.type.declname = new_name
    elif isinstance(decl.type, c_ast.TypeDecl):
        decl.type.declname = new_name
    elif isinstance(decl.type, c_ast.ArrayDecl):
        decl.type.type.declname = new_name
    elif isinstance(decl.type, c_ast.PtrDecl):
        # probably needs to be recursive
        decl.type.type.declname = new_name
    else:
        assert False, f"unexpected decl: {decl}"

    for id, sym in meta_info.sym_links.items():
        if sym == decl:
            assert isinstance(id, c_ast.ID)
            id.name = new_name


def IsExternOrStatic(node, parent):
    return isinstance(node, c_ast.Decl) and ("extern" in node.storage or "static" in node.storage)


def LiftStaticAndExternToGlobalScope(ast: c_ast.FileAST, meta_info: meta.MetaInfo, id_gen: common.UniqueId):
    """Requires that if statements only have gotos

    Why the constraint?
    We want all variables we need to allocate memory for to be at the
    top level.
    """
    candidates = common.FindMatchingNodesPostOrder(ast, ast, IsExternOrStatic)

    for decl, parent in candidates:
        if "static" in decl.storage:
            new_name = id_gen.next("__static") + "_" + decl.name
            decl.storage.remove("static")
            RenameSymbol(decl, new_name, meta_info)
            if isinstance(decl.type, (c_ast.TypeDecl, c_ast.ArrayDecl, c_ast.PtrDecl)) and parent != ast:
                # rip it out
                stmts = common.GetStatementList(parent)
                assert stmts, parent
                stmts.remove(decl)
                # TODO: insert it just outside the function
                ast.ext.insert(0, decl)
            elif isinstance(decl.type, c_ast.FuncDecl):
                pass
            else:
                assert False, decl
        if "extern" in decl.storage:
            decl.storage.remove("extern")
            if ast != parent:
                stmts = common.GetStatementList(parent)
                assert stmts, parent
                stmts.remove(decl)
                # TODO: insert it just outside the function
                ast.ext.insert(0, decl)


def IsShadowingEarlierDecl(name, sym_tab):
    for l in reversed(sym_tab):
        s = l.get(name)
        if s:
            return s
    return None


def MaybeRenameSymbols(node, parent, meta_info, local_syms, id_gen: common.UniqueId):
    #if isinstance(node, common.NEW_SCOPE_NODE):
    #    local_syms.append({})

    if isinstance(node, (c_ast.Struct,c_ast.Union)):
        return

    if isinstance(node, c_ast.Decl):
        # skip non local vars
        if "static" in node.storage or "extern" in node.storage:
            return
        if IsShadowingEarlierDecl(node.name, local_syms):
            new_name = id_gen.next("__local") + "_" + node.name
            RenameSymbol(node, new_name, meta_info)

        local_syms[-1][node.name] = node

    for c in node:
        MaybeRenameSymbols(c, node, meta_info, local_syms, id_gen)

    #if isinstance(node, common.NEW_SCOPE_NODE):
    #    local_syms.pop(-1)


def UniquifyLocalVars(fun: c_ast.FuncDef, meta_info: meta.MetaInfo, id_gen: common.UniqueId):
    MaybeRenameSymbols(fun, fun, meta_info, [{}], id_gen)
