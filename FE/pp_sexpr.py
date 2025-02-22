#!/bin/env python3
"""SEXPR Pretty printer (PP) for Cwerg AST to sexpr syntax

"""

import logging

from typing import Optional

from FE import cwast
from Util import pretty as PP


logger = logging.getLogger(__name__)


_BLOCK_INDENT = 4
_CONT_INDENT = 2
_MOD_INDENT = 0


def _MaybeSimplifyLeafNode(node) -> Optional[str]:
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


def _GetNodeTypeAndFields(node, condense=True):
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


############################################################
# Pretty Print
############################################################


def _GetDoc(node):
    for nfd in node.ATTRS:
        if nfd.name == "doc":
            val = getattr(node, "doc")
            return val
    return None


def _RenderColonList(out, val: list, indent: int):
    if not val:
        return
    out += [PP.Beg(PP.BreakType.FORCE_LINE_BREAK, indent)]
    add_break = False
    for cc in val:
        if add_break:
            out += [PP.Brk()]
        add_break = True
        _RenderRecursivelyToIR(out, cc)
    out += [PP.End()]


def _RenderList(out, val: list, field: str):
    if not val:
        out += [PP.Str("[]")]
        return
    out += [PP.Beg(PP.BreakType.INCONSISTENT, _BLOCK_INDENT), PP.Str("[")]
    width = 0
    for cc in val:
        out += [PP.Brk(width)]
        width = 1
        _RenderRecursivelyToIR(out, cc)
    out += [PP.Brk(0), PP.Str("]"), PP.End()]


def _RenderMacroInvoke(out, node: cwast.MacroInvoke):
    out += [PP.Beg(PP.BreakType.INCONSISTENT, _CONT_INDENT),
            PP.Str("("),
            PP.NoBreak(0),
            PP.Str(str(node.name))]

    for a in node.args:
        if isinstance(a, cwast.EphemeralList):
            if a.colon:
                out += [PP.Brk(0), PP.Str(":"), PP.End()]
                _RenderColonList(out, a.args, 4)
                out += [PP.Beg(PP.BreakType.INCONSISTENT, _CONT_INDENT)]
            else:
                out += [PP.Brk()]
                _RenderList(out, a.args)
        else:
            out += [PP.Brk()]
            _RenderRecursivelyToIR(out, a)

    out += [PP.Str(")"), PP.End()]


# printed after the open paren
_AFTER_ANNOTATIONS = set([
    "ref", "pub", "init", "fini", "extern", "builtin",
    "cdecl", "arg_ref", "res_ref", "unchecked", "wrapped",
    "untagged", "poly", "preserve_mut"])


def _RenderAttr(out, node):
    for nfd in node.ATTRS:
        if nfd.name not in _AFTER_ANNOTATIONS:
            continue

        val = getattr(node, nfd.name)
        if not val:
            continue
        assert isinstance(val, bool)
        out += [PP.Str(f"@{nfd.name}"), PP.NoBreak(1)]


def _RenderRecursivelyToIR(out, node):
    if cwast.NF.TOP_LEVEL in node.FLAGS:
        out.append(PP.LineBreak())

    doc = _GetDoc(node)
    if doc:
        out += [PP.Str(f"@doc {doc}"), PP.LineBreak()]
    abbrev = _MaybeSimplifyLeafNode(node)
    if abbrev:
        out.append(PP.Str(abbrev))
        return

    if isinstance(node, cwast.MacroInvoke):
        _RenderMacroInvoke(out, node)
        return

    if isinstance(node, cwast.ValPoint) and isinstance(node.point, cwast.ValAuto) and not node.doc:
        _RenderRecursivelyToIR(out, node.value_or_undef)
        return

    node_name, fields = _GetNodeTypeAndFields(node)
    if isinstance(node, (cwast.DefGlobal, cwast.DefVar, cwast.DefGlobal,
                         cwast.TypePtr, cwast.TypeSpan, cwast.ExprAddrOf,
                         cwast.ExprFront)):
        if node.mut:
            node_name += "!"

    out += [PP.Beg(PP.BreakType.INCONSISTENT, _CONT_INDENT),
            PP.Str("(")]

    _RenderAttr(out, node)
    out += [PP.NoBreak(0), PP.Str(node_name)]

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
            out += [PP.Brk(), PP.Str(str(val))]
        elif field_kind is cwast.NFK.NAME:
            out += [PP.Brk(), PP.Str(str(val))]
        elif field_kind is cwast.NFK.KIND:
            out += [PP.Brk(), PP.Str(val.name)]
        elif field_kind is cwast.NFK.NODE:
            out += [PP.Brk()]
            _RenderRecursivelyToIR(out, val)
        elif field_kind is cwast.NFK.LIST:
            if field in ("items", "fields", "body_mod", "body", "body_t", "body_f", "body_for",
                         "cases", "body_macro"):
                indent = _MOD_INDENT if field == "body_mod" else _BLOCK_INDENT
                out += [PP.Brk(0), PP.Str(":"), PP.End()]
                _RenderColonList(out, val, indent)
                out += [PP.Beg(PP.BreakType.INCONSISTENT, _CONT_INDENT)]
            else:
                out += [PP.Brk()]
                _RenderList(out, val, field)
        else:
            assert False, f"unexpected field {field}"

    out += [PP.Str(")"), PP.End()]

############################################################
#
############################################################


def PrettyPrint(mod: cwast.DefMod, outp):
    out: list[PP.Token] = [PP.Beg(PP.BreakType.CONSISTENT, 0)]
    _RenderRecursivelyToIR(out, mod)
    out += [PP.End()]
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
