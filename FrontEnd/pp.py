#!/usr/bin/python3

"""Pretty printer (PP) for Cwerg AST

"""

import sys
import logging
import argparse
import enum

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
    elif isinstance(node, cwast.MacroId):
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
        prefix = "r" if node.raw else ""
        return prefix + node.string
    else:
        return None


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

    for field, nfd in node.ATTRS:
        val = getattr(node, field)
        if val:
            line.append(" @" + field)

    for field, nfd in fields:
        field_kind = nfd.kind
        line = out[-1]
        val = getattr(node, field)

        if cwast.IsFieldWithDefaultValue(field, val):
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

    for field, nfd in fields:
        line = out[-1]
        field_kind = nfd.kind
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
            assert False, f"{name} {nfd}"

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


@enum.unique
class TK(enum.Enum):
    INVALID = 0

    ATTR = 1  # attribute
    SEP = 2  # sequence seperator
    SEQ = 3  # sequence element
    COM = 4  # comment
    MCOM = 5  # multi line comment
    BINOP = 6  # binary operator
    UNOP = 7  # unary operator
    BEG = 8
    BEG_WITH_SEP = 9
    END = 10


def ConcreteSyntaxExpr(node):
    if isinstance(node, cwast.Id):
        yield node.name, TK.ATTR
    elif isinstance(node, cwast.ValString):
        yield node.string, TK.ATTR
    elif isinstance(node, cwast.ValNum):
        yield node.number, TK.ATTR
    elif isinstance(node, cwast.ValTrue):
        yield "true", TK.ATTR
    elif isinstance(node, cwast.ValFalse):
        yield "false", TK.ATTR
    elif isinstance(node, cwast.ValUndef):
        yield "undef", TK.ATTR
    elif isinstance(node, cwast.ValVoid):
        yield "void", TK.ATTR
    elif isinstance(node, cwast.Expr2):
        yield from ConcreteSyntaxExpr(node.expr1)
        yield "{node.binary_expr_kind.name}", cwast.BINOP
        yield from ConcreteSyntaxExpr(node.expr2)
    elif isinstance(node, cwast.ExprPointer):
        yield from ConcreteSyntaxExpr(node.expr1)
        yield "{node.pointer_expr_kind.name}", cwast.BINOP
        yield from ConcreteSyntaxExpr(node.expr2)
    elif isinstance(node, cwast.ValArray):
        yield "[", TK.BEG
        yield from ConcreteSyntaxExpr(node.expr_size)
        yield "]", TK.END
        yield from ConcreteSyntaxType(node.type)
        # TODO
    elif isinstance(node, cwast.ExprDeref):
        yield "^", cwast.UNOP
        yield from ConcreteSyntaxExpr(node.expr)
    elif isinstance(node, cwast.ExprAs):
        yield from ConcreteSyntaxExpr(node.expr)
        yield "as", TK.BINOP
        yield from ConcreteSyntaxType(node.expr)
    elif isinstance(node, cwast.ExprCall):
        yield from ConcreteSyntaxExpr(node.calleee)
        yield "(", cwast.BEG_WITH_SEP
        sep = False
        for e in node.args:
            if sep:
                yield ",", TK.SEP
            sep = True
            yield from ConcreteSyntaxExpr(e)
        yield ")", cwast.END
    elif isinstance(node, cwast.ExprIndex):
        yield "[", cwast.BEG
        yield from ConcreteSyntaxExpr(node.expr_index)
        yield "]", cwast.END
        yield from ConcreteSyntaxExpr(node.container)
    else:
        assert False, f"unknown expr node: {type(node)}"


def ConcreteSyntaxType(node):
    if isinstance(node, cwast.Id):
        yield node.name, TK.ATTR
    elif isinstance(node, cwast.TypeAuto):
        yield "auto", TK.ATTR
    elif isinstance(node, cwast.TypeBase):
        yield node.base_type_kind.name, TK.ATTR
    elif isinstance(node, cwast.TypePtr):
        yield "*", TK.UNOP
        yield from ConcreteSyntaxType(node.type)
    elif isinstance(node, cwast.TypeArray):
        yield "[", TK.BEG
        yield from ConcreteSyntaxExpr(node.expr_size)
        yield "]", TK.END
        yield from ConcreteSyntaxType(node.type)
    else:
        assert False, f"unknown type node: {type(node)}"


def ConcreteSyntaxComment(node: cwast.Comment):
    if node.comment.startswith('"""'):
        yield (node.comment[3:-3], TK.MCOM)
    else:
        yield (node.comment[1:-1], TK.COM)


def ConcreteSyntaxStmt(node):
    if isinstance(node, cwast.Id):
        yield (node.name, TK.ATTR)
    elif isinstance(node, cwast.Comment):
        yield from ConcreteSyntaxComment(node)
    elif isinstance(node, cwast.Case):
        yield ("case", TK.BEG)

        ConcreteSyntaxExpr(node.cond)
        yield (":", TK.BEG)
        for c in node.body:
            yield from ConcreteSyntaxStmt(c)
        yield ("", TK.END)
        yield ("", TK.END)

    elif isinstance(node, cwast.StmtCond):
        yield ("cond", TK.BEG)
        yield (":", TK.BEG)
        for c in node.cases:
            yield from ConcreteSyntaxStmt(c)
        yield ("", TK.END)
        yield ("", TK.END)
    elif isinstance(node, cwast.DefVar):
        yield ("let", TK.BEG)
        yield (node.name, TK.ATTR)
        yield from ConcreteSyntaxType(node.type_or_auto)
        if not isinstance(node.initial_or_undef_or_auto, cwast.VaLAuto):
            yield ("=", TK.BINOP)
            yield from ConcreteSyntaxExpr(node.initial_or_undef_or_auto)
        yield ("", TK.END)
    elif isinstance(node, cwast.StmtCompoundAssignment):
        yield ("set", TK.BEG)
        yield from ConcreteSyntaxExpr(node.lhs)
        yield f"={node.assignment_kind}", TK.BINOP
        yield from ConcreteSyntaxExpr(node.expr_rhs)
    elif isinstance(node, cwast.StmtAssignment):
        yield ("set", TK.BEG)
        yield from ConcreteSyntaxExpr(node.lhs)
        yield f"=", TK.BINOP
        yield ConcreteSyntaxExpr(node.expr_rhs)
    elif isinstance(node, cwast.StmtIf):
        yield ("if", TK.BEG)
        yield from ConcreteSyntaxExpr(node.cond)
        yield (":", TK.BEG)
        for c in node.body_t:
            yield from ConcreteSyntaxStmt(c)
        yield (":", TK.BEG)
        if node.body_f:
            yield ("else", TK.ATTR)
            yield (":", TK.BEG)
            for c in node.body_f:
                yield ConcreteSyntaxStmt(c)
            yield ("", TK.END)
        yield ("", TK.END)
    elif isinstance(node, cwast.MacroInvoke):
        yield f"{node.name}!", TK.BEG_WITH_SEP
        sep = False
        for a in node.args:
            if sep:
                yield ",", TK.SEP
            sep = True
            if isinstance(a, cwast.Id):
                yield a.name, TK.ATTR
            elif isinstance(a, (cwast.EphemeralList)):
                if a.colon:
                    yield ":", TK.BEG
                    for s in a.args:
                        yield from ConcreteSyntaxStmt(s)
                    yield "", TK.END
                else:
                    sep2 = False
                    yield "[", TK.BEG_WITH_SEP
                    for e in a.args:
                        if sep2:
                            yield ",", TK.SEP
                        sep2 = True
                        yield from ConcreteSyntaxExpr(e)
                    yield "]", TK.END
            elif isinstance(a, (cwast.TypeBase, cwast.TypeAuto, cwast.TypeArray)):
                yield from ConcreteSyntaxType(a)
            else:
                yield from ConcreteSyntaxExpr(a)
        yield "", TK.END
    elif isinstance(node, cwast.StmtReturn):
        yield "return", TK.BEG
        yield from ConcreteSyntaxExpr(node.expr_ret)
        yield ("", TK.END)

    else:
        assert False, f"unknown stmt node: {type(node)}"


def ConcreteSyntaxTop(node):
    if isinstance(node, cwast.DefMod):
        yield ("module", TK.BEG)
        yield (node.name, TK.ATTR)
        for child in node.body_mod:
            yield from ConcreteSyntaxTop(child)
        yield ("", TK.END)

    elif isinstance(node, cwast.Comment):
        yield from ConcreteSyntaxComment(node)

    elif isinstance(node, cwast.DefGlobal):
        yield ("global", TK.BEG)
        yield (node.name, TK.ATTR)
        yield from ConcreteSyntaxType(node.type_or_auto)
        if not isinstance(node.initial_or_undef_or_auto, cwast.ValAuto):
            yield ("=", TK.BINOP)
            yield from ConcreteSyntaxExpr(node.initial_or_undef_or_auto)
        yield ("", TK.END)
    elif isinstance(node, cwast.DefFun):
        yield ("fun", TK.BEG)
        yield (node.name, TK.ATTR)

        yield ("(", TK.BEG_WITH_SEP)
        sep = False
        for p in node.params:
            if sep:
                yield ",", TK.SEP
            sep = True
            yield (p.name, TK.ATTR)
            yield from ConcreteSyntaxType(p.type)
        yield (")", TK.END)

        yield from ConcreteSyntaxType(node.result)
        yield (":", TK.BEG)

        for child in node.body:
            yield from ConcreteSyntaxStmt(child)
        yield ("", TK.END)
        yield ("", TK.END)

    elif isinstance(node, cwast.Import):
        yield ("import", TK.BEG)
        yield (node.name, TK.ATTR)
        if node.alias:
            yield ("as", TK.BINOP)
            yield (node.alias, TK.ATTR)
        yield ("", TK.END)

    elif isinstance(node, cwast.DefRec):
        pass
    else:
        assert False, f"unknown node: {type(node)}"


BEG_TOKENS = set(["module", "global", "fun", "cond", "if",
                 "case", "let", "set", "return", ":"])
BEG_WITH_SEP_TOKENS = set(["(", "["])
END_TOKENS = set(["", ")", "]"])


def GetCurrentIndent(stack) -> int:
    for t, kind, i in reversed(stack):
        if kind is TK.BEG:
            return i * 4
    assert False


def FormatTokenStream(tokens, stack, col):
    t, kind = tokens.pop(-1)
    if kind is TK.BEG:
        assert t in BEG_TOKENS, f"bad BEG token {t}"
        if t == "module":
            assert not stack
            print(t, end="")
            stack.append((t, kind, 0))
        elif t == ":":
            print(" ", t, end="")
        else:
            print()

            ci = GetCurrentIndent(stack)
            print(" " * ci, t, end="")
            stack.append((t, kind, ci + 1))
    elif kind is TK.BEG_WITH_SEP:
        assert t in BEG_WITH_SEP_TOKENS or t.endswith(
            "!"), f"bad BEG token {t}"
        ci = GetCurrentIndent(stack)
        stack.append((t, kind, ci + 1))
        print(" ", t, end="")
    elif kind is TK.ATTR:
        print(" ", t, end="")
        col += 1 + len(t)
    elif kind is TK.SEP:
        print(" ", t, end="")
        col += 1 + len(t)
    elif kind is TK.END:
        assert t in END_TOKENS, f"bad END token {t}"
        beg = stack.pop(-1)
        if beg[0] == "module":
            assert not stack
            return
        print(" ", t)
    FormatTokenStream(tokens, stack, col)


############################################################
#
############################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='pretty_printer')
    parser.add_argument(
        '-mode', type=str, help='mode. one of: reformat, annotate, concrete', default="reformat")
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
            tokens = ConcreteSyntaxTop(mod)
            tokens = list(tokens)
            tokens.reverse()
            FormatTokenStream(tokens, [], 0)
    else:
        assert False, f"unknown mode {args.mode}"
