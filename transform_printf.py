#!/usr/bin/python3

import re
from typing import Optional, List

from pycparser import c_ast

import common
import meta

__all__ = ["TokenizeFormatString", "FormatOptions", "PrintfSplitterTransform"]

PRINTF_OPTION = re.compile(r"%([-+ 0]*)([0-9]*)([.][0-9]+)?([lqh]+)?([cduoxefgsp])")

LENGTH_TRANSLATION = {
    None: "",
    "l": "l",
    "ll": "q",
    "q": "q",
    "h": "h",
}


def MakeSimpleTypeDecl(name, type_names):
    return c_ast.TypeDecl(name, [], common.GetCanonicalIdentifierType(type_names))


def MakePrintfStyleDecl(name: str, type_names: List[str], is_pointer=False):
    parameter_format = c_ast.Decl("format", [], [], [],
                                  c_ast.PtrDecl([], MakeSimpleTypeDecl("format", ["char"])), None, None)

    parameter_value = c_ast.Decl("value", [], [], [], MakeSimpleTypeDecl("value", type_names), None, None)
    if is_pointer:
        parameter_value.type = c_ast.PtrDecl([], parameter_value.type)

    fun_result = MakeSimpleTypeDecl(name, ["int"])
    return c_ast.Decl(
        name, [], [], [], c_ast.FuncDecl(
            c_ast.ParamList([parameter_format, parameter_value]),
            fun_result), None, None)


PUTS = c_ast.Decl(
    "puts", [], [], [], c_ast.FuncDecl(
        c_ast.ParamList([
            c_ast.Decl("s", [], [], [],
                       c_ast.PtrDecl([], MakeSimpleTypeDecl("s", ["char"])), None, None)
        ]),
        MakeSimpleTypeDecl("puts", ["int"])), None, None)

PRINTF_PROTOTYPES = {
    "printf_u": MakePrintfStyleDecl("printf_u", ["long", "long", "unsigned"]),
    "printf_d": MakePrintfStyleDecl("printf_d", ["long", "long"]),
    "printf_f": MakePrintfStyleDecl("printf_f", ["double"]),
    "printf_c": MakePrintfStyleDecl("printf_c", ["char"]),
    "printf_p": MakePrintfStyleDecl("printf_p", ["void"], True),
    "printf_s": MakePrintfStyleDecl("printf_s", ["char"], True)
}


PRINTF_DISPATCH = {
    "c": "printf_c",
    "s": "printf_s",
    "d": "printf_d",
    "p": "printf_p",
    #
    "u": "printf_u",
    "o": "printf_u",
    "x": "printf_u",
    #
    "e": "printf_e",
    "f": "printf_f",
    "g": "printf_g",
}


class FormatOptions:

    def __init__(self, s: str) -> None:
        m = PRINTF_OPTION.match(s)
        assert m
        flags, width, precision, length, kind = m.groups()
        self.kind = kind
        self.length = LENGTH_TRANSLATION.get(length, "")
        self.precision = int(precision[1:]) if precision else -1
        self.width = int(width) if width else -1
        self.show_sign = "+" in flags
        self.adjust_left = "-" in flags
        self.pad_with_zero = "0" in flags
        self.space_for_plus = " " in flags

    def __str__(self):
        f = []
        if self.show_sign: f.append("+")
        if self.adjust_left: f.append("-")
        if self.pad_with_zero: f.append("0")
        if self.space_for_plus: f.append(" ")
        return "[FormatOptions (%s) %d %d %s %s]" % ("".join(f), self.width, self.precision, self.length, self.kind)


def TokenizeFormatString(s: str):
    out = []
    last = 0

    def add_plain(start, end):
        if start != end:
            plain = s[start: end]
            out.append(plain if plain != "%%" else "%")

    for m in PRINTF_OPTION.finditer(s):
        start, end = m.span()
        add_plain(last, start)
        last = end
        out.append(m.group(0))
    add_plain(last, len(s))
    return out


# ================================================================================
# This transformation splits printf calls with constant format string into several printf
# calls. Each of which has at most one argument besides the format string
# This eliminates the primary use case of variable argument lists.
#
# if `use_specialized_printf` is true the printfs will also be renamed based on
# PRINTF_DISPATCH and the printf prototype will be replaced by PRINTF_PROTOTYPES.
# printf with only a single argument after splitting will renamed into `puts`
#
# This invalidates sym_tab and type_tab
# ================================================================================
def _IsSuitablePrintf(node: c_ast.Node, _):
    if not isinstance(node, c_ast.FuncCall): return None
    if not isinstance(node.name, c_ast.ID): return None
    if node.name.name != "printf": return None
    assert isinstance(node.args, c_ast.ExprList)
    assert len(node.args.exprs) > 0
    format_arg = node.args.exprs[0]
    if not isinstance(format_arg, c_ast.Constant): return None
    assert format_arg.type == "string"
    return True


def MakePrintfCall(fmt_str, arg_node: Optional[c_ast.Node], use_specialized_printf):
    args = [c_ast.Constant("string", '"' + fmt_str + '"')]
    if arg_node:
        args.append(arg_node)
        name = PRINTF_DISPATCH[fmt_str[-1]]
    else:
        name = "puts"
    if not use_specialized_printf:
        name = "printf"
    return c_ast.FuncCall(c_ast.ID(name), c_ast.ExprList(args))


def _DoPrintfSplitter(call: c_ast.FuncCall, parent, use_specialized_printf):
    args = call.args.exprs
    fmt_pieces = TokenizeFormatString(args[0].value[1:-1])
    if len(fmt_pieces) <= 1:
            if use_specialized_printf:
                call.name.name = "puts"
            return

    stmts = common.GetStatementList(parent)
    if not stmts:
        stmts = [call]
        common.ReplaceNode(parent, call, c_ast.Compound(stmts))

    calls = []
    args = args[1:]  # skip the format string
    for f in fmt_pieces:
        arg = None
        if f[0] == '%' and len(f) > 1:
            arg = args.pop(0)
        c = MakePrintfCall(f, arg, use_specialized_printf)
        calls.append(c)
    pos = stmts.index(call)
    stmts[pos:pos + 1] = calls


def PrintfSplitterTransform(ast: c_ast.FileAST, use_specialized_printf):
    candidates = common.FindMatchingNodesPostOrder(ast, ast, _IsSuitablePrintf)

    for call, parent in candidates:
        _DoPrintfSplitter(call, parent, use_specialized_printf)
    if not use_specialized_printf or len(candidates) == 0:
        return
    ext = ast.ext
    to_be_deleted = []
    for node in ext:
        if isinstance(node, c_ast.Decl) and node.name in {"puts", "printf"}:
            to_be_deleted.append(node)
    for node in to_be_deleted:
        ext.remove(node)
    ext[0:0] = [PUTS] + list(PRINTF_PROTOTYPES.values())


if __name__ == "__main__":
    import sys

    for a in sys.argv[1:]:
        print([str(x) for x in TokenizeFormatString(a)])
