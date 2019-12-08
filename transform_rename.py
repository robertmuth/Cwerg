"""
TODO
"""
from typing import Mapping

from pycparser import c_ast

import common
import meta

__all__ = ["LiftStaticAndExternToGlobalScope"]


def IsExternOrStatic(node, parent):
    return  isinstance(node, c_ast.Decl) and ("extern" in node.storage or "static" in node.storage)


def LiftStaticAndExternToGlobalScope(ast: c_ast.FileAST, meta_info: meta.MetaInfo, id_gen: common.UniqueId):
    """Requires that if statements only have gotos"""
    candidates = common.FindMatchingNodesPostOrder(ast, ast, IsExternOrStatic)

    for decl, parent in candidates:
        if "static" in decl.storage:
            new_name = id_gen.next("__static") + "_" + decl.name
            decl.name = new_name
            decl.storage.remove("static")
            if isinstance(decl.type, c_ast.FuncDecl):
                decl.type.type.declname = new_name

            elif isinstance(decl.type, c_ast.TypeDecl):
                decl.type.declname = new_name
                if parent != ast:
                    stmts = common.GetStatementList(parent)
                    assert stmts, parent
                    stmts.remove(decl)
                    # TODO: insert it just outside the function
                    ast.ext.insert(0, decl)
            for id, sym in meta_info.sym_links.items():
                if sym == decl:
                    assert isinstance(id, c_ast.ID)
                    id.name = new_name
        if "extern" in decl.storage:
            decl.storage.remove("extern")
            if parent != ast:
                stmts = common.GetStatementList(parent)
                assert stmts, parent
                stmts.remove(decl)
                # TODO: insert it just outside the function
                ast.ext.insert(0, decl)
