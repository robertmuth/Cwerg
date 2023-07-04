#!/usr/bin/python3

"""Pretty printer (PP) for Cwerg AST

"""

import sys
import logging
import argparse

from typing import List, Dict, Set, Optional, Union, Any, Tuple

from FrontEnd import cwast
from FrontEnd import parse
from FrontEnd import symbolize
from FrontEnd import typify
from FrontEnd import types
from FrontEnd import eval


logger = logging.getLogger(__name__)


def MaybeSimplifyLeafNode(node) -> Optional[str]:
    if isinstance(node, cwast.TypeBase):
        return node.base_type_kind.name.lower()
    elif isinstance(node, cwast.ValUndef):
        return "undef"
    elif isinstance(node, cwast.TypeAuto):
        return "auto"
    elif isinstance(node, cwast.Id):
        return node.name
    elif isinstance(node, cwast.ValTrue):
        return "true"
    elif isinstance(node, cwast.ValFalse):
        return "false"
    elif isinstance(node, cwast.ValNum):
        return node.number
    elif isinstance(node, cwast.ValVoid):
        return "void_val"
    elif isinstance(node, cwast.ValString):
        return node.string
    elif isinstance(node, cwast.StmtBreak) and node.target == "":
        return "break"
    elif isinstance(node, cwast.StmtContinue) and node.target == "":
        return "continue"
    else:
        return None


def IsFieldWithDefaultValue(field, val):
    expected = cwast.OPTIONAL_FIELDS.get(field)
    return val == expected


def GetNodeTypeAndFields(node, condense=True):
    cls = node.__class__
    fields = cls.FIELDS[:]
    if not condense:
        return cls.__name__, fields

    if isinstance(node, cwast.StmtCompoundAssignment):
        fields.pop(0)
        return cwast.ASSIGMENT_SHORTCUT_INV[node.assignment_kind], fields
    elif isinstance(node, cwast.Expr1):
        fields.pop(0)
        return cwast.UNARY_EXPR_SHORTCUT_INV[node.unary_expr_kind], fields
    elif isinstance(node, cwast.Expr2):
        fields.pop(0)
        return cwast.BINARY_EXPR_SHORTCUT_INV[node.binary_expr_kind], fields
    elif isinstance(node, cwast.ExprPointer):
        fields.pop(0)
        return cwast.POINTER_EXPR_SHORTCUT_INV[node.pointer_expr_kind], fields
    elif cls.ALIAS:
        return cls.ALIAS, fields
    else:
        return cls.__name__, fields


############################################################
# Pretty Print
############################################################
STMT_LIST_INDENT = 4
EXPR_LIST_INDENT = 8


def GetColonIndent(field: str):
    return 0 if field == "body_mod" else STMT_LIST_INDENT


def GetExprIndent(field: str):
    return EXPR_LIST_INDENT


def RenderColonList(val: List, field: str, out, indent: str):

    extra_indent = GetColonIndent(field)
    line = out[-1]
    if field == "body_f":
        out.append([" " * (indent + extra_indent) + ":"])
        for cc in val:
            out.append([" " * (indent + extra_indent)])
            RenderRecursivelyToIR(
                cc, out, indent + extra_indent)
    else:
        line.append(" :")
        for cc in val:
            out.append([" " * (indent + extra_indent)])
            RenderRecursivelyToIR(cc, out, indent + extra_indent)
            # extra line between top level nodes
            if field == "body_mod" and not isinstance(cc, cwast.Comment):
                out.append([" " * indent])


def ListIsCompact(val: List):
    if len(val) > 2:
        return False
    for x in val:
        if isinstance(x, cwast.Comment):
            return False
    return True


def RenderList(val: List, field: str, out, indent: str):
    extra_indent = GetExprIndent(field)
    line = out[-1]
    if not val:
        line.append(" []")
    elif ListIsCompact(val):
        line.append(" [")
        sep = ""
        for cc in val:
            line = out[-1]
            line.append(sep)
            sep = " "
            RenderRecursivelyToIR(cc, out, indent + extra_indent)
        out[-1].append("]")

    else:
        line.append(" [")
        for cc in val:
            out.append([" " * (indent + extra_indent)])
            RenderRecursivelyToIR(cc, out, indent + extra_indent)
        out[-1].append("]")


def RenderMacroInvoke(node: cwast.MacroInvoke, out, indent: str):
    line = out[-1]
    line.append("(" + node.name)
    for a in node.args:
        line = out[-1]
        if isinstance(a, cwast.EphemeralList):
            if a.colon:
                RenderColonList(a.args, "dummy", out, indent)
            else:
                RenderList(a.args, "dummy", out, indent)
        else:
            line.append(" ")
            RenderRecursivelyToIR(a, out, indent)
    line = out[-1]
    line.append(")")


def RenderRecursivelyToIR(node, out, indent: str):
    line = out[-1]
    abbrev = MaybeSimplifyLeafNode(node)
    if abbrev:
        line.append(abbrev)
        return

    if isinstance(node, cwast.MacroInvoke):
        RenderMacroInvoke(node, out, indent)
        return
    node_name, fields = GetNodeTypeAndFields(node)
    line.append("(" + node_name)

    for field in fields:
        line = out[-1]
        field_kind = cwast.ALL_FIELDS_MAP[field].kind
        val = getattr(node, field)
        if field_kind is cwast.NFK.FLAG:
            if val:
                line.append(" " + field)
        elif IsFieldWithDefaultValue(field, val):
            continue
        elif field_kind is cwast.NFK.STR:
            line.append(" " + str(val))
        elif field_kind is cwast.NFK.INT:
            line.append(" " + str(val))
        elif field_kind is cwast.NFK.KIND:
            line.append(" " + val.name)
        elif field_kind is cwast.NFK.NODE:
            line.append(" ")
            RenderRecursivelyToIR(val, out, indent)
        elif field_kind is cwast.NFK.LIST:
            if field in ("items", "fields", "body_mod", "body", "body_t", "body_f", "body_for",
                         "cases", "body_macro"):
                RenderColonList(val, field, out, indent)
            else:
                RenderList(val, field, out, indent)
        elif field_kind is cwast.NFK.STR_LIST:
            line.append(f" [{' '.join(val)}]")
        else:
            assert False

    line = out[-1]
    line.append(")")
    # note: comments are not toplevel
    if cwast.NF.TOP_LEVEL in node.FLAGS:
        out.append([""])
    if isinstance(node, cwast.DefMod):
        out.append([""])
        out.append([""])


def PrettyPrint(mod: cwast.DefMod) -> List[Tuple[int, str]]:
    out = [[""]]
    RenderRecursivelyToIR(mod, out, 0)
    for a in out:
        print("".join(a))


############################################################
# Pretty Print HTML
############################################################
def RenderIndent(n):
    return ["<span class=indent>", "&emsp;" * 2 * n, "</span>"]


def CircledLetterEntity(c):
    offset = ord(c.upper()) - ord('A')
    return f"&#{0x24b6 + offset};"


def DecorateNode(node_name, node, tc: types.TypeCorpus):
    problems = []
    if node.x_srcloc is None:
        problems.append("missing srcloc")
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS and node.x_type is None:
        problems.append("missing type")

    out = ["<span class=name>", node_name, "</span>"]
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
        out += ["<span class=type title='",
                tc.canon_name(node.x_type), "'>", CircledLetterEntity("T"), "</span>"]
    if cwast.NF.VALUE_ANNOTATED in node.FLAGS and node.x_value is not None:
        out += ["<span class=value title='",
                str(node.x_value), "'>", CircledLetterEntity("V"), "</span>"]
    if cwast.NF.FIELD_ANNOTATED in node.FLAGS:
        out += [CircledLetterEntity("F")]
    if cwast.NF.CONTROL_FLOW in node.FLAGS:
        out += [CircledLetterEntity("C")]
    if problems:
        out += ["<span class=problems title='",
                "\n".join(problems), "'>", CircledLetterEntity("X"), "</span>"]
    return out


def RenderRecursivelyHTML(node, tc, out, indent: str):
    line = out[-1]
    abbrev = MaybeSimplifyLeafNode(node)
    if abbrev:
        abbrev = abbrev.replace("<", "&lt;").replace(">", "&gt;")
        if isinstance(node, (cwast.ValNum, cwast.ValString, cwast.Id)):
            line.append(abbrev)
        else:
            line += DecorateNode(abbrev, node, tc)
        return

    node_name, fields = GetNodeTypeAndFields(node)
    line += DecorateNode("(" + node_name, node, tc)

    for field in fields:
        line = out[-1]
        field_kind = cwast.ALL_FIELDS_MAP[field].kind
        val = getattr(node, field)
        if field_kind is cwast.NFK.FLAG:
            if val:
                line.append(" " + field)
        elif IsFieldWithDefaultValue(field, val):
            continue
        elif field_kind is cwast.NFK.STR:
            line.append(
                " " + str(val.replace("<", "&lt;").replace(">", "&gt;")))
        elif field_kind is cwast.NFK.INT:
            line.append(" " + str(val))
        elif field_kind is cwast.NFK.KIND:
            line.append(" " + val.name)
        elif field_kind is cwast.NFK.NODE:
            line.append(" ")
            RenderRecursivelyHTML(val, tc, out, indent)
        elif field_kind is cwast.NFK.LIST:
            extra_indent = GetColonIndent(field)
            if not val:
                line.append(" []")
            else:
                line.append(" [")
                for cc in val:
                    out.append(RenderIndent(indent + extra_indent))
                    RenderRecursivelyHTML(cc, tc, out, indent + extra_indent)
                if field == "body_mod" and not isinstance(cc, cwast.Comment):
                    out.append(RenderIndent(indent))
                out[-1].append("]")
        elif field_kind is cwast.NFK.STR_LIST:
            line.append(f" [{' '.join(val)}]")
        else:
            assert False

    line = out[-1]
    line.append(")")
    if cwast.NF.TOP_LEVEL in node.FLAGS:
        out.append(["<p></p>"])


def PrettyPrintHTML(mod: cwast.DefMod, tc) -> List[Tuple[int, str]]:
    out = [[
        """<html>
           <style>
           body { font-family: monospace; }
           span.name { font-weight: bold; }
           </style>"""]
    ]
    RenderRecursivelyHTML(mod, tc, out, 0)
    out += [["</html>"]]
    for a in out:
        print("".join(a))
        print("<br>")
############################################################
#
############################################################


def ConcreteSyntaxExpr(node):
    if isinstance(node, cwast.Id):
        return node.name
    elif isinstance(node, cwast.ValString):
        return node.string
    elif isinstance(node, cwast.ValNum):
        return node.number
    elif isinstance(node, cwast.ValTrue):
        return "true"
    elif isinstance(node, cwast.ValFalse):
        return "false"
    elif isinstance(node, cwast.ValUndef):
        return "undef"
    elif isinstance(node, cwast.ValVoid):
        return "void"
    elif isinstance(node, cwast.Expr2):
        return f"{ConcreteSyntaxExpr(node.expr1)} {node.binary_expr_kind.name} {ConcreteSyntaxExpr(node.expr2)}"
    elif isinstance(node, cwast.ExprPointer):
        return f"{ConcreteSyntaxExpr(node.expr1)} {node.pointer_expr_kind.name} {ConcreteSyntaxExpr(node.expr2)}"
    elif isinstance(node, cwast.ValArray):
        return f"[{ConcreteSyntaxExpr(node.expr_size)}]{ConcreteSyntaxType(node.type)} ..."
    elif isinstance(node, cwast.ExprDeref):
        return f"^{ConcreteSyntaxExpr(node.expr)}"
    elif isinstance(node, cwast.ExprAs):
        return f"{ConcreteSyntaxExpr(node.expr)} as {ConcreteSyntaxType(node.expr)}"
    elif isinstance(node, cwast.ExprCall):
        args = ["..."]
        return f"{ConcreteSyntaxExpr(node.callee)}({', '.join(args)})"
    elif isinstance(node, cwast.ExprIndex):
        return f"[{ConcreteSyntaxExpr(node.expr_index)}]{ConcreteSyntaxExpr(node.container)}"
    else:
        assert False, f"unknown expr node: {type(node)}"


def ConcreteSyntaxType(node) -> str:
    if isinstance(node, cwast.Id):
        return node.name
    elif isinstance(node, cwast.TypeAuto):
        return "auto"
    elif isinstance(node, cwast.TypeBase):
        return node.base_type_kind.name
    elif isinstance(node, cwast.TypePtr):
        return f"*{ConcreteSyntaxType(node.type)}"
    elif isinstance(node, cwast.TypeArray):
        return f"[]{ConcreteSyntaxType(node.type)}"
    else:
        assert False, f"unknown type node: {type(node)}"


def ConcreteSyntaxFunParams(params: List[cwast.FunParam]) -> str:
    out = [f"{p.name} {ConcreteSyntaxType(p.type)}" for p in params]
    return ", ".join(out)

def ConcreteSyntaxColonList(lst, indent):
    if not lst:
        print(" " * (indent + 4) + "pass")
    else:
        for a in lst:
            ConcreteSyntaxStmt(a, indent+4)   
            
def ConcreteSyntaxStmt(node, indent):
    prefix = " " * indent
    if isinstance(node, cwast.Id):
        print(f"{prefix}{node.name}")
    elif isinstance(node, cwast.Comment):
        print(f"{prefix}# {node.comment[1:-1]}")
    elif isinstance(node, cwast.Case):
        print(f"{prefix}case {ConcreteSyntaxExpr(node.cond)}:")
        for c in node.body:
            ConcreteSyntaxStmt(c, indent+4)
    elif isinstance(node, cwast.StmtCond):
        print(f"{prefix}cond:")
        for c in node.cases:
            ConcreteSyntaxStmt(c, indent+4)
    elif isinstance(node, cwast.DefVar):
        print(f"{prefix}let {node.name} {ConcreteSyntaxType(node.type_or_auto)} = {ConcreteSyntaxExpr(node.initial_or_undef)}")
    elif isinstance(node, cwast.StmtCompoundAssignment):
        print(f"{prefix} {ConcreteSyntaxExpr(node.lhs)} {node.assignment_kind} {ConcreteSyntaxExpr(node.expr_rhs)}")
    elif isinstance(node, cwast.StmtAssignment):
        print(f"{prefix} {ConcreteSyntaxExpr(node.lhs)} = {ConcreteSyntaxExpr(node.expr_rhs)}")
    elif isinstance(node, cwast.StmtIf):
        print(f"{prefix}if {ConcreteSyntaxExpr(node.cond)}:")
        ConcreteSyntaxColonList(node.body_t, indent + 4)
        if node.body_f:
            print(f"{prefix}else:")
            ConcreteSyntaxColonList(node.body_f, indent + 4)
    elif isinstance(node, cwast.MacroInvoke):
        print(f"{prefix}{node.name}!", end="")
        sep = " "
        for a in node.args:
            if isinstance(a, cwast.Id):
                print(f"{sep}{a.name}", end="")
            elif isinstance(a, (cwast.EphemeralList)):
                if a.colon:
                    print(":")
                    ConcreteSyntaxColonList(a.args, indent + 4)

                else:
                    print(f"{sep}(", end="")
                    sep2 = ""
                    for a2 in a.args:
                        print(f"{sep2}{ConcreteSyntaxExpr(a2)}", end="")
                    sep2 = ", "
                    print(")", end="")
            elif isinstance(a, (cwast.TypeBase, cwast.TypeAuto, cwast.TypeArray)):
                print(f"{sep}{ConcreteSyntaxType(a)}", end="")
            else:
                print(f"{sep}{ConcreteSyntaxExpr(a)}", end="")
            sep = ", "
        print()
    elif isinstance(node, cwast.StmtReturn):
        print(f"{prefix}return {ConcreteSyntaxExpr(node.expr_ret)}")
    else:
        assert False, f"unknown stmt node: {type(node)}"


def ConcreteSyntaxTop(node, indent):
    prefix = " " * indent
    if isinstance(node, cwast.DefMod):
        print(f"{prefix}module {node.name}")
        print("")
        for child in node.body_mod:
            ConcreteSyntaxTop(child, indent)
    elif isinstance(node, cwast.Comment):
        print(f"{prefix}# {node.comment[1:-1]}")
    elif isinstance(node, cwast.DefGlobal):
        print(f"{prefix}global {node.name} {ConcreteSyntaxType(node.type_or_auto)} = {ConcreteSyntaxExpr(node.initial_or_undef)}")
    elif isinstance(node, cwast.DefFun):
        params = ConcreteSyntaxFunParams(node.params)
        print(
            f"{prefix}fun {node.name}({params}) -> {ConcreteSyntaxType(node.result)}:")
        for child in node.body:
            ConcreteSyntaxStmt(child, indent+4)
    elif isinstance(node, cwast.Import):
        extra = ""
        if node.alias:
            extra = f"as {node.alias}"
        print(f"{prefix}import {node.name}{extra}")
    else:
        assert False, f"unknown node: {type(node)}"


############################################################
#
############################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='pretty_printer')
    parser.add_argument(
        '-mode', type=str, help='mode. one of: reformat, annotate', default="reformat")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)

    mods = parse.ReadModsFromStream(sys.stdin)

    if args.mode == 'reformat':
        for mod in mods:
            PrettyPrint(mod)
    elif args.mode == 'annotate':
        mod_topo_order, mod_map = symbolize.ModulesInTopologicalOrder(mods)
        symbolize.MacroExpansionDecorateASTWithSymbols(mod_topo_order, mod_map)
        for mod in mod_topo_order:
            cwast.StripFromListRecursively(mod, cwast.Comment)
            cwast.StripFromListRecursively(mod, cwast.DefMacro)
        tc = types.TypeCorpus(
            cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
        typify.DecorateASTWithTypes(mod_topo_order, tc)
        eval.DecorateASTWithPartialEvaluation(mod_topo_order)

        for mod in mods:
            PrettyPrintHTML(mod, tc)
    elif args.mode == 'concrete':
        for mod in mods:
            ConcreteSyntaxTop(mod, 0)
    else:
        assert False, f"unknown mode {args.mode}"
