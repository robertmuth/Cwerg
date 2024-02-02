#!/usr/bin/python3

"""Pretty printer (PP) for Cwerg AST

"""

import logging
import argparse
import enum
import os
import pathlib
import dataclasses

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
        return cwast.ASSIGNMENT_SHORTCUT_INV[node.assignment_kind], fields
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

    line.append("(")

    for field, nfd in node.ATTRS:
        if field == "doc":
            # handled above
            continue
        val = getattr(node, field)
        if val:
            line.append("@" + field + " ")

    line.append(node_name)

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


def PrettyPrintHTML(mod: cwast.DefMod, tc):  # -> List[Tuple[int, str]]:
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
_OPS_PRECENDENCE = {
    # "->": 10,
    cwast.ExprField: 10,
    cwast.ExprAs: 10,
    #
    cwast.Expr1: 11,
    cwast.ExprDeref: 11,
    cwast.ExprAddrOf: 11,

    cwast.ExprIs: 50,
}

_OPS_PRECENDENCE_EXPR2 = {
    cwast.BINARY_EXPR_KIND.SHL: 20,
    cwast.BINARY_EXPR_KIND.ROTL: 20,
    cwast.BINARY_EXPR_KIND.SHR: 20,
    cwast.BINARY_EXPR_KIND.ROTR: 20,
    #
    cwast.BINARY_EXPR_KIND.MUL: 30,
    cwast.BINARY_EXPR_KIND.DIV: 30,
    cwast.BINARY_EXPR_KIND.MOD: 30,
    cwast.BINARY_EXPR_KIND.AND: 30,
    cwast.BINARY_EXPR_KIND.XOR: 30,
    #
    cwast.BINARY_EXPR_KIND.OR: 35,
    cwast.BINARY_EXPR_KIND.ADD: 35,
    cwast.BINARY_EXPR_KIND.SUB: 35,
    #
    cwast.BINARY_EXPR_KIND.MAX: 40,
    cwast.BINARY_EXPR_KIND.MIN: 40,
    #
    cwast.BINARY_EXPR_KIND.GE: 60,
    cwast.BINARY_EXPR_KIND.GT: 60,
    cwast.BINARY_EXPR_KIND.LE: 60,
    cwast.BINARY_EXPR_KIND.LT: 60,
    cwast.BINARY_EXPR_KIND.EQ: 65,
    cwast.BINARY_EXPR_KIND.NE: 65,
    #
    cwast.BINARY_EXPR_KIND.ANDSC: 70,
    cwast.BINARY_EXPR_KIND.ORSC: 75,
}


def _NodeNeedsParen(node, parent, field: str):
    if isinstance(parent, cwast.Expr2):
        if field == "expr1":
            if isinstance(node, cwast.Expr2):
                return _OPS_PRECENDENCE_EXPR2[node.binary_expr_kind] > _OPS_PRECENDENCE_EXPR2[parent.binary_expr_kind]
        if field == "expr2":
            if isinstance(node, cwast.Expr2):
                return _OPS_PRECENDENCE_EXPR2[node.binary_expr_kind] > _OPS_PRECENDENCE_EXPR2[parent.binary_expr_kind]

    return False


def AddMissingParens(node):
    """Eliminate Array to Slice casts. """

    def replacer(node, parent, field: str):
        if _NodeNeedsParen(node, parent, field):
            return cwast.ExprParen(node, x_srcloc=node.x_srcloc, x_type=node.x_type)

        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)

############################################################
# Token
############################################################


@enum.unique
class TK(enum.Enum):
    """TBD"""
    INVALID = 0

    ATTR = 1  # attribute
    ATTR_WITH_SPACE = 2  # attribute

    SEP = 3  # sequence seperator
    SEQ = 4  # sequence element
    BINOP = 5  # binary operator
    BINOP_NO_SPACE = 6  # binary operator

    UNOP = 7  # unary operator - not space afterwards
    END = 8
    BEG = 9
    ELSE = 10
    BEG_PAREN = 20
    BEG_COLON = 30
    BEG_ANON = 40
    BEG_EXPR_PAREN = 50

    ANNOTATION_SHORT = 11
    ANNOTATION_LONG = 12
    EOL_COMMENT = 13
    COMMENT = 14



BEG_TOKENS = set([
    "module", "global", "global!", "enum", "import", "defer", "block", "expr",
    "break", "continue", "fun", "cond", "type", "if", "type",
    "shed", "discard", "rec", "case", "let", "let!", "set", "for", "macro",
    "while", "try", "trylet", "trap", "return", "NONE", "static_assert",
    "$let", "$let!", "$for", "$for!", "swap",
])

INDENT = 1
MAX_LINE_LEN = 80


@dataclasses.dataclass()
class Token:
    """Node Field Descriptor"""
    kind: TK
    tag: str
    beg: Optional["Token"] = None
    start: int = 0
    length: int = 0
    long_array_val: bool = False

    def IsBeg(self) -> bool:
        return self.kind in (TK.BEG_COLON, TK.BEG, TK.BEG_PAREN, TK.BEG_ANON, TK.BEG_EXPR_PAREN)

    def IsTopLevelBeg(self):
        return self.kind is TK.BEG and self.tag in ("rec", "enum", "fun", "type", "import",
                                                    "global", "macro", "static_assert")


class TS:

    def __init__(self):
        self._tokens: List[Token] = []
        self._count = 0

    def Pos(self) -> int:
        return self._count

    def EmitToken(self, kind: TK, tag="", beg=None):
        if tag == "(" or tag == "[":
            assert kind in (TK.BEG_PAREN, TK.BEG_EXPR_PAREN)
        elif tag == ":":
            assert kind is TK.BEG_COLON
        tk = Token(kind, tag=tag, beg=beg, start=self._count)
        self._count += len(tag)
        self._tokens.append(tk)
        if beg is not None:
            beg.length = self._count - beg.start
        return tk

    def EmitUnOp(self, a: str):
        return self.EmitToken(TK.UNOP, a)

    def EmitBinOpNoSpace(self, a: str):
        return self.EmitToken(TK.BINOP_NO_SPACE, a)

    def EmitBinOp(self, a: str):
        return self.EmitToken(TK.BINOP, a)

    def EmitAttr(self, a: str):
        return self.EmitToken(TK.ATTR, a)

    def EmitElse(self):
        return self.EmitToken(TK.ELSE, "else")

    def EmitAnnotationShort(self, a: str):
        return self.EmitToken(TK.ANNOTATION_SHORT, a)

    def EmitAnnotationLong(self, a: str):
        return self.EmitToken(TK.ANNOTATION_LONG, a)

    def EmitEolComment(self, a: str):
        return self.EmitToken(TK.EOL_COMMENT, a)

    def EmitComment(self, a: str):
        return self.EmitToken(TK.COMMENT, a)

    def EmitSep(self, a: str):
        return self.EmitToken(TK.SEP, a)

    # no space before paren
    def EmitBegParen(self, a: str):
        return self.EmitToken(TK.BEG_PAREN, a)

    # space before paren
    def EmitBegExprParen(self, a: str):
        return self.EmitToken(TK.BEG_EXPR_PAREN, a)

    def EmitBeg(self, a: str):
        assert a in BEG_TOKENS or a.endswith(
            cwast.MACRO_SUFFIX), f"bad BEG token {a}"
        return self.EmitToken(TK.BEG, a)

    def EmitBegAnon(self):
        return self.EmitToken(TK.BEG_ANON)

    def EmitEnd(self, beg: Token):
        if beg.kind in (TK.BEG_PAREN, TK.BEG_EXPR_PAREN):
            return self.EmitToken(TK.END, tag=")" if beg.tag == "(" else "]", beg=beg)
        return self.EmitToken(TK.END, beg=beg)

    def EmitBegColon(self):
        return self.EmitToken(TK.BEG_COLON, ":")


def TokensParenList(ts: TS, lst, is_grouping: bool):
    sep = False
    beg = ts.EmitBegExprParen("(") if is_grouping else ts.EmitBegParen("(")
    for t in lst:
        if sep:
            ts.EmitSep(",")
        sep = True
        EmitTokens(ts, t)
    ts.EmitEnd(beg)


def TokensFunctional(ts: TS, name, nodes: List):
    if isinstance(name, str):
        ts.EmitUnOp(name)
    else:
        EmitTokens(ts, name)
    TokensParenList(ts, nodes, False)


def TokensBinaryInfix(ts: TS, name: str, node1, node2, node):
    EmitTokens(ts, node1)
    TokensAnnotations(ts, node)
    if name in (".", "->"):
        ts.EmitBinOpNoSpace(name)
    else:
        ts.EmitBinOp(name)
    if isinstance(node2, str):
        ts.EmitAttr(node2)
    else:
        EmitTokens(ts, node2)


def TokensUnaryPrefix(ts: TS, name: str, node):
    ts.EmitUnOp(name)
    EmitTokens(ts, node)


def EmitExpr3(ts: TS, node: cwast.Expr3):
    EmitTokens(ts, node.cond)
    ts.EmitAttr("??")
    EmitTokens(ts, node.expr_t)
    ts.EmitAttr("!!")
    EmitTokens(ts, node.expr_f)


def TokensAnnotations(ts: TS, node):
    # handle docs first
    for field, nfd in node.ATTRS:
        # these attributes will be rendered directly
        if field in ("triplequoted", "strkind") or nfd.kind is not cwast.NFK.ATTR_STR:
            continue
        val = getattr(node, field)
        if val:
            if field == "doc":
                if val.startswith('"""'):
                    val = val[3:-3]
                else:
                    val = val[1:-1]
                for line in val.split("\n"):
                    ts.EmitComment("-- " + line)

            else:
                ts.EmitAnnotationLong("@" + field + "=" + val)

    # next handle non-docs
    for field, nfd in node.ATTRS:
        # mut is handled directly
        if field in ("triplequoted", "strkind", "mut") or nfd.kind is not cwast.NFK.ATTR_BOOL:
            continue

        val = getattr(node, field)
        if val:
            ts.EmitAnnotationShort("@" + field)


def TokensMacroInvoke(ts: TS, node: cwast.MacroInvoke):
    if node.name == "->":
        assert len(node.args) == 2
        TokensBinaryInfix(ts, "->", node.args[0], node.args[1], node)
        return
    is_block_like = node.name in ["for", "while", "tryset", "trylet"]
    if is_block_like:
        beg_block = ts.EmitBeg(node.name)
    else:
        if node.x_role is cwast.MACRO_PARAM_KIND.STMT:
            beg_stmt = ts.EmitBegAnon()
        ts.EmitAttr(node.name)
        beg_paren = ts.EmitBegParen("(")
    sep = False
    for a in node.args:
        if sep:
            if not isinstance(a, cwast.EphemeralList) or not a.colon:
                ts.EmitSep(",")
        sep = True
        if isinstance(a, cwast.Id):
            ts.EmitAttr(a.name)
        elif isinstance(a, cwast.EphemeralList):
            if a.colon:
                beg = ts.EmitBegColon()
                for s in a.args:
                    EmitTokens(ts, s)
                ts.EmitEnd(beg)
            else:
                sep2 = False
                beg = ts.EmitBegParen("[")
                for e in a.args:
                    if sep2:
                        ts.EmitSep(",")
                    sep2 = True
                    EmitTokens(ts, e)
                ts.EmitEnd(beg)
        elif isinstance(a, (cwast.TypeBase, cwast.TypeAuto, cwast.TypeOf,
                            cwast.TypeArray, cwast.TypePtr, cwast.TypeSlice)):
            EmitTokens(ts, a)
        else:
            EmitTokens(ts, a)
    if is_block_like:
        ts.EmitEnd(beg_block)
    else:
        ts.EmitEnd(beg_paren)
        if node.x_role is cwast.MACRO_PARAM_KIND.STMT:
            ts.EmitEnd(beg_stmt)


def TokensSimpleStmt(ts: TS, kind: str, arg):
    beg = ts.EmitBeg(kind)    # return, continue, etc.
    if arg:
        if isinstance(arg, str):
            ts.EmitAttr(arg)
        elif not isinstance(arg, cwast.ValVoid):
            # for return
            EmitTokens(ts, arg)

    ts.EmitEnd(beg)


def TokensStmtBlock(ts: TS, kind, arg, stmts):
    beg_block = ts.EmitBeg(kind)
    if arg:
        if type(arg) == str:
            ts.EmitAttr(arg)
        else:
            EmitTokens(ts, arg)
    beg_colon = ts.EmitBegColon()
    for s in stmts:
        EmitTokens(ts, s)
    ts.EmitEnd(beg_colon)
    ts.EmitEnd(beg_block)


def TokensStmtSet(ts: TS, kind, lhs, rhs):
    beg = ts.EmitBeg("set")
    EmitTokens(ts, lhs)
    ts.EmitBinOp(kind)
    EmitTokens(ts, rhs)
    ts.EmitEnd(beg)


def TokensStmtLet(ts: TS, kind, name: str, type_or_auto, init_or_auto):
    beg = ts.EmitBeg(kind)
    ts.EmitAttr(name)
    EmitTokens(ts, type_or_auto)
    if not isinstance(init_or_auto, cwast.ValAuto):
        ts.EmitBinOp("=")
        EmitTokens(ts, init_or_auto)
    ts.EmitEnd(beg)


def TokensMacroFor(ts: TS, node: cwast.MacroFor):
    beg_for = ts.EmitBeg("$for")
    ts.EmitAttr(node.name)
    ts.EmitAttr(node.name_list)
    beg_colon = ts.EmitBegColon()
    for x in node.body_for:
        EmitTokens(ts, x)
    ts.EmitEnd(beg_colon)
    ts.EmitEnd(beg_for)


def ConcreteIf(ts: TS, node: cwast.StmtIf):
    beg_if = ts.EmitBeg("if")
    EmitTokens(ts, node.cond)
    beg_colon = ts.EmitBegColon()
    for c in node.body_t:
        EmitTokens(ts, c)
    ts.EmitEnd(beg_colon)
    if node.body_f:
        ts.EmitElse()
        beg_colon = ts.EmitBegColon()
        for c in node.body_f:
            EmitTokens(ts, c)
        ts.EmitEnd(beg_colon)
    ts.EmitEnd(beg_if)


def TokensValRec(ts: TS, node: cwast.ValRec):
    EmitTokens(ts, node.type)
    beg = ts.EmitBegParen("[")
    sep = False
    for e in node.inits_field:
        if sep:
            ts.EmitSep(",")
        sep = True
        EmitTokens(ts, e.value_or_undef)
        if e.init_field:
            ts.EmitAttr(e.init_field)
    ts.EmitEnd(beg)


def TokensValArray(ts: TS, node: cwast.ValArray):
    TokensFunctional(ts, "array", [node.expr_size, node.type])
    beg = ts.EmitBegParen("[")
    sizes = []
    sep = False
    for e in node.inits_array:
        assert isinstance(e, cwast.IndexVal)
        if sep:
            ts.EmitSep(",")
        sep = True
        start = ts.Pos()
        EmitTokens(ts, e.value_or_undef)
        if not isinstance(e.init_index, cwast.ValAuto):
            EmitTokens(ts, e.init_index)
        sizes.append(ts.Pos() - start)
    if len(sizes) > 5 and max(sizes) < MAX_LINE_LEN:
        beg.long_array_val = True
    ts.EmitEnd(beg)


def TokensDefMod(ts: TS, node: cwast.DefMod):
    beg = ts.EmitBeg("module")
    # we do not want the next item to be indented
    ts.EmitUnOp(node.name)
    beg_colon = ts.EmitBegColon()
    for child in node.body_mod:
        EmitTokens(ts, child)
    ts.EmitEnd(beg_colon)
    ts.EmitEnd(beg)


def TokensDefGlobal(ts: TS, node: cwast.DefGlobal):
    beg = ts.EmitBeg("global!" if node.mut else "global")
    ts.EmitAttr(node.name)
    EmitTokens(ts, node.type_or_auto)
    if not isinstance(node.initial_or_undef_or_auto, cwast.ValAuto):
        ts.EmitBinOp("=")
        EmitTokens(ts, node.initial_or_undef_or_auto)
    ts.EmitEnd(beg)


def TokensImport(ts: TS, node: cwast.Import):
    beg = ts.EmitBeg("import")
    ts.EmitAttr(node.name)
    if node.alias:
        ts.EmitBinOp("as")
        ts.EmitAttr(node.alias)
    ts.EmitEnd(beg)


def TokensDefType(ts: TS, node: cwast.DefType):
    beg = ts.EmitBeg("type")
    ts.EmitAttr(node.name)
    ts.EmitBinOp("=")
    EmitTokens(ts, node.type)
    ts.EmitEnd(beg)


def TokensTypeFun(ts: TS, node: cwast.TypeFun):
    ts.EmitUnOp("funtype")
    beg_paren = ts.EmitBegParen("(")
    sep = False
    for p in node.params:
        if sep:
            ts.EmitSep(",")
        sep = True
        ts.EmitAttr(p.name)
        EmitTokens(ts, p.type)
    ts.EmitEnd(beg_paren)
    EmitTokens(ts, node.result)


def TokensRecField(ts: TS, node: cwast.RecField):
    beg = ts.EmitBegAnon()
    ts.EmitAttr(node.name)
    EmitTokens(ts, node.type)
    ts.EmitEnd(beg)


def TokensDefRec(ts: TS, node: cwast.DefRec):
    beg_rec = ts.EmitBeg("rec")
    ts.EmitAttr(node.name)
    beg_colon = ts.EmitBegColon()
    for f in node.fields:
        EmitTokens(ts, f)
    ts.EmitEnd(beg_colon)
    ts.EmitEnd(beg_rec)


def TokensEnumVal(ts: TS, node: cwast.EnumVal):
    beg = ts.EmitBegAnon()
    ts.EmitAttr(node.name)
    EmitTokens(ts, node.value_or_auto)
    ts.EmitEnd(beg)


def TokensDefEnum(ts: TS, node: cwast.DefEnum):
    beg_enum = ts.EmitBeg("enum")
    ts.EmitAttr(node.name,)
    ts.EmitAttr(node.base_type_kind.name)
    beg_colon = ts.EmitBegColon()
    for f in node.items:
        EmitTokens(ts, f)
    ts.EmitEnd(beg_colon)
    ts.EmitEnd(beg_enum)


def TokensStaticAssert(ts: TS, node: cwast.StmtStaticAssert):
    beg = ts.EmitBeg("static_assert")
    EmitTokens(ts, node.cond)
    ts.EmitEnd(beg)


def TokensDefFun(ts: TS, node: cwast.DefFun):
    beg_fun = ts.EmitBeg("fun")
    ts.EmitAttr(node.name)

    beg_paren = ts.EmitBegParen("(")
    sep = False
    for p in node.params:
        if sep:
            ts.EmitSep(",")
        sep = True
        ts.EmitAttr(p.name)
        EmitTokens(ts, p.type)
    ts.EmitEnd(beg_paren)
    EmitTokens(ts, node.result)
    beg = ts.EmitBegColon()
    for child in node.body:
        EmitTokens(ts, child)
    ts.EmitEnd(beg)
    ts.EmitEnd(beg_fun)


def TokensDefMacro(ts: TS, node: cwast.DefMacro):
    beg_macro = ts.EmitBeg("macro")
    ts.EmitAttr(node.name)
    ts.EmitAttr(node.macro_result_kind.name)
    beg_paren = ts.EmitBegParen("(")
    sep = False
    for p in node.params_macro:
        if sep:
            ts.EmitSep(",")
        sep = True
        ts.EmitAttr(p.name)
        ts.EmitAttr(p.macro_param_kind.name)
    ts.EmitEnd(beg_paren)
    #
    beg_paren = ts.EmitBegParen("[")
    sep = False
    for gen_id in node.gen_ids:
        if sep:
            ts.EmitSep(",")
        sep = True
        ts.EmitAttr(gen_id)
    ts.EmitEnd(beg_paren)
    beg = ts.EmitBegColon()
    for x in node.body_macro:
        EmitTokens(ts, x)
    ts.EmitEnd(beg)
    ts.EmitEnd(beg_macro)


def TokensMacroId(ts: TS, node: cwast.MacroId):
    if node.x_role is cwast.MACRO_PARAM_KIND.STMT:
        beg = ts.EmitBegAnon()
        ts.EmitAttr(node.name)
        ts.EmitEnd(beg)
    else:
        ts.EmitAttr(node.name)


_INFIX_OPS = set([
    cwast.ExprIs,
    cwast.ExprIndex,
    cwast.ExprField,
    cwast.Expr2,
])


_CONCRETE_SYNTAX = {
    cwast.Id: lambda ts, n:  (ts.EmitAttr(n.name)),
    #
    cwast.MacroId: TokensMacroId,
    cwast.MacroInvoke: TokensMacroInvoke,
    cwast.MacroVar: lambda ts, n: TokensStmtLet(ts, "$let!" if n.mut else "$let", n.name, n.type_or_auto, n.initial_or_undef_or_auto),
    cwast.MacroFor: TokensMacroFor,
    #
    cwast.TypeAuto: lambda ts, n: ts.EmitAttr("auto"),
    cwast.TypeBase: lambda ts, n: ts.EmitAttr(n.base_type_kind.name.lower()),
    cwast.TypeSlice: lambda ts, n: TokensFunctional(ts, "slice!" if n.mut else "slice", [n.type]),
    cwast.TypeOf: lambda ts, n: TokensFunctional(ts, "typeof", [n.expr]),
    cwast.TypeUnion: lambda ts, n: TokensFunctional(ts, "union", n.types),
    cwast.TypePtr: lambda ts, n: TokensFunctional(ts, "ptr!" if n.mut else "ptr", [n.type]),
    cwast.TypeArray: lambda ts, n: TokensFunctional(ts, "array", [n.size, n.type]),
    cwast.TypeUnionDelta: lambda ts, n: TokensFunctional(ts, "uniondelta", [n.type, n.subtrahend]),
    cwast.TypeFun:  TokensTypeFun,
    #
    cwast.ValNum: lambda ts, n: ts.EmitAttr(n.number),
    cwast.ValTrue: lambda ts, n: ts.EmitAttr("true"),
    cwast.ValFalse: lambda ts, n: ts.EmitAttr("false"),
    cwast.ValUndef: lambda ts, n: ts.EmitAttr("undef"),
    cwast.ValVoid: lambda ts, n: ts.EmitAttr("void"),
    cwast.ValAuto: lambda ts, n: ts.EmitAttr("auto"),
    cwast.ValString: lambda ts, n: ts.EmitAttr(f'{n.strkind}"{n.string}"'),
    cwast.ValRec: TokensValRec,
    cwast.ValArray: TokensValArray,

    #
    cwast.ExprFront: lambda ts, n: TokensFunctional(ts, "front!" if n.mut else "front", [n.container]),
    cwast.ExprUnionTag: lambda ts, n: TokensFunctional(ts, "uniontag", [n.expr]),
    cwast.ExprAs: lambda ts, n: TokensFunctional(ts, "as", [n.expr, n.type]),
    cwast.ExprIs: lambda ts, n: TokensBinaryInfix(ts, "is", n.expr, n.type, n),
    cwast.ExprBitCast: lambda ts, n: TokensFunctional(ts, "asbits", [n.expr, n.type]),
    cwast.ExprOffsetof: lambda ts, n: TokensFunctional(ts, "offsetof", [n.type, n.field]),
    cwast.ExprLen: lambda ts, n: TokensFunctional(ts, "len", [n.container]),
    cwast.ExprSizeof: lambda ts, n: TokensFunctional(ts, "sizeof", [n.type]),
    cwast.ExprTypeId: lambda ts, n: TokensFunctional(ts, "sizeof", [n.type]),
    cwast.ExprNarrow: lambda ts, n: TokensFunctional(ts, "narrowto", [n.expr, n.type]),
    cwast.Expr1: lambda ts, n: TokensUnaryPrefix(ts, cwast.UNARY_EXPR_SHORTCUT_INV[n.unary_expr_kind], n.expr),
    cwast.ExprPointer: lambda ts, n: TokensFunctional(
        ts, cwast.POINTER_EXPR_SHORTCUT_INV[n.pointer_expr_kind],
        [n.expr1, n.expr2] if isinstance(n.expr_bound_or_undef, cwast.ValUndef) else
        [n.expr1, n.expr2, n.expr_bound_or_undef]),
    cwast.ExprIndex: lambda ts, n: TokensBinaryInfix(ts, "at", n.container, n.expr_index, n),
    cwast.ValSlice: lambda ts, n: TokensFunctional(ts, "slice", [n.pointer, n.expr_size]),
    cwast.ExprWrap: lambda ts, n: TokensFunctional(ts, "wrapas", [n.expr, n.type]),
    cwast.ExprUnwrap: lambda ts, n: TokensFunctional(ts, "unwrap", n.expr),
    cwast.ExprField: lambda ts, n: TokensBinaryInfix(ts, ".", n.container, n.field, n),
    cwast.ExprDeref: lambda ts, n: TokensUnaryPrefix(ts, "^", n.expr),
    cwast.ExprAddrOf: lambda ts, n: TokensUnaryPrefix(ts, "&!" if n.mut else "&", n.expr_lhs),
    cwast.Expr2: lambda ts, n: TokensBinaryInfix(ts, cwast.BINARY_EXPR_SHORTCUT_INV[n.binary_expr_kind],
                                                 n.expr1, n.expr2, n),
    cwast.Expr3: EmitExpr3,
    cwast.ExprStringify: lambda ts, n: TokensFunctional(ts, "stringify", [n.expr]),
    cwast.ExprCall: lambda ts, n: TokensFunctional(ts, n.callee, n.args),
    cwast.ExprStmt: lambda ts, n: TokensStmtBlock(ts, "expr", "", n.body),
    cwast.ExprParen: lambda ts, n: TokensParenList(ts, [n.expr], True),

    #
    cwast.StmtContinue: lambda ts, n: TokensSimpleStmt(ts, "continue", n.target),
    cwast.StmtBreak: lambda ts, n: TokensSimpleStmt(ts, "break", n.target),
    cwast.StmtTrap: lambda ts, n: TokensSimpleStmt(ts, "trap", ""),
    cwast.StmtReturn: lambda ts, n: TokensSimpleStmt(ts, "return", n.expr_ret),
    cwast.StmtExpr: lambda ts, n: TokensSimpleStmt(ts, "shed", n.expr),
    cwast.StmtDefer: lambda ts, n: TokensStmtBlock(ts, "defer", "", n.body),
    cwast.StmtBlock: lambda ts, n: TokensStmtBlock(ts, "block", n.label, n.body),
    cwast.Case: lambda ts, n: TokensStmtBlock(ts, "case", n.cond, n.body),

    cwast.StmtCond: lambda ts, n: TokensStmtBlock(ts, "cond", "", n.cases),
    cwast.StmtCompoundAssignment: lambda ts, n: TokensStmtSet(ts, cwast.ASSIGNMENT_SHORTCUT_INV[n.assignment_kind],
                                                              n.lhs, n.expr_rhs),
    cwast.StmtAssignment: lambda ts, n: TokensStmtSet(ts, "=", n.lhs, n.expr_rhs),
    cwast.DefVar: lambda ts, n: TokensStmtLet(ts, "let!" if n.mut else "let", n.name, n.type_or_auto, n.initial_or_undef_or_auto),
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
    cwast.EnumVal:  TokensEnumVal,
    cwast.RecField:  TokensRecField,
}


def EmitTokens(ts: TS, node):
    if node.__class__ not in _INFIX_OPS:
        TokensAnnotations(ts, node)

    gen = _CONCRETE_SYNTAX.get(node.__class__)
    assert gen, f"unknown node {node.__class__}"
    gen(ts, node)


class Stack:
    """TBD"""

    def __init__(self):
        self._stack = []

    def depth(self):
        return len(self._stack)

    def empty(self):
        return 0 == len(self._stack)

    def push(self, tk: Token, indent_delta: int, break_after_sep=False) -> int:
        assert tk.IsBeg(), f"{tk}"
        new_indent = self.CurrentIndent() + indent_delta
        self._stack.append((tk, new_indent, break_after_sep))
        return new_indent

    def pop(self):
        return self._stack.pop(-1)

    def CurrentIndent(self) -> int:
        if self._stack:
            return self._stack[-1][1]
        return 0

    def BreakAfterSep(self) -> bool:
        if self._stack:
            return self._stack[-1][2]
        assert False


class Sink:
    """TBD"""

    def __init__(self):
        self._indent = 0
        self._col = 0

    def CurrenColumn(self):
        return self._col

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


def FormatTokenStream(tokens, stack: Stack, sink: Sink):
    """
    TK.BEG may force a new indentation level

    """
    want_space = False

    while True:
        tk: Token = tokens.pop(-1)
        kind = tk.kind
        tag = tk.tag
        if want_space:
            if kind in (TK.BEG, TK.BEG_ANON, TK.UNOP, TK.ANNOTATION_SHORT, TK.BINOP, TK.ATTR, TK.BEG_EXPR_PAREN):
                # assert False, f"{tk}"
                sink.emit_space()
        want_space = False
        if kind is TK.BEG:
            sink.emit_token(tag)
            stack.push(tk, 0)
            if tag == "module":
                # there maybe parameters
                want_space = True
            elif not tag.endswith(cwast.MACRO_SUFFIX):
                want_space = True
        elif kind is TK.BEG_ANON:
            stack.push(tk, 0)
        elif kind is TK.COMMENT:
            sink.emit_token(tag)
            sink.newline()
        elif kind is TK.BEG_COLON:
            sink.emit_token(tag)
            sink.newline()
            if stack.depth() <= 1:
                sink.newline()
            indent = stack.push(tk, INDENT if stack.depth() > 1 else 0)
            sink.set_indent(indent)
        elif kind in (TK.BEG_PAREN, TK.BEG_EXPR_PAREN):
            sink.emit_token(tag)
            if sink.CurrenColumn() + tk.length > MAX_LINE_LEN:
                break_after_sep = (not tk.long_array_val) and stack.CurrentIndent(
                ) + tk.length > MAX_LINE_LEN
                indent = stack.push(
                    tk, INDENT, break_after_sep=break_after_sep)
                sink.set_indent(indent)
                sink.newline()
            else:
                stack.push(tk, 0)
        elif kind is TK.ELSE:
            # ci = stack.CurrentIndent()
            # sink.indent(ci)
            sink.emit_token(tag)
        elif kind is TK.ATTR:
            if sink.CurrenColumn() + tk.length > MAX_LINE_LEN:
                sink.newline()
            sink.emit_token(tag)
            want_space = True
        elif kind is TK.ATTR_WITH_SPACE:
            sink.emit_token(tag)
            sink.emit_space()
        elif kind is TK.SEP:
            sink.emit_token(tag)
            if stack.BreakAfterSep():
                sink.newline()
            else:
                want_space = True
        elif kind is TK.END:
            beg, _, _ = stack.pop()
            sink.set_indent(stack.CurrentIndent())
            if beg.kind is TK.BEG:
                if beg.tag == "module":
                    assert not tokens
                    assert stack.empty()
                    return
                sink.maybe_newline()
            elif beg.kind is TK.BEG_ANON:
                sink.maybe_newline()
            elif beg.kind is TK.BEG_COLON:
                sink.maybe_newline()
            elif beg.kind is TK.BEG_EXPR_PAREN:
                sink.emit_token(tk.tag)
                want_space = True
            elif beg.kind is TK.BEG_PAREN:
                # TODO
                sink.emit_token(tk.tag)
                want_space = True
            else:
                assert False
            if beg.IsTopLevelBeg():
                sink.newline()
        elif kind is TK.BINOP_NO_SPACE:
            sink.emit_token(tag)
        elif kind is TK.BINOP:
            sink.emit_token(tag)
            want_space = True
        elif kind is TK.UNOP:
            sink.emit_token(tag)
        elif kind is TK.ANNOTATION_LONG:
            sink.maybe_newline()
            sink.emit_token(tag)
            sink.newline()
        elif kind is TK.ANNOTATION_SHORT:
            sink.emit_token(tag)
            want_space = True
        else:
            assert False, f"{kind}"
        assert tokens, f"{tag} {kind}"
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
            ts = TS()
            tokens = EmitTokens(ts, mods[0])
            tokens = list(ts._tokens)
            # print(tokens)
            # reverse once because popping of the end of a list is more efficient
            tokens.reverse()
            # and now format the stream
            FormatTokenStream(tokens, Stack(), Sink())
    else:
        assert False, f"unknown mode {args.mode}"


if __name__ == "__main__":
    main()
