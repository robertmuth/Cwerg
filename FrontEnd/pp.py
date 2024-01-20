#!/usr/bin/python3

"""Pretty printer (PP) for Cwerg AST

"""

import logging
import argparse
import enum
import os
import pathlib

from typing import List, Optional, Tuple

from FrontEnd import cwast
from FrontEnd import parse
from FrontEnd import symbolize
from FrontEnd import typify
from FrontEnd import type_corpus
from FrontEnd import eval
from FrontEnd import mod_pool

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
        quotes = '"""' if node.triplequoted else '"'
        prefix = ""
        if node.strkind == "raw":
            prefix = "r"
        elif node.strkind == "hex":
            prefix = "x"
        return prefix + quotes + node.string + quotes
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


def GetDoc(node):
    for field, _ in node.ATTRS:
        if field == "doc":
            val = getattr(node, "doc")
            return val
    return None


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
            if field == "body_mod":
                out.append([" " * indent])


def ListIsCompact(val: List):
    for v in val:
        if GetDoc(v):
            return False
    if len(val) > 2:
        return False
    # for x in val:
    #    if isinstance(x, cwast.Comment):
    #        return False
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
    if cwast.NF.TOP_LEVEL in node.FLAGS:
        out.append([""])
    line = out[-1]
    abbrev = MaybeSimplifyLeafNode(node)
    if abbrev:
        line.append(abbrev)
        return

    if isinstance(node, cwast.MacroInvoke):
        RenderMacroInvoke(node, out, indent)
        return
    node_name, fields = GetNodeTypeAndFields(node)
    doc = GetDoc(node)

    if doc:
        line.append("@doc ")
        line.append(doc)
        out.append([" " * indent])
        line = out[-1]

    line.append("(" + node_name)

    for field, nfd in node.ATTRS:
        if field == "doc":
            # handled above
            continue
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
            assert False, f"unexpected field {field}"

    line = out[-1]
    line.append(")")

    if isinstance(node, cwast.DefMod):
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


def DecorateNode(node_name, node):
    problems = []
    if node.x_srcloc is None:
        problems.append("missing srcloc")
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS and node.x_type is None:
        problems.append("missing type")

    out = ["<span class=name>", node_name, "</span>"]
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
        out += ["<span class=type title='",
                node.x_type.name, "'>", CircledLetterEntity("T"), "</span>"]
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
            line += DecorateNode(abbrev, node)
        return

    node_name, fields = GetNodeTypeAndFields(node)
    line += DecorateNode("(" + node_name, node)

    for field, nfd in node.ATTRS:
        field_kind = nfd.kind
        val = getattr(node, field)
        if field_kind is cwast.NFK.ATTR_BOOL:
            if val:
                line.append(" " + field)
        elif field_kind is cwast.NFK.ATTR_STR:
            if val:
                pass
                # line.append(" " + field)

    for field, nfd in fields:
        line = out[-1]
        field_kind = nfd.kind
        val = getattr(node, field)

        if cwast.IsFieldWithDefaultValue(field, val):
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
                if field == "body_mod":
                    out.append(RenderIndent(indent))
                out[-1].append("]")
        elif field_kind is cwast.NFK.STR_LIST:
            line.append(f" [{' '.join(val)}]")
        else:
            assert False, f"{node_name} {nfd}"

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


def AddMissingParens(node):
    """Eliminate Array to Slice casts. """

    def replacer(node, parent, _field):
        if isinstance(node, cwast.ExprPointer) and isinstance(parent, cwast.ExprDeref):
            return cwast.ExprParen(node, x_srcloc=node.x_srcloc, x_type=node.x_type)

        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)

############################################################
#
############################################################


@enum.unique
class TK(enum.Enum):
    """TBD"""
    INVALID = 0

    ATTR = 1  # attribute
    ATTR_WITH_SPACE = 4  # attribute

    SEP = 2  # sequence seperator
    SEQ = 3  # sequence element
    BINOP = 6  # binary operator
    UNOP = 7  # unary operator - not space afterwards
    BEG = 8
    END = 10
    BEG_PAREN = 20
    END_PAREN = 21
    BEG_MISC = 30
    END_MISC = 31
    ANNOTATION_SHORT = 11
    ANNOTATION_LONG = 12
    NEWLINE = 13


_POINTER_EXPR_KIND_TO_STR = {
    cwast.POINTER_EXPR_KIND.DECP: "--",
    cwast.POINTER_EXPR_KIND.INCP: "++",
}


_BINARY_EXPR_KIND_TO_STR = {

    cwast.BINARY_EXPR_KIND.ADD: "+",
    cwast.BINARY_EXPR_KIND.SUB: "-",
    cwast.BINARY_EXPR_KIND.MUL: "*",
    cwast.BINARY_EXPR_KIND.DIV: "/",
    cwast.BINARY_EXPR_KIND.REM: "mod",
    cwast.BINARY_EXPR_KIND.MIN: "min",
    cwast.BINARY_EXPR_KIND.MAX: "max",
    #
    cwast.BINARY_EXPR_KIND.OR: "or",
    cwast.BINARY_EXPR_KIND.AND: "and",
    cwast.BINARY_EXPR_KIND.XOR: "xor",

    #
    cwast.BINARY_EXPR_KIND.SHL: "<<",
    cwast.BINARY_EXPR_KIND.SHR: ">>",
    cwast.BINARY_EXPR_KIND.EQ: "==",
    cwast.BINARY_EXPR_KIND.NE: "!=",
    cwast.BINARY_EXPR_KIND.LE: "<",
    cwast.BINARY_EXPR_KIND.LT: "<=",
    cwast.BINARY_EXPR_KIND.GE: ">",
    cwast.BINARY_EXPR_KIND.GT: ">=",
    #
    cwast.BINARY_EXPR_KIND.ANDSC: "&&",
    cwast.BINARY_EXPR_KIND.ORSC: "||",
}

_UNARY_EXPR_KIND_TO_STR = {
    cwast.UNARY_EXPR_KIND.MINUS: "-",
    cwast.UNARY_EXPR_KIND.NOT: "!",

}

_ASSIGNMENT_KIND_TO_STR = {
    cwast.ASSIGNMENT_KIND.ADD: "+=",
    cwast.ASSIGNMENT_KIND.SUB: "-=",
    cwast.ASSIGNMENT_KIND.MUL: "*=",
    cwast.ASSIGNMENT_KIND.DIV: "/=",
    cwast.ASSIGNMENT_KIND.REM: "%=",
    cwast.ASSIGNMENT_KIND.OR: "or=",
    cwast.ASSIGNMENT_KIND.AND: "and=",
    cwast.ASSIGNMENT_KIND.XOR: "xor=",

    cwast.ASSIGNMENT_KIND.SHL: "<<=",
    cwast.ASSIGNMENT_KIND.SHR: ">>=",
}


def Token(a, k):
    if a == "(" or a == "[":
        assert k is TK.BEG_PAREN
    elif a == ")" or a == "]":
        assert k is TK.END_PAREN
    elif a == ":":
        assert k is TK.BEG_MISC
    elif a == "@:":
        assert k is TK.END_MISC
    return (a, k)


def TokensUnaryFunction(name, node):
    yield Token(name, TK.UNOP)
    yield Token("(", TK.BEG_PAREN)
    yield from Tokens(node)
    yield Token(")", TK.END_PAREN)


def TokensBinaryFunction(name, node1, node2):
    yield Token(name, TK.UNOP)
    yield Token("(", TK.BEG_PAREN)
    yield from Tokens(node1)
    yield Token(",", TK.SEP)
    if type(node2) == str:
        yield Token(node2, TK.ATTR)
    else:
        yield from Tokens(node2)
    yield Token(")", TK.END_PAREN)


def TokensBinaryInfix(name: str, node1, node2):
    yield from Tokens(node1)
    yield Token(name, TK.BINOP)
    if type(node2) == str:
        yield Token(node2, TK.ATTR)
    else:
        yield from Tokens(node2)


def TokensUnaryPrefix(name: str, node):
    yield Token(name, TK.UNOP)
    yield from Tokens(node)


def TokensParenList(lst):
    sep = False
    yield Token("(", TK.BEG_PAREN)
    for t in lst:
        if sep:
            yield Token(",", TK.SEP)
        sep = True
        yield from Tokens(t)
    yield Token(")", TK.END_PAREN)


def NameWithParenListExpr(name, lst):
    yield Token(name, TK.UNOP)
    yield from TokensParenList(lst)


def TokensExprtWithParenListExpr(callee, lst):
    yield from Tokens(callee)
    yield from TokensParenList(lst)


def ConcreteExpr3(node: cwast.Expr3):
    yield from Tokens(node.cond)
    yield Token("??", TK.ATTR)
    yield from Tokens(node.expr_t)
    yield Token("!!", TK.ATTR)
    yield from Tokens(node.expr_f)


def TokensMacroInvoke(node: cwast.MacroInvoke):
    if node.name == "->":
        assert len(node.args) == 2
        yield from TokensBinaryInfix("->", node.args[0], node.args[1])
        return
    is_block_like = node.name in ["for", "while", "tryset", "trylet"]
    if is_block_like:
        yield Token(node.name, TK.BEG)
    else:
        if node.x_role is cwast.MACRO_PARAM_KIND.STMT:
            yield Token("NONE", TK.BEG)
        yield Token(node.name, TK.ATTR)
        yield Token("(", TK.BEG_PAREN)
    sep = False
    for a in node.args:

        if isinstance(a, cwast.Id):
            if sep:
                yield Token(",", TK.SEP)
            yield Token(a.name, TK.ATTR)
        elif isinstance(a, (cwast.EphemeralList)):
            if a.colon:
                yield Token(":", TK.BEG_MISC)
                for s in a.args:
                    yield from Tokens(s)
                yield Token("@:", TK.END_MISC)
            else:
                if sep:
                    yield Token(",", TK.SEP)
                sep2 = False
                yield Token("[", TK.BEG_PAREN)
                for e in a.args:
                    if sep2:
                        yield Token(",", TK.SEP)
                    sep2 = True
                    yield from Tokens(e)
                yield Token("]", TK.END_PAREN)
        elif isinstance(a, (cwast.TypeBase, cwast.TypeAuto, cwast.TypeOf,
                            cwast.TypeArray, cwast.TypePtr, cwast.TypeSlice)):
            if sep:
                yield Token(",", TK.SEP)
            yield from Tokens(a)
        else:
            if sep:
                yield Token(",", TK.SEP)
            yield from Tokens(a)
        sep = True
    if is_block_like:
        yield Token(f"@{node.name}", TK.END)
    else:
        yield Token(")", TK.END_PAREN)
        if node.x_role is cwast.MACRO_PARAM_KIND.STMT:
            yield Token("@NONE", TK.END)


def TokensSimpleStmt(kind: str, arg):
    yield Token(kind, TK.BEG)    # return, continue, etc.
    if arg:
        if type(arg) == str:
            yield Token(arg, TK.ATTR)
        elif not isinstance(arg, cwast.ValVoid):
            # for return
            yield from Tokens(arg)

    yield Token("@" + kind, TK.END)


def TokensStmtBlock(kind, arg, stmts):
    yield Token(kind, TK.BEG)
    if arg:
        if type(arg) == str:
            yield Token(arg, TK.ATTR)
        else:
            yield from Tokens(arg)
    yield Token(":", TK.BEG_MISC)
    for s in stmts:
        yield from Tokens(s)
    yield Token("@:", TK.END_MISC)
    yield Token("@" + kind, TK.END)


def TokensStmtSet(kind, lhs, rhs):
    yield Token("set", TK.BEG)
    yield from Tokens(lhs)
    yield Token(kind, TK.BINOP)
    yield from Tokens(rhs)
    yield Token("@set", TK.END)


def TokensStmtLet(kind, name: str, type_or_auto, init_or_auto):
    yield Token(kind, TK.BEG)
    yield Token(name, TK.ATTR)
    yield from Tokens(type_or_auto)
    if not isinstance(init_or_auto, cwast.ValAuto):
        yield Token("=", TK.BINOP)
        yield from Tokens(init_or_auto)
    yield Token("@" + kind, TK.END)


def TokensMacroFor(node: cwast.MacroFor):
    yield Token("$for", TK.BEG)
    yield Token(node.name, TK.ATTR)
    yield Token(node.name_list, TK.ATTR)
    yield Token(":", TK.BEG_MISC)
    for x in node.body_for:
        yield from Tokens(x)
    yield Token("@:", TK.END_MISC)
    yield Token("@$for", TK.END)


def ConcreteIf(node: cwast.StmtIf):
    yield Token("if", TK.BEG)
    yield from Tokens(node.cond)
    yield Token(":", TK.BEG_MISC)
    for c in node.body_t:
        yield from Tokens(c)
    yield Token("@:", TK.END_MISC)
    if node.body_f:
        yield Token("else", TK.ATTR)
        yield Token(":", TK.BEG_MISC)
        for c in node.body_f:
            yield from Tokens(c)
        yield Token("@:", TK.END_MISC)
    yield Token("@if", TK.END)


def TokensValRec(node: cwast.ValRec):
    yield from Tokens(node.type)
    yield Token("[", TK.BEG_PAREN)
    sep = False
    for e in node.inits_field:
        if sep:
            yield Token(",", TK.SEP)
        sep = True
        yield from Tokens(e.value_or_undef)
        if e.init_field:
            yield Token(e.init_field, TK.ATTR)
    yield Token("]", TK.END_PAREN)


def TokensValArray(node: cwast.ValArray):
    yield from TokensBinaryFunction("array", node.expr_size, node.type)
    yield Token("[", TK.BEG_PAREN)
    sep = False
    for e in node.inits_array:
        assert isinstance(e, cwast.IndexVal)
        if sep:
            yield Token(",", TK.SEP)
        sep = True
        yield from Tokens(e.value_or_undef)
        if not isinstance(e.init_index, cwast.ValAuto):
            yield from Tokens(e.init_index)
    yield Token("]", TK.END_PAREN)


def TokensDefMod(node: cwast.DefMod):
    yield Token("module", TK.BEG)
    # we do not want the next item to be indented
    yield Token(node.name, TK.UNOP)
    for child in node.body_mod:
        yield from Tokens(child)
    yield Token("@module", TK.END)


def TokensDefGlobal(node: cwast.DefGlobal):
    yield Token("global", TK.BEG)
    yield Token(node.name, TK.ATTR)
    yield from Tokens(node.type_or_auto)
    if not isinstance(node.initial_or_undef_or_auto, cwast.ValAuto):
        yield Token("=", TK.BINOP)
        yield from Tokens(node.initial_or_undef_or_auto)
    yield Token("@global", TK.END)


def TokensImport(node: cwast.Import):
    yield Token("import", TK.BEG)
    yield Token(node.name, TK.ATTR)
    if node.alias:
        yield Token("as", TK.BINOP)
        yield Token(node.alias, TK.ATTR)
    yield Token("@import", TK.END)


def TokensDefType(node: cwast.DefType):
    yield Token("type", TK.BEG)
    yield Token(node.name, TK.ATTR)
    yield Token("=", TK.BINOP)
    yield from Tokens(node.type)
    yield Token("@type", TK.END)


def TokensTypeFun(node: cwast.TypeFun):
    yield Token("funtype", TK.UNOP)
    yield Token("(", TK.BEG_PAREN)
    sep = False
    for p in node.params:
        if sep:
            yield Token(",", TK.SEP)
        sep = True
        yield Token(p.name, TK.ATTR)
        yield from Tokens(p.type)
    yield Token(")", TK.END_PAREN)
    yield from Tokens(node.result)


def TokensDefRec(node: cwast.DefRec):
    yield Token("rec", TK.BEG)
    yield Token(node.name, TK.ATTR)
    yield Token(":", TK.BEG_MISC)
    for f in node.fields:
        yield from TokensAnnotations(f)
        yield Token("NONE", TK.BEG)
        yield Token(f.name, TK.ATTR)
        yield from Tokens(f.type)
        yield Token("@NONE", TK.END)
    yield Token("@:", TK.END_MISC)
    yield Token("@rec", TK.END)


def TokensDefEnum(node: cwast.DefEnum):
    yield Token("enum", TK.BEG)
    yield Token(node.name, TK.ATTR)
    yield Token(node.base_type_kind.name, TK.ATTR)
    yield Token(":", TK.BEG_MISC)
    for f in node.items:
        yield Token("NONE", TK.BEG)
        yield Token(f.name, TK.ATTR)
        yield from Tokens(f.value_or_auto)
        yield Token("@NONE", TK.END)
    yield Token("@:", TK.END_MISC)
    yield Token("@enum", TK.END)


def TokensStaticAssert(node: cwast.StmtStaticAssert):
    yield Token("static_assert", TK.BEG)
    yield from Tokens(node.cond)
    yield Token("@static_assert", TK.END)


def TokensDefFun(node: cwast.DefFun):
    yield Token("fun", TK.BEG)
    yield Token(node.name, TK.ATTR)

    yield ("(", TK.BEG_PAREN)
    sep = False
    for p in node.params:
        if sep:
            yield Token(",", TK.SEP)
        sep = True
        yield Token(p.name, TK.ATTR)
        yield from Tokens(p.type)
    yield Token(")", TK.END_PAREN)
    yield from Tokens(node.result)
    yield Token(":", TK.BEG_MISC)
    for child in node.body:
        yield from Tokens(child)
    yield Token("@:", TK.END_MISC)
    yield Token("@fun", TK.END)


def TokensDefMacro(node: cwast.DefMacro):
    yield Token("macro", TK.BEG)
    yield Token(node.name, TK.ATTR)
    yield Token(node.macro_result_kind.name, TK.ATTR)
    yield Token("[", TK.BEG_PAREN)
    sep = False
    for p in node.params_macro:
        if sep:
            yield Token(",", TK.SEP)
        sep = True
        yield Token(p.name, TK.ATTR)
        yield Token(p.macro_param_kind.name, TK.ATTR)
    yield Token("]", TK.END_PAREN)
    #
    yield Token("[", TK.BEG_PAREN)
    sep = False
    for gen_id in node.gen_ids:
        if sep:
            yield Token(",", TK.SEP)
        sep = True
        yield Token(gen_id, TK.ATTR)
    yield Token("]", TK.END_PAREN)
    yield Token(":", TK.BEG_MISC)
    for x in node.body_macro:
        yield from Tokens(x)
    yield Token("@:", TK.END_MISC)
    yield Token("@macro", TK.END)


def TokensMacroId(node: cwast.MacroId):
    if node.x_role is cwast.MACRO_PARAM_KIND.STMT:
        yield Token("NONE", TK.BEG)
        yield Token(node.name, TK.ATTR)
        yield Token("@NONE", TK.END)
    else:
        yield Token(node.name, TK.ATTR)


CONCRETE_SYNTAX = {
    cwast.Id: lambda n:  (yield Token(n.name, TK.ATTR)),
    #
    cwast.MacroId: TokensMacroId,
    cwast.MacroInvoke: TokensMacroInvoke,
    cwast.MacroVar: lambda n: TokensStmtLet("$let", n.name, n.type_or_auto, n.initial_or_undef_or_auto),
    cwast.MacroFor: TokensMacroFor,
    #
    cwast.TypeAuto: lambda n: (yield Token("auto", TK.ATTR)),
    cwast.TypeBase: lambda n: (yield Token(n.base_type_kind.name.lower(), TK.ATTR)),
    cwast.TypeSlice: lambda n: TokensUnaryFunction("slice", n.type),
    cwast.TypeOf: lambda n: TokensUnaryFunction("typeof", n.expr),
    cwast.TypeUnion: lambda n: NameWithParenListExpr("union", n.types),
    cwast.TypePtr: lambda n: TokensUnaryFunction("ptr", n.type),
    cwast.TypeArray: lambda n: TokensBinaryFunction("array", n.size, n.type),
    cwast.TypeUnionDelta: lambda n: TokensBinaryFunction("uniondelta", n.type, n.subtrahend),
    cwast.TypeFun:  TokensTypeFun,
    #
    cwast.ValNum: lambda n: (yield Token(n.number, TK.ATTR)),
    cwast.ValTrue: lambda n: (yield Token("true", TK.ATTR)),
    cwast.ValFalse: lambda n: (yield Token("false", TK.ATTR)),
    cwast.ValUndef: lambda n: (yield Token("undef", TK.ATTR)),
    cwast.ValVoid: lambda n: (yield Token("void", TK.ATTR)),
    cwast.ValAuto: lambda n: (yield Token("auto", TK.ATTR)),
    cwast.ValString: lambda n: (yield Token(f'{n.strkind}"{n.string}"', TK.ATTR)),
    cwast.ValRec: TokensValRec,
    cwast.ValArray: TokensValArray,

    #
    cwast.ExprFront: lambda n: TokensUnaryFunction("front", n.container),
    cwast.ExprUnionTag: lambda n: TokensUnaryFunction("uniontag", n.expr),
    cwast.ExprAs: lambda n: TokensBinaryFunction("as", n.expr, n.type),
    cwast.ExprIs: lambda n: TokensBinaryInfix("is", n.expr, n.type),
    cwast.ExprBitCast: lambda n: TokensBinaryFunction("asbits", n.expr, n.type),
    cwast.ExprOffsetof: lambda n: TokensBinaryFunction("offsetof", n.type, n.field),
    cwast.ExprLen: lambda n: TokensUnaryFunction("len", n.container),
    cwast.ExprSizeof: lambda n: TokensUnaryFunction("sizeof", n.type),
    cwast.ExprTypeId: lambda n: TokensUnaryFunction("sizeof", n.type),
    cwast.ExprNarrow: lambda n: TokensBinaryFunction("narrowto", n.expr, n.type),
    cwast.Expr1: lambda n: TokensUnaryPrefix(_UNARY_EXPR_KIND_TO_STR[n.unary_expr_kind], n.expr),
    cwast.ExprPointer: lambda n: TokensBinaryInfix(_POINTER_EXPR_KIND_TO_STR[n.pointer_expr_kind], n.expr1, n.expr2),
    cwast.ExprIndex: lambda n: TokensBinaryInfix("at", n.container, n.expr_index),
    cwast.ValSlice: lambda n: TokensBinaryFunction("slice", n.pointer, n.expr_size),
    cwast.ExprWrap: lambda n: TokensBinaryFunction("wrapas", n.expr, n.type),
    cwast.ExprUnwrap: lambda n: TokensUnaryFunction("unwrap", n.expr),
    cwast.ExprField: lambda n: TokensBinaryInfix(".", n.container, n.field),
    cwast.ExprDeref: lambda n: TokensUnaryPrefix("^", n.expr),
    cwast.ExprAddrOf: lambda n: TokensUnaryPrefix("&", n.expr_lhs),
    cwast.Expr2: lambda n: TokensBinaryInfix(_BINARY_EXPR_KIND_TO_STR[n.binary_expr_kind],
                                             n.expr1, n.expr2),
    cwast.Expr3: ConcreteExpr3,
    cwast.ExprStringify: lambda n: TokensUnaryFunction("stringify", n.expr),
    cwast.ExprCall: lambda n: TokensExprtWithParenListExpr(n.callee, n.args),
    cwast.ExprStmt: lambda n: TokensStmtBlock("expr", "", n.body),
    cwast.ExprParen: lambda n: TokensParenList([n.expr]),

    #
    cwast.StmtContinue: lambda n: TokensSimpleStmt("continue", n.target),
    cwast.StmtBreak: lambda n: TokensSimpleStmt("break", n.target),
    cwast.StmtTrap: lambda n: TokensSimpleStmt("trap", ""),
    cwast.StmtReturn: lambda n: TokensSimpleStmt("return", n.expr_ret),
    cwast.StmtExpr: lambda n: TokensSimpleStmt("shed", n.expr),
    cwast.StmtDefer: lambda n: TokensStmtBlock("defer", "", n.body),
    cwast.StmtBlock: lambda n: TokensStmtBlock("block", n.label, n.body),
    cwast.Case: lambda n: TokensStmtBlock("case", n.cond, n.body),

    cwast.StmtCond: lambda n: TokensStmtBlock("cond", "", n.cases),
    cwast.StmtCompoundAssignment: lambda n: TokensStmtSet(_ASSIGNMENT_KIND_TO_STR[n.assignment_kind],
                                                          n.lhs, n.expr_rhs),
    cwast.StmtAssignment: lambda n: TokensStmtSet("=", n.lhs, n.expr_rhs),
    cwast.DefVar: lambda n: TokensStmtLet("let", n.name, n.type_or_auto, n.initial_or_undef_or_auto),
    cwast.StmtIf: ConcreteIf,
    #
    cwast.DefMod: TokensDefMod,
    cwast.DefGlobal: TokensDefGlobal,
    cwast.Import: TokensImport,
    cwast.DefType: TokensDefType,
    cwast.DefFun: TokensDefFun,
    cwast.DefEnum: TokensDefEnum,
    cwast.DefRec: TokensDefRec,
    cwast.StmtStaticAssert: TokensStaticAssert,
    cwast.DefMacro: TokensDefMacro,
}


def TokensAnnotations(node):
    for field, nfd in node.ATTRS:
        if field in ("triplequoted", "strkind"):
            continue
        if nfd.kind is cwast.NFK.ATTR_STR:
            val = getattr(node, field)
            if val:
                yield Token("@" + field + "=" + val, TK.ANNOTATION_LONG)

    for field, nfd in node.ATTRS:
        if field in ("triplequoted", "strkind"):
            continue

        if nfd.kind is cwast.NFK.ATTR_BOOL:
            val = getattr(node, field)
            if val:
                yield Token("@" + field, TK.ANNOTATION_SHORT)


def Tokens(node):
    if isinstance(node, (cwast.DefRec, cwast.DefEnum, cwast.DefFun, cwast.DefType, cwast.Import,
                         cwast.DefGlobal, cwast.DefMacro, cwast.StmtStaticAssert)):
        yield Token("", TK.NEWLINE)

    yield from TokensAnnotations(node)

    gen = CONCRETE_SYNTAX.get(node.__class__)
    assert gen, f"unknown node {node.__class__}"
    yield from gen(node)


BEG_TOKENS = set([
    "module", "global", "enum", "import", "defer", "block", "expr",
    "break", "continue", "fun", "cond", "type", "if", "type",
    "shed", "discard", "rec", "case", "let", "set", "for", "macro",
    "while", "try", "trylet", "trap", "return", "NONE", "static_assert",
    "$let", "$for", "swap", ":", "(", "[",
])


class Stack:
    """TBD"""

    def __init__(self):
        self._stack = []

    def empty(self):
        return 0 == len(self._stack)

    def push(self, t: str, kind, indent_delta: int) -> int:
        assert t.endswith("!") or t in BEG_TOKENS, f"{t}"
        new_indent = self.CurrentIndent() + indent_delta
        self._stack.append((t, kind, new_indent))
        return new_indent

    def pop(self):
        return self._stack.pop(-1)

    def CurrentIndent(self) -> int:
        for _, kind, i in reversed(self._stack):
            if kind in (TK.BEG_MISC, TK.BEG, TK.BEG_PAREN):
                return i
        return 0


class Sink:
    """TBD"""

    def __init__(self):
        self._indent = 0
        self._col = 0

    def maybe_newline(self):
        if self._col != 0:
            self.newline()

    def newline(self):
        print()
        self._col = 0

    def emit_token(self, token):
        if self._col == 0:
            ws = " " * (4 * self._indent)
            # ws = f"{len(ws):02}" + ws[2:]
            print(ws, end="")
            self._col = len(ws)
        print(token, end="")
        self._col += len(token)

    def emit_space(self):
        self.emit_token(" ")

    def set_indent(self, indent):
        self._indent = indent


INDENT = 1


def FormatTokenStream(tokens, stack: Stack, sink: Sink):
    """
    TK.BEG may force a new indentation level

    """
    want_space = False

    while True:
        t, kind = tokens.pop(-1)
        if kind is TK.BEG:
            # want_space = False
            # sink.maybe_newline()
            assert t in BEG_TOKENS or t.endswith("!"), f"bad BEG token {t}"
            if t == "module":
                assert stack.empty()
                sink.emit_token(t)
                want_space = True
                stack.push(t, kind, 0)

            elif t.endswith("!"):
                sink.emit_token(t)
                stack.push(t, kind, 0)
            else:
                if want_space:
                    sink.emit_space()
                    want_space = False
                if t != "NONE":
                    sink.emit_token(t)
                    want_space = True
                stack.push(t, kind, 0)
        elif kind is TK.BEG_MISC:
            want_space = False
            sink.emit_token(t)
            sink.newline()
            indent = stack.push(t, kind, INDENT)
            sink.set_indent(indent)
        elif kind is TK.BEG_PAREN:
            want_space = False
            sink.emit_token(t)
            stack.push(t, kind, 0)
        elif kind is TK.ATTR:
            assert type(t) is str, repr(t)
            if t == "else":
                # ci = stack.CurrentIndent()
                # sink.indent(ci)
                sink.emit_token(t)
            else:
                if want_space:
                    sink.emit_space()
                    want_space = False
                sink.emit_token(t)
                want_space = True
        elif kind is TK.ATTR_WITH_SPACE:
            sink.emit_token(t)
            sink.emit_space()
        elif kind is TK.SEP:
            sink.emit_token(t)
            sink.emit_space()
            want_space = False
        elif kind is TK.END:
            t_beg, kind_beg, _ = stack.pop()
            sink.set_indent(stack.CurrentIndent())
            assert kind_beg is TK.BEG
            assert t.startswith("@")
            assert t[1:] == t_beg, f"{t_beg} vs {t}"
            if t_beg == "module":
                sink.newline()
                assert not tokens
                assert stack.empty()
                return
            sink.maybe_newline()
            want_space = False
        elif kind is TK.END_MISC:
            t_beg, kind_beg, _ = stack.pop()
            sink.set_indent(stack.CurrentIndent())
            assert kind_beg is TK.BEG_MISC
            sink.maybe_newline()
            want_space = False
        elif kind is TK.END_PAREN:
            t_beg, kind_beg, _ = stack.pop()
            sink.set_indent(stack.CurrentIndent())
            assert kind_beg is TK.BEG_PAREN
            sink.emit_token(t)
            want_space = True
        elif kind is TK.BINOP:
            if t == "." or t == "->":
                sink.emit_token(t)
                want_space = False
            else:
                if want_space:
                    sink.emit_space()
                sink.emit_token(t)
                want_space = True
        elif kind is TK.UNOP:
            if want_space:
                sink.emit_space()
                want_space = False
            sink.emit_token(t)
        elif kind is TK.NEWLINE:
            sink.newline()
        elif kind is TK.ANNOTATION_LONG:
            sink.maybe_newline()
            sink.emit_token(t)
            sink.newline()
        elif kind is TK.ANNOTATION_SHORT:
            if want_space:
                sink.emit_space()
                want_space = False
            sink.emit_token(t)
            want_space = True
        else:
            assert False, f"{kind}"
        assert tokens, f"{t} {kind}"
        # TODO: this stopped working after comment support was added
        # assert stack._stack[0][0] == "module", stack._stack[0][1] == TK.BEG


############################################################
#
############################################################
def main():
    parser = argparse.ArgumentParser(description='pretty_printer')
    parser.add_argument(
        '-mode', type=str, help='mode. one of: reformat, annotate, concrete', default="reformat")
    parser.add_argument('files', metavar='F', type=str, nargs='+',
                        help='an input source file')
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    assert len(args.files) == 1
    assert args.files[0].endswith(".cw")

    if args.mode == 'reformat':
        with open(args.files[0], encoding="utf8") as f:
            mods = parse.ReadModsFromStream(f)
            assert len(mods) == 1
            PrettyPrint(mods[0])
    elif args.mode == 'annotate':
        cwd = os.getcwd()
        mp: mod_pool.ModPool = mod_pool.ModPool(pathlib.Path(cwd) / "Lib")
        mp.InsertSeedMod("builtin")
        mp.InsertSeedMod(str(pathlib.Path(args.files[0][:-3]).resolve()))
        mp.ReadAndFinalizedMods()

        mod_topo_order = mp.ModulesInTopologicalOrder()
        symbolize.MacroExpansionDecorateASTWithSymbols(mod_topo_order)
        for mod in mod_topo_order:
            cwast.StripFromListRecursively(mod, cwast.DefMacro)
        tc = type_corpus.TypeCorpus(type_corpus.STD_TARGET_X64)
        typify.DecorateASTWithTypes(mod_topo_order, tc)
        eval.DecorateASTWithPartialEvaluation(mod_topo_order)

        for mod in mod_topo_order:
            PrettyPrintHTML(mod, tc)
    elif args.mode == 'concrete':
        with open(args.files[0], encoding="utf8") as f:
            mods = parse.ReadModsFromStream(f)
            assert len(mods) == 1
            for m in mods:
                assert isinstance(m, cwast.DefMod)
                cwast.AnnotateRole(m)
                AddMissingParens(m)
                cwast.CheckAST(m, set(), pre_symbolize=True)
            # we first produce an output token stream from the AST
            tokens = Tokens(mods[0])
            tokens = list(tokens)
            # print(tokens)
            tokens.reverse()
            # and now format the stream
            FormatTokenStream(tokens, Stack(), Sink())
    else:
        assert False, f"unknown mode {args.mode}"


if __name__ == "__main__":
    main()
