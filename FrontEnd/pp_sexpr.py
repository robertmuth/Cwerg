#!/usr/bin/python3
"""SEXPR Pretty printer (PP) for Cwerg AST

"""

import logging

from typing import Optional

from FrontEnd import cwast


logger = logging.getLogger(__name__)


def MaybeSimplifyLeafNode(node) -> Optional[str]:
    if isinstance(node, cwast.TypeBase):
        return cwast.BaseTypeKindToKeyword(node.base_type_kind)
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


STMT_LIST_INDENT = 4
EXPR_LIST_INDENT = 8


def GetColonIndent(field: str) -> int:
    return 0 if field == "body_mod" else STMT_LIST_INDENT

############################################################
# Pretty Print
############################################################


def GetExprIndent(_) -> int:
    return EXPR_LIST_INDENT


def GetDoc(node):
    for field, _ in node.ATTRS:
        if field == "doc":
            val = getattr(node, "doc")
            return val
    return None


def _RenderColonList(val: list, field: str, out, indent: int):

    extra_indent = GetColonIndent(field)
    line = out[-1]
    if field == "body_f":
        out.append([" " * (indent + extra_indent - 3) + ":"])
        for cc in val:
            out.append([" " * (indent + extra_indent)])
            _RenderRecursivelyToIR(
                cc, out, indent + extra_indent)
    else:
        line.append(":")
        for cc in val:
            out.append([" " * (indent + extra_indent)])
            _RenderRecursivelyToIR(cc, out, indent + extra_indent)
            # extra line between top level nodes
            if field == "body_mod":
                out.append([" " * indent])


def _ListIsCompact(val: list):
    for v in val:
        if GetDoc(v):
            return False
    if len(val) > 2:
        return False
    # for x in val:
    #    if isinstance(x, cwast.Comment):
    #        return False
    return True


def _RenderList(val: list, field: str, out, indent: int):
    extra_indent = GetExprIndent(field)
    line = out[-1]
    if not val:
        line.append("[]")
    elif _ListIsCompact(val):
        line.append("[")
        sep = ""
        for cc in val:
            line = out[-1]
            line.append(sep)
            sep = " "
            _RenderRecursivelyToIR(cc, out, indent + extra_indent)
        out[-1].append("]")

    else:
        line.append("[")
        for cc in val:
            out.append([" " * (indent + extra_indent)])
            _RenderRecursivelyToIR(cc, out, indent + extra_indent)
        out[-1].append("]")


def _RenderMacroInvoke(node: cwast.MacroInvoke, out, indent: int):
    line = out[-1]
    line.append("(" + node.name)
    for a in node.args:
        line = out[-1]
        if isinstance(a, cwast.EphemeralList):
            line.append(" ")
            if a.colon:
                _RenderColonList(a.args, "dummy", out, indent)
            else:
                _RenderList(a.args, "dummy", out, indent)
        else:
            line.append(" ")
            _RenderRecursivelyToIR(a, out, indent)
    line = out[-1]
    line.append(")")


def _RenderLomgAttr(node):
    pass


def _RenderShortAttr(node):
    out = []
    for field, _ in node.ATTRS:
        if field == "doc":
            # handled elsewhere
            continue
        elif field == "mut":
            # handled elsewhere
            continue
        val = getattr(node, field)
        if not val:
            continue
        if isinstance(val, bool):
            out.append(f"@{field} ")
        else:
            assert isinstance(val, str)
            out.append(f"@{field} {val} ")
    return out


def _RenderRecursivelyToIR(node, out, indent: int):
    if cwast.NF.TOP_LEVEL in node.FLAGS:
        out.append([""])
    line: list[str] = out[-1]
    abbrev = MaybeSimplifyLeafNode(node)
    if abbrev:
        line.append(abbrev)
        return

    doc = GetDoc(node)
    if doc:
        line.append("@doc ")
        line.append(doc)
        out.append([" " * indent])
        line = out[-1]

    if isinstance(node, cwast.MacroInvoke):
        _RenderMacroInvoke(node, out, indent)
        return

    node_name, fields = GetNodeTypeAndFields(node)
    if isinstance(node, (cwast.DefGlobal, cwast.DefVar, cwast.DefGlobal,
                         cwast.TypePtr, cwast.TypeSlice, cwast.ExprAddrOf,
                         cwast.ExprFront, cwast.MacroVar)):
        if node.mut:
            node_name += "!"



    line += _RenderShortAttr(node)
    line.append("(")
    spacer = ""
    if not isinstance(node, cwast.ExprCall):
        line.append(node_name)
        spacer = " "
    for field, nfd in fields:
        field_kind = nfd.kind
        line = out[-1]
        val = getattr(node, field)

        if cwast.IsFieldWithDefaultValue(field, val):
            continue

        if field_kind is not cwast.NFK.LIST or field != "body_f":
            line.append(spacer)
        spacer = " "
        # spacer = str(field_kind.value)

        if field_kind is cwast.NFK.STR:
            line.append(str(val))
        elif field_kind is cwast.NFK.KIND:
            line.append(val.name)
        elif field_kind is cwast.NFK.NODE:
            _RenderRecursivelyToIR(val, out, indent)
        elif field_kind is cwast.NFK.LIST:
            if field in ("items", "fields", "body_mod", "body", "body_t", "body_f", "body_for",
                         "cases", "body_macro"):
                _RenderColonList(val, field, out, indent)
            else:
                _RenderList(val, field, out, indent)
        elif field_kind is cwast.NFK.STR_LIST:
            line.append(f"[{' '.join(val)}]")
        else:
            assert False, f"unexpected field {field}"

    line = out[-1]
    line.append(")")

    if isinstance(node, cwast.DefMod):
        out.append([""])


def PrettyPrint(mod: cwast.DefMod):
    out = [[""]]
    _RenderRecursivelyToIR(mod, out, 0)
    for a in out:
        print("".join(a))


############################################################
#
############################################################
if __name__ == "__main__":
    import os
    import argparse
    import pathlib

    from FrontEnd import type_corpus
    from FrontEnd import parse_sexpr
    from FrontEnd import symbolize
    from FrontEnd import typify
    from FrontEnd import eval

    def main():
        parser = argparse.ArgumentParser(description='pretty_printer')
        parser.add_argument('-i', "--inplace",
                            action="store_true", help='update files in place')
        parser.add_argument('files', metavar='F', type=str, nargs='+',
                            help='an input source file')
        args = parser.parse_args()

        logging.basicConfig(level=logging.WARN)
        logger.setLevel(logging.INFO)
        for fn in args.files:
            assert fn.endswith(".cw")

            fp = open(fn, encoding="utf8")
            mods = parse_sexpr.ReadModsFromStream(fp)
            fp.close()
            assert len(mods) == 1
            out = [[""]]
            _RenderRecursivelyToIR(mods[0], out, 0)
            if args.inplace:
                fp = open(fn, "w", encoding="utf8")
                for a in out:
                    for b in a:
                        fp.write(b)
                    fp.write("\n")
                fp.close()
            else:
                for a in out:
                    print("".join(a))
    main()
