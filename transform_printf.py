#!/usr/bin/python3

import re
from typing import Optional

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


def MakePrintfCall(fmt_str, arg_node: Optional[c_ast.Node]):
    args = [c_ast.Constant("string", '"' + fmt_str + '"')]
    if arg_node: args.append(arg_node)
    return c_ast.FuncCall(c_ast.ID("printf"), c_ast.ExprList(args))


def _DoPrintfSplitter(call: c_ast.FuncCall, parent, meta_info: meta.MetaInfo):
    args = call.args.exprs
    fmt_pieces = TokenizeFormatString(args[0].value[1:-1])
    if not fmt_pieces: return
    if len(fmt_pieces) == 1: return

    stmts = common.GetStatementList(parent)
    if not stmts:
        assert False, parent

    calls = []
    args = args[1:]  # skip the format string
    for f in fmt_pieces:
        arg = None
        if f[0] == '%' and len(f) > 1:
            arg = args.pop(0)
        c = MakePrintfCall(f, arg)
        meta_info.type_links[c] = meta_info.type_links[call]
        meta_info.type_links[c.args] = meta_info.type_links[call.args]
        meta_info.type_links[c.args.exprs[0]] = meta_info.type_links[call.args.exprs[0]]
        meta_info.type_links[c.name] = meta_info.type_links[call.name]
        meta_info.sym_links[c.name] = meta_info.sym_links[call.name]
        calls.append(c)
    pos = stmts.index(call)
    stmts[pos:pos + 1] = calls


def PrintfSplitterTransform(ast: c_ast.Node, meta: meta.MetaInfo):
    candidates = common.FindMatchingNodesPostOrder(ast, ast, _IsSuitablePrintf)

    for call, parent in candidates:
        _DoPrintfSplitter(call, parent, meta)


if __name__ == "__main__":
    import sys

    for a in sys.argv[1:]:
        print([str(x) for x in TokenizeFormatString(a)])
