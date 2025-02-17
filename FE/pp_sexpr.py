#!/bin/env python3
"""SEXPR Pretty printer (PP) for Cwerg AST to sexpr syntax

"""

import logging

from typing import Optional

from FE import cwast
from Util import pretty as PP


logger = logging.getLogger(__name__)


def MaybeSimplifyLeafNode(node) -> Optional[str]:
    if isinstance(node, cwast.TypeBase):
        return cwast.BaseTypeKindToKeyword(node.base_type_kind)
    elif isinstance(node, cwast.ValUndef):
        return "undef"
    elif isinstance(node, cwast.TypeAuto):
        return "auto"
    elif isinstance(node, cwast.Id):
        return node.FullName()
    elif isinstance(node, cwast.MacroId):
        return str(node.name)
    elif isinstance(node, cwast.ValTrue):
        return "true"
    elif isinstance(node, cwast.ValFalse):
        return "false"
    elif isinstance(node, cwast.ValNum):
        return node.number
    elif isinstance(node, cwast.ValVoid):
        return "void_val"
    elif isinstance(node, cwast.ValString):
        k = node.str_kind
        quotes = '"""' if k in (cwast.STR_KIND.HEX_TRIPLE,
                                cwast.STR_KIND.RAW_TRIPLE,
                                cwast.STR_KIND.NORMAL_TRIPLE) else '"'
        prefix = ""
        if k in (cwast.STR_KIND.RAW_TRIPLE, cwast.STR_KIND.RAW):
            prefix = "r"
        elif k in (cwast.STR_KIND.HEX_TRIPLE, cwast.STR_KIND.HEX):
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
        return cwast.UNARY_EXPR_SHORTCUT_SEXPR_INV[node.unary_expr_kind], fields
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


def GetDoc(node):
    for nfd in node.ATTRS:
        if nfd.name == "doc":
            val = getattr(node, "doc")
            return val
    return None


def _RenderColonList(out, val: list):
    if not val:
        return
    out += [PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
    add_break = False
    for cc in val:
        if add_break:
            out += [PP.Break()]
        add_break = True
        _RenderRecursivelyToIR(out, cc)
    out += [PP.End()]


def _RenderList(out, val: list, field: str):
    if not val:
        out += [PP.String("[]")]
        return
    out += [PP.Begin(PP.BreakType.INCONSISTENT, 4), PP.String("[")]
    width = 0
    for cc in val:
        out += [PP.Break(width)]
        width = 1
        _RenderRecursivelyToIR(out, cc)
    out += [PP.Break(0), PP.String("]"), PP.End()]


def _RenderMacroInvoke(out, node: cwast.MacroInvoke):
    out += [PP.Begin(PP.BreakType.INCONSISTENT, 4),
            PP.String("("),
            PP.WeakBreak(0),
            PP.String(str(node.name))]

    for a in node.args:
        if isinstance(a, cwast.EphemeralList):
            if a.colon:
                out += [PP.Break(0), PP.String(":"), PP.End()]
                _RenderColonList(out, a.args)
                out += [PP.Begin(PP.BreakType.INCONSISTENT, 4)]
            else:
                out += [PP.Break()]
                _RenderList(out, a.args)
        else:
            out += [PP.Break()]
            _RenderRecursivelyToIR(out, a)

    out += [PP.String(")"), PP.End()]


_ATTR_MODE = {
    "doc": "skip",  # handled elsewhere
    "mut": "skip",
    "ref": "after",
    "pub": "after",
    "init": "after",
    "fini": "after",
    "extern": "after",
    "popl": "after",
    "builtin": "after",
    "cdecl": "after",
    "polymorphic": "after",
    "arg_ref": "after",
    "res_ref": "after",
    "unchecked": "after",
    "wrapped": "after",
    "untagged": "after",
    "poly": "after",
    "preserve_mut": "after",
}


def _RenderAttr(out, node):
    #   doc = GetDoc(node)
    #    if doc:
    #        out += [PP.LineBreak(), PP.String(f"@doc {doc}"), PP.LineBreak()]

    for nfd in node.ATTRS:
        mode = _ATTR_MODE[nfd.name]

        if mode == "skip":
            continue
        assert mode == "after"

        val = getattr(node, nfd.name)
        if not val:
            continue
        assert isinstance(val, bool)
        out += [PP.String(f"@{nfd.name}"), PP.WeakBreak(1)]


def _RenderRecursivelyToIR(out, node):
    if cwast.NF.TOP_LEVEL in node.FLAGS:
        out.append(PP.LineBreak())
    abbrev = MaybeSimplifyLeafNode(node)
    if abbrev:
        out.append(PP.String(abbrev))
        return

    if isinstance(node, cwast.MacroInvoke):
        _RenderMacroInvoke(out, node)
        return

    if isinstance(node, cwast.ValPoint) and isinstance(node.point, cwast.ValAuto) and not node.doc:
        _RenderRecursivelyToIR(out, node.value_or_undef)
        return

    node_name, fields = GetNodeTypeAndFields(node)
    if isinstance(node, (cwast.DefGlobal, cwast.DefVar, cwast.DefGlobal,
                         cwast.TypePtr, cwast.TypeSpan, cwast.ExprAddrOf,
                         cwast.ExprFront)):
        if node.mut:
            node_name += "!"

    out += [PP.Begin(PP.BreakType.INCONSISTENT, 4),
            PP.String("(")]

    _RenderAttr(out, node)
    out += [PP.WeakBreak(0), PP.String(node_name)]

    for nfd in fields:
        field_kind = nfd.kind
        field = nfd.name
        val = getattr(node, nfd.name)

        if cwast.IsFieldWithDefaultValue(field, val):
            continue

        # if field_kind is not cwast.NFK.LIST or field != "body_f":
        #    line.append(spacer)
        # spacer = str(field_kind.value)

        if field_kind is cwast.NFK.STR:
            out += [PP.Break(), PP.String(str(val))]
        elif field_kind is cwast.NFK.NAME:
            out += [PP.Break(), PP.String(str(val))]
        elif field_kind is cwast.NFK.KIND:
            out += [PP.Break(), PP.String(val.name)]
        elif field_kind is cwast.NFK.NODE:
            out += [PP.Break()]
            _RenderRecursivelyToIR(out, val)
        elif field_kind is cwast.NFK.LIST:
            if field in ("items", "fields", "body_mod", "body", "body_t", "body_f", "body_for",
                         "cases", "body_macro"):
                out += [PP.Break(0), PP.String(":"), PP.End()]
                _RenderColonList(out, val)
                out += [PP.Begin(PP.BreakType.INCONSISTENT, 4)]
            else:
                out += [PP.Break()]
                _RenderList(out, val, field)
        else:
            assert False, f"unexpected field {field}"

    out += [PP.String(")"), PP.End()]


def PrettyPrint(mod: cwast.DefMod, outp):
    out: list[PP.Token] = []
    _RenderRecursivelyToIR(out, mod)
    result = PP.PrettyPrint(out, 80)
    print(result, file=outp)


############################################################
#
############################################################
if __name__ == "__main__":
    import argparse

    from FE import parse_sexpr

    def main():
        parser = argparse.ArgumentParser(description='pretty_printer')
        parser.add_argument("-inplace",
                            action="store_true", help='update files in place')
        parser.add_argument('files', metavar='F', type=str, nargs='+',
                            help='an input source file')
        args = parser.parse_args()

        logging.basicConfig(level=logging.WARN)
        logger.setLevel(logging.INFO)
        for fn in args.files:
            assert fn.endswith(".cws")
            fp = open(fn, encoding="utf8")
            mod = parse_sexpr.ReadModFromStream(fp, fn)
            fp.close()
            out: list[PP.Token] = []
            _RenderRecursivelyToIR(out, mod)
            result = PP.PrettyPrint(out)
            if args.inplace:
                fp = open(fn, "w", encoding="utf8")
                fp.write(result)
                fp.close()
            else:
                print(result)
    main()
