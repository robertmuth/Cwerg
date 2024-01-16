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


@enum.unique
class TK(enum.Enum):
    """TBD"""
    INVALID = 0

    ATTR = 1  # attribute
    SEP = 2  # sequence seperator
    SEQ = 3  # sequence element
    COM = 4  # comment
    MCOM = 5  # multi line comment
    BINOP = 6  # binary operator
    UNOP = 7  # unary operator
    BEG = 8
    END = 10
    ANNOTATION = 11
    NEWLINE = 12


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

_ASSIGNMENT_KIND_TO_STR = {
    cwast.ASSIGNMENT_KIND.ADD: "+=",
    cwast.ASSIGNMENT_KIND.SUB: "-=",
    cwast.ASSIGNMENT_KIND.MUL: "*=",
    cwast.ASSIGNMENT_KIND.REM: "%=",
    cwast.ASSIGNMENT_KIND.OR: "or=",
    cwast.ASSIGNMENT_KIND.AND: "and=",
    cwast.ASSIGNMENT_KIND.XOR: "xor=",

    cwast.ASSIGNMENT_KIND.SHL: "<<=",
    cwast.ASSIGNMENT_KIND.SHR: ">>=",
}


def Token(a, k):
    return (a, k)


def UnaryFunction(name, node):
    yield Token(name, TK.ATTR)
    yield Token("(", TK.BEG)
    yield from ConcreteSyntaxMisc(node)
    yield Token(")", TK.END)


def UnaryFunctionType(name, node):
    yield Token(name, TK.ATTR)
    yield Token("(", TK.BEG)
    yield from ConcreteSyntaxMisc(node)
    yield Token(")", TK.END)


def UnaryFunctionType(name, node):
    yield Token(name, TK.ATTR)
    yield Token("(", TK.BEG)
    yield from ConcreteSyntaxMisc(node)
    yield Token(")", TK.END)


def BinaryFunction(name, node1, node2):
    yield Token(name, TK.ATTR)
    yield Token("(", TK.BEG)
    yield from ConcreteSyntaxMisc(node1)
    yield Token(",", TK.SEP)
    yield from ConcreteSyntaxMisc(node2)
    yield Token(")", TK.END)


def BinaryFunctionType(name, node1, node2):
    yield Token(name, TK.ATTR)
    yield Token("(", TK.BEG)
    yield from ConcreteSyntaxMisc(node1)
    yield Token(",", TK.SEP)
    yield from ConcreteSyntaxMisc(node2)
    yield Token(")", TK.END)


def BinaryFunctionTypeString(name, node1, field):
    yield Token(name, TK.ATTR)
    yield Token("(", TK.BEG)
    yield from ConcreteSyntaxMisc(node1)
    yield Token(",", TK.SEP)
    yield (field, TK.ATTR)
    yield Token(")", TK.END)


def BinaryInfix(name: str, node1, node2):
    yield from ConcreteSyntaxMisc(node1)
    yield Token(name, TK.BINOP)
    yield from ConcreteSyntaxMisc(node2)


def BinaryInfixType(name: str, node1, node2):
    yield from ConcreteSyntaxMisc(node1)
    yield Token(name, TK.BINOP)
    yield from ConcreteSyntaxMisc(node2)


def BinaryInfixString(name: str, node1, field):
    yield from ConcreteSyntaxMisc(node1)
    yield Token(name, TK.BINOP)
    yield Token(field, TK.ATTR)


def UnaryPrefix(name: str, node):
    yield Token(name, TK.BINOP)
    yield from ConcreteSyntaxMisc(node)


def ParenListType(lst):
    sep = False
    yield Token("(", TK.BEG)
    for t in lst:
        if sep:
            yield Token(",", TK.SEP)
            sep = True
        yield from ConcreteSyntaxMisc(t)
    yield Token(")", TK.END)


def ParenListExpr(lst):
    sep = False
    yield Token("(", TK.BEG)
    for t in lst:
        if sep:
            yield Token(",", TK.SEP)
            sep = True
        yield from ConcreteSyntaxMisc(t)
    yield Token(")", TK.END)


def NameWithParenListExpr(name, lst):
    yield Token(name, TK.UNOP)
    yield from ParenListExpr(lst)


def ConcreteSyntaxMacroInvoke(node: cwast.MacroInvoke):
    yield Token(f"{node.name}", TK.BEG)
    is_block_like = node.name in ["for", "while", "tryset", "trylet"]
    if not is_block_like:
        yield Token("(", TK.BEG)
    sep = False
    for a in node.args:

        if isinstance(a, cwast.Id):
            if sep:
                yield Token(",", TK.SEP)
            yield a.name, TK.ATTR
        elif isinstance(a, (cwast.EphemeralList)):
            if a.colon:
                yield Token(":", TK.BEG)
                for s in a.args:
                    yield from ConcreteSyntaxStmt(s)
                yield Token("@:", TK.END)
            else:
                if sep:
                    yield Token(",", TK.SEP)
                sep2 = False
                yield Token("[", TK.BEG)
                for e in a.args:
                    if sep2:
                        yield Token(",", TK.SEP)
                    sep2 = True
                    yield from ConcreteSyntaxMisc(e)
                yield "]", TK.END
        elif isinstance(a, (cwast.TypeBase, cwast.TypeAuto, cwast.TypeOf,
                            cwast.TypeArray, cwast.TypePtr, cwast.TypeSlice)):
            if sep:
                yield Token(",", TK.SEP)
            yield from ConcreteSyntaxMisc(a)
        else:
            if sep:
                yield Token(",", TK.SEP)
            yield from ConcreteSyntaxMisc(a)
        sep = True
    if not is_block_like:
        yield Token(")", TK.END)

    yield Token(f"@{node.name}", TK.END)


CONCRETE_SYNTAX = {
    cwast.Id: lambda n:  (yield Token(n.name, TK.ATTR)),
    #
    cwast.MacroId: lambda n:  (yield Token(n.name, TK.ATTR)),
    cwast.MacroInvoke: ConcreteSyntaxMacroInvoke,
    #
    cwast.TypeAuto: lambda n: (yield Token("auto", TK.ATTR)),
    cwast.TypeBase: lambda n: (yield Token(n.base_type_kind.name.lower(), TK.ATTR)),
    cwast.TypeSlice: lambda n: UnaryFunctionType("slice", n.type),
    cwast.TypeOf: lambda n: UnaryFunction("typeof", n.expr),
    cwast.TypeUnion: lambda n: NameWithParenListExpr("union", n.types),
    cwast.TypePtr: lambda n: UnaryFunctionType("ptr", n.type),
    cwast.TypeArray: lambda n: BinaryFunctionType("array", n.size, n.type),
    #
    cwast.ValNum: lambda n: (yield Token(n.number, TK.ATTR)),
    cwast.ValTrue: lambda n: (yield Token("true", TK.ATTR)),
    cwast.ValFalse: lambda n: (yield Token("false", TK.ATTR)),
    cwast.ValUndef: lambda n: (yield Token("undef", TK.ATTR)),
    cwast.ValVoid: lambda n: (yield Token("void", TK.ATTR)),
    cwast.ValAuto: lambda n: (yield Token("auto", TK.ATTR)),
    cwast.ValString: lambda n: (yield Token(f'{n.strkind}"{n.string}"', TK.ATTR)),
    #
    cwast.ExprFront: lambda n: UnaryFunction("front", n.container),
    cwast.ExprUnionTag: lambda n: UnaryFunction("uniontag", n.expr),
    cwast.ExprAs: lambda n: BinaryFunctionType("as", n.expr, n.type),
    cwast.ExprIs: lambda n: BinaryInfixType("is", n.expr, n.type),
    cwast.ExprBitCast: lambda n: BinaryInfixType("asbits", n.expr, n.type),
    cwast.ExprOffsetof: lambda n: BinaryFunctionTypeString("offsetof", n.type, n.field),
    cwast.ExprLen: lambda n: UnaryFunction("len", n.container),
    cwast.ExprSizeof: lambda n: UnaryFunctionType("sizeof", n.type),
    cwast.ExprTypeId: lambda n: UnaryFunctionType("sizeof", n.type),
    cwast.ExprNarrow: lambda n: BinaryInfixType("narrowto", n.expr, n.type),
    cwast.Expr1: lambda n: UnaryFunction(f"{n.unary_expr_kind.name}", n.expr),
    cwast.ExprPointer: lambda n: BinaryInfix(f"{n.pointer_expr_kind.name}", n.expr1, n.expr2),
    cwast.ExprIndex: lambda n: BinaryInfix("at", n.container, n.expr_index),
    cwast.ValSlice: lambda n: BinaryFunction("slice", n.pointer, n.expr_size),
    cwast.ExprWrap: lambda n: BinaryInfixType("wrap", n.expr, n.type),
    cwast.ExprUnwrap: lambda n: UnaryFunction("unwrap", n.expr),
    cwast.ExprField: lambda n: BinaryInfixString(".", n.container, n.field),
    cwast.ExprDeref: lambda n: UnaryPrefix("^", n.expr),
    cwast.ExprAddrOf: lambda n: UnaryPrefix("&", n.expr_lhs),
    cwast.Expr2: lambda n: BinaryInfix(_BINARY_EXPR_KIND_TO_STR[n.binary_expr_kind],
                                       n.expr1, n.expr2),
    cwast.ExprStringify: lambda n: UnaryFunction("stringify", n.expr),

}


def ConcreteSyntaxMisc(node):
    gen = CONCRETE_SYNTAX.get(node.__class__)
    if gen:
        yield from gen(node)
        return

    if isinstance(node, cwast.ValRec):
        yield from ConcreteSyntaxMisc(node.type)
        yield Token("[", TK.BEG)
        sep = False
        for e in node.inits_field:
            if sep:
                yield Token(",", TK.SEP)
            sep = True
            yield from ConcreteSyntaxMisc(e.value_or_undef)
            if e.init_field:
                yield Token(e.init_field, TK.ATTR)
        yield Token("]", TK.END)

    elif isinstance(node, cwast.MacroInvoke):
        if node.name == "->":
            assert len(node.args) == 2
            yield from ConcreteSyntaxMisc(node.args[0])
            yield Token("->", TK.ATTR)
            yield from ConcreteSyntaxMisc(node.args[1])
        else:
            yield from ConcreteSyntaxMacroInvoke(node)
    elif isinstance(node, cwast.Expr3):
        yield from ConcreteSyntaxMisc(node.cond)
        yield Token("??", TK.ATTR)
        yield from ConcreteSyntaxMisc(node.expr_t)
        yield Token("!!", TK.ATTR)
        yield from ConcreteSyntaxMisc(node.expr_f)
    elif isinstance(node, cwast.ValArray):
        yield Token("[", TK.BEG)
        yield from ConcreteSyntaxMisc(node.expr_size)
        yield Token("]", TK.END)
        yield from ConcreteSyntaxMisc(node.type)
        yield Token("[", TK.BEG)
        sep = False
        for e in node.inits_array:
            assert isinstance(e, cwast.IndexVal)
            if sep:
                yield Token(",", TK.SEP)
            sep = True
            yield from ConcreteSyntaxMisc(e.value_or_undef)
            if not isinstance(e.init_index, cwast.ValAuto):
                yield from ConcreteSyntaxMisc(e.init_index)
        yield Token("]", TK.END)

    elif isinstance(node, cwast.ExprCall):
        yield from ConcreteSyntaxMisc(node.callee)
        yield from ParenListExpr(node.args)


    elif isinstance(node, cwast.TypePtr):
        if node.mut:
            yield Token("@mut", TK.ATTR)
        yield "*", TK.UNOP
        yield from ConcreteSyntaxMisc(node.type)


    elif isinstance(node, cwast.TypeFun):
        yield Token("funtype", TK.UNOP)
        yield Token("(", TK.BEG)
        for p in node.params:
            yield Token(p.name, TK.ATTR)
            yield from ConcreteSyntaxMisc(p.type)
        yield Token(")", TK.END)
        yield from ConcreteSyntaxMisc(node.result)
    elif isinstance(node, cwast.TypeUnionDelta):
        yield from ConcreteSyntaxMisc(node.type)
        yield Token("uniondelta", TK.ATTR)
        yield from ConcreteSyntaxMisc(node.subtrahend)


    elif isinstance(node, cwast.MacroVar):
        yield ("$let", TK.BEG)
        if node.mut:
            yield "@mut", TK.ATTR
        yield (node.name, TK.ATTR)
        yield from ConcreteSyntaxMisc(node.type_or_auto)
        if not isinstance(node.initial_or_undef_or_auto, cwast.ValAuto):
            yield ("=", TK.BINOP)
            yield from ConcreteSyntaxMisc(node.initial_or_undef_or_auto)
        yield ("@$let", TK.END)
    elif isinstance(node, cwast.MacroFor):
        yield ("$for", TK.BEG)
        yield (node.name, TK.ATTR)
        yield (node.name_list, TK.ATTR)
        yield ":", TK.BEG

        yield "@:", TK.END
        yield ("@$for", TK.END)
    else:
        assert False, f"{node.__class__} {node}"



def ConcreteSyntaxStmt(node):
    if node.GROUP is cwast.GROUP.Macro:
        yield from ConcreteSyntaxMisc(node)
        return
    if node.doc:
        yield "@doc=" + node.doc, TK.ANNOTATION
    if isinstance(node, cwast.Id):
        yield Token(node.name, TK.ATTR)
    elif isinstance(node, cwast.Case):
        yield ("case", TK.BEG)
        yield from ConcreteSyntaxMisc(node.cond)
        yield (":", TK.BEG)
        for c in node.body:
            yield from ConcreteSyntaxStmt(c)
        yield ("@:", TK.END)
        yield ("@case", TK.END)

    elif isinstance(node, cwast.StmtCond):
        yield ("cond", TK.BEG)
        yield (":", TK.BEG)
        for c in node.cases:
            yield from ConcreteSyntaxStmt(c)
        yield ("@:", TK.END)
        yield ("@cond", TK.END)
    elif isinstance(node, cwast.DefVar):
        yield ("let", TK.BEG)
        if node.mut:
            yield "@mut", TK.ATTR
        yield (node.name, TK.ATTR)
        yield from ConcreteSyntaxMisc(node.type_or_auto)
        if not isinstance(node.initial_or_undef_or_auto, cwast.ValAuto):
            yield ("=", TK.BINOP)
            yield from ConcreteSyntaxMisc(node.initial_or_undef_or_auto)
        yield ("@let", TK.END)
    elif isinstance(node, cwast.StmtCompoundAssignment):
        yield ("set", TK.BEG)
        yield from ConcreteSyntaxMisc(node.lhs)
        yield _ASSIGNMENT_KIND_TO_STR[node.assignment_kind], TK.BINOP
        yield from ConcreteSyntaxMisc(node.expr_rhs)
        yield ("@set", TK.END)
    elif isinstance(node, cwast.StmtAssignment):
        yield ("set", TK.BEG)
        yield from ConcreteSyntaxMisc(node.lhs)
        yield "=", TK.BINOP
        yield from ConcreteSyntaxMisc(node.expr_rhs)
        yield ("@set", TK.END)
    elif isinstance(node, cwast.StmtIf):
        yield ("if", TK.BEG)
        yield from ConcreteSyntaxMisc(node.cond)
        yield (":", TK.BEG)
        for c in node.body_t:
            yield from ConcreteSyntaxStmt(c)
        yield ("@:", TK.END)
        if node.body_f:
            yield ("else", TK.ATTR)
            yield (":", TK.BEG)
            for c in node.body_f:
                yield from ConcreteSyntaxStmt(c)
            yield ("@:", TK.END)
        yield ("@if", TK.END)
    elif isinstance(node, cwast.MacroInvoke):
        yield from ConcreteSyntaxMacroInvoke(node)
    elif isinstance(node, cwast.StmtDefer):
        yield ("defer", TK.BEG)
        yield ":", TK.BEG
        for s in node.body:
            yield from ConcreteSyntaxStmt(s)
        yield "@:", TK.END
        yield ("@defer", TK.END)
    elif isinstance(node, cwast.StmtExpr):
        yield ("shed", TK.BEG)
        yield from ConcreteSyntaxMisc(node.expr)
        yield ("@shed", TK.END)
    elif isinstance(node, cwast.StmtBlock):
        yield ("block", TK.BEG)
        if node.label:
            yield (node.label, TK.ATTR)
        yield ":", TK.BEG
        for s in node.body:
            yield from ConcreteSyntaxStmt(s)
        yield "@:", TK.END
        yield ("@block", TK.END)
    elif isinstance(node, cwast.StmtReturn):
        yield "return", TK.BEG
        yield from ConcreteSyntaxMisc(node.expr_ret)
        yield ("@return", TK.END)
    elif isinstance(node, cwast.StmtBreak):
        yield "break", TK.BEG
        if node.target:
            yield node.target, TK.ATTR
        yield ("@break", TK.END)
    elif isinstance(node, cwast.StmtContinue):
        yield "continue", TK.BEG
        if node.target:
            yield node.target, TK.ATTR
        yield ("@continue", TK.END)
    elif isinstance(node, cwast.StmtTrap):
        yield "trap", TK.BEG
        yield "@trap", TK.END
    else:
        assert False, f"unknown stmt node: {type(node)}"





def ConcreteSyntaxMacroBody(node):
    if node.GROUP is cwast.GROUP.Type:
        yield from ConcreteSyntaxMisc(node)
    elif node.GROUP is cwast.GROUP.Statement:
        yield from ConcreteSyntaxStmt(node)
    elif node.GROUP is cwast.GROUP.Value:
        yield from ConcreteSyntaxMisc(node)
    elif node.GROUP is cwast.GROUP.Expression:
        yield from ConcreteSyntaxMisc(node)
    elif node.GROUP is cwast.GROUP.Macro:
        yield from ConcreteSyntaxMisc(node)
    else:
        assert False, f"unsupported top level {node.__class__}"


def ConcreteSyntaxTop(node):
    if not isinstance(node, cwast.DefMod):
        yield ("", TK.NEWLINE)
    if "doc" in node.__class__.ATTRS_MAP:
        if node.doc:
            yield Token("@doc=" + node.doc, TK.ANNOTATION)
    if "pub" in node.__class__.ATTRS_MAP:
        if node.pub:
            yield Token("@pub", TK.ANNOTATION)
    if isinstance(node, cwast.DefMod):
        yield Token("module", TK.BEG)
        yield (node.name, TK.ATTR)
        for child in node.body_mod:
            yield from ConcreteSyntaxTop(child)
        yield ("@module", TK.END)

    elif isinstance(node, cwast.DefGlobal):
        yield Token("global", TK.BEG)
        yield Token(node.name, TK.ATTR)
        yield from ConcreteSyntaxMisc(node.type_or_auto)
        if not isinstance(node.initial_or_undef_or_auto, cwast.ValAuto):
            yield Token("=", TK.BINOP)
            yield from ConcreteSyntaxMisc(node.initial_or_undef_or_auto)
        yield ("@global", TK.END)
    elif isinstance(node, cwast.DefFun):
        yield Token("fun", TK.BEG)
        yield Token(node.name, TK.ATTR)

        yield ("(", TK.BEG)
        sep = False
        for p in node.params:
            if sep:
                yield ",", TK.SEP
            sep = True
            yield (p.name, TK.ATTR)
            yield from ConcreteSyntaxMisc(p.type)
        yield Token(")", TK.END)
        yield from ConcreteSyntaxMisc(node.result)
        yield Token(":", TK.BEG)

        for child in node.body:
            yield from ConcreteSyntaxStmt(child)
        yield Token("@:", TK.END)
        yield Token("@fun", TK.END)

    elif isinstance(node, cwast.Import):
        yield ("import", TK.BEG)
        yield (node.name, TK.ATTR)
        if node.alias:
            yield ("as", TK.BINOP)
            yield (node.alias, TK.ATTR)
        yield ("@import", TK.END)
    elif isinstance(node, cwast.DefType):
        yield "type", TK.BEG
        if node.wrapped:
            yield "wrapped", TK.ATTR
        yield node.name, TK.ATTR
        yield from ConcreteSyntaxMisc(node.type)
        yield "@type", TK.END
    elif isinstance(node, cwast.DefRec):
        yield "rec", TK.BEG
        yield node.name, TK.ATTR
        yield ":", TK.BEG
        for f in node.fields:
            yield "NONE", TK.BEG
            yield f.name, TK.ATTR
            yield from ConcreteSyntaxMisc(f.type)
            yield "@NONE", TK.END
        yield "@:", TK.END
        yield "@rec", TK.END
    elif isinstance(node, cwast.DefEnum):
        yield "enum", TK.BEG
        yield node.name, TK.ATTR
        yield node.base_type_kind.name, TK.ATTR
        yield ":", TK.BEG
        for f in node.items:
            yield "NONE", TK.BEG
            yield f.name, TK.ATTR
            yield from ConcreteSyntaxMisc(f.value_or_auto)
            yield "@NONE", TK.END
        yield "@:", TK.END
        yield "@enum", TK.END
    elif isinstance(node, cwast.StmtStaticAssert):
        yield "static_assert", TK.BEG
        yield from ConcreteSyntaxMisc(node.cond)
        yield "@static_assert", TK.END
    elif isinstance(node, cwast.DefMacro):
        yield "macro", TK.BEG
        yield node.name, TK.ATTR
        yield node.macro_result_kind.name, TK.ATTR
        yield ("[", TK.BEG)
        sep = False
        for p in node.params_macro:
            if sep:
                yield ",", TK.SEP
            sep = True
            yield p.name, TK.ATTR
            yield p.macro_param_kind.name, TK.ATTR
        yield ("]", TK.END)
        #
        yield ("[", TK.BEG)
        sep = False
        for gen_id in node.gen_ids:
            if sep:
                yield ",", TK.SEP
            sep = True
            yield gen_id, TK.ATTR
        yield ("]", TK.END)
        yield ":", TK.BEG
        for x in node.body_macro:
            yield from ConcreteSyntaxMacroBody(x)
        yield "@:", TK.END

        yield "@macro", TK.END

    else:
        assert False, f"unknown node: {type(node)}"


BEG_TOKENS = set([
    "module", "global", "enum", "import", "defer", "block",
    "break", "continue", "fun", "cond", "type", "if", "type",
    "shed", "discard", "rec", "case", "let", "set", "for", "macro",
    "while", "try", "trylet", "trap", "return", "NONE", "static_assert",
    "$let", "$for",
    ":", "(", "["
])
BEG_WITH_SEP_TOKENS = set(["(", "["])
END_TOKENS = set(["", ")", "]"])


def GetCurrentIndent(stack) -> int:
    for _, kind, i in reversed(stack):
        if kind is TK.BEG:
            return i * 4
    assert False


class Stack:
    """TBD"""

    def __init__(self):
        self._stack = []

    def empty(self):
        return 0 == len(self._stack)

    def push(self, t, kind, indent):
        self._stack.append((t, kind, indent))

    def pop(self):
        return self._stack.pop(-1)

    def CurrentIndent(self) -> int:
        for _, kind, i in reversed(self._stack):
            if kind is TK.BEG:
                return i
        return 0
        assert False


class Sink:
    """TBD"""

    def __init__(self):
        self._col = 0

    def maybe_newline(self):
        if self._col != 0:
            print()
            self._col = 0

    def newline(self):
        print()
        self._col = 0

    def emit_token(self, token):
        print(token, end="")
        self._col += len(token)

    def indent(self, ci):
        print(" " * (4 * ci), end="")


def FormatTokenStream(tokens, stack: Stack, sink: Sink):
    """
    TK.BEG may force a new indentation level

    """
    while True:
        t, kind = tokens.pop(-1)
        if kind is TK.BEG:
            assert t in BEG_TOKENS or t.endswith("!"), f"bad BEG token {t}"
            if t == "module":
                assert stack.empty()
                sink.emit_token(t)
                stack.push(t, kind, 0)
            elif t == ":":
                ci = stack.CurrentIndent()
                sink.emit_token(t)
                sink.newline()
                stack.push(t, kind, ci + 1)
            elif t.endswith("!"):
                ci = stack.CurrentIndent()
                sink.indent(ci)
                sink.emit_token(t)
                stack.push(t, kind, ci)
            elif t in BEG_WITH_SEP_TOKENS:
                ci = stack.CurrentIndent()
                sink.emit_token(" " + t)
                stack.push(t, kind, ci)
            else:
                ci = stack.CurrentIndent()
                sink.indent(ci)
                if t != "NONE":
                    sink.emit_token(t)
                stack.push(t, kind, ci)
        elif kind is TK.ATTR:
            assert type(t) is str, repr(t)
            if t == "else":
                ci = stack.CurrentIndent()
                sink.indent(ci)
                sink.emit_token(t)
            else:
                sink.emit_token(" "+t)
        elif kind is TK.SEP:
            sink.emit_token(t)
        elif kind is TK.END:
            t_beg, kind_beg, _ = stack.pop()
            assert kind_beg is TK.BEG
            if t.startswith("@"):
                assert t[1:] == t_beg, f"{t_beg} vs {t}"
            elif t == ")":
                assert t_beg == "(", f"{t_beg} vs {t}"
            else:
                assert t_beg == "[" and t == "]", f"{t_beg} vs {t}"
            if t_beg == "module":
                sink.newline()
                assert not tokens
                assert stack.empty()
                return
            if not t.startswith("@"):
                sink.emit_token(t)
            if t.startswith("@"):
                sink.maybe_newline()

        elif kind is TK.BINOP:
            sink.emit_token(" " + t)
        elif kind is TK.UNOP:
            sink.emit_token(" " + t)
        elif kind is TK.COM:
            ci = stack.CurrentIndent()
            sink.maybe_newline()
            sink.indent(ci)
            sink.emit_token("# ")
            sink.emit_token(t)
            sink.newline()
        elif kind is TK.NEWLINE:
            sink.newline()
        elif kind is TK.ANNOTATION:
            ci = stack.CurrentIndent()
            sink.indent(ci)
            sink.emit_token(t)
            sink.newline()
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
                cwast.CheckAST(m, set(), pre_symbolize=True)
            # we first produce an output token stream from the AST
            tokens = ConcreteSyntaxTop(mods[0])
            tokens = list(tokens)
            # print(tokens)
            tokens.reverse()
            # and now format the stream
            FormatTokenStream(tokens, Stack(), Sink())
    else:
        assert False, f"unknown mode {args.mode}"


if __name__ == "__main__":
    main()
