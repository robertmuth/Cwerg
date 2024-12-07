#!/bin/env python3
"""Pretty printer (PP) for Cwerg AST to HTML

"""

import logging

from FE import cwast
from FE import pp_sexpr

from FE import mod_pool

logger = logging.getLogger(__name__)


############################################################
# Pretty Print HTML
############################################################
def _RenderIndent(n):
    return ["<span class=indent>", "&emsp;" * 2 * n, "</span>"]


def _CircledLetterEntity(c):
    offset = ord(c.upper()) - ord('A')
    return f"&#{0x24b6 + offset};"


def _DecorateNode(node_name, node):
    problems = []
    if node.x_srcloc is None:
        problems.append("missing srcloc")
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS and node.x_type is None:
        problems.append("missing type")

    out = ["<span class=name>", node_name, "</span>"]
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
        out += ["<span class=type title='",
                node.x_type.name, "'>", _CircledLetterEntity("T"), "</span>"]
    if cwast.NF.VALUE_ANNOTATED in node.FLAGS and node.x_value is not None:
        out += ["<span class=value title='",
                str(node.x_value), "'>", _CircledLetterEntity("V"), "</span>"]
    if cwast.NF.CONTROL_FLOW in node.FLAGS:
        targets = [f"{node.x_target}"]

        out += ["<span class=problems title='",
                "\n".join(targets), "'>", _CircledLetterEntity("C"), "</span>"]
    if problems:
        out += ["<span class=problems title='",
                "\n".join(problems), "'>", _CircledLetterEntity("X"), "</span>"]
    return out


def _RenderRecursivelyHTML(node, out, indent: int):
    line = out[-1]
    abbrev = pp_sexpr.MaybeSimplifyLeafNode(node)
    if abbrev:
        abbrev = abbrev.replace("<", "&lt;").replace(">", "&gt;")
        if isinstance(node, (cwast.ValNum, cwast.ValString, cwast.Id)):
            line.append(abbrev)
        else:
            line += _DecorateNode(abbrev, node)
        return

    node_name, fields = pp_sexpr.GetNodeTypeAndFields(node)
    line += _DecorateNode("(" + node_name, node)

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
        elif field_kind is cwast.NFK.NAME:
            line.append(
                " " + str(str(val).replace("<", "&lt;").replace(">", "&gt;")))
        elif field_kind is cwast.NFK.KIND:
            line.append(" " + val.name)
        elif field_kind is cwast.NFK.NODE:
            line.append(" ")
            _RenderRecursivelyHTML(val, out, indent)
        elif field_kind is cwast.NFK.LIST:
            extra_indent = pp_sexpr.GetColonIndent(field)
            if not val:
                line.append(" []")
            else:
                line.append(" [")
                for cc in val:
                    out.append(_RenderIndent(indent + extra_indent))
                    _RenderRecursivelyHTML(cc, out, indent + extra_indent)
                if field == "body_mod":
                    out.append(_RenderIndent(indent))
                out[-1].append("]")
        elif field_kind is cwast.NFK.NAME_LIST:
            line.append(f" [{' '.join(val)}]")
        else:
            assert False, f"{node_name} {nfd}"

    line = out[-1]
    line.append(")")
    if cwast.NF.TOP_LEVEL in node.FLAGS:
        out.append(["<p></p>"])


def PrettyPrintHTML(mod: cwast.DefMod):  # -> list[Tuple[int, str]]:
    out = [[
        """<html>
           <style>
           body { font-family: monospace; }
           span.name { font-weight: bold; }
           </style>"""]
    ]
    _RenderRecursivelyHTML(mod, out, 0)
    out += [["</html>"]]
    for a in out:
        print("".join(a))
        print("<br>")


############################################################
#
############################################################
if __name__ == "__main__":
    import os
    import argparse
    import pathlib

    from FE import type_corpus
    from FE import symbolize
    from FE import typify
    from FE import eval
    from FE import identifier

    def main() -> int:
        parser = argparse.ArgumentParser(description='pretty_printer')
        parser.add_argument('files', metavar='F', type=str, nargs='+',
                            help='an input source file')
        args = parser.parse_args()

        logging.basicConfig(level=logging.WARN)
        logger.setLevel(logging.INFO)
        assert len(args.files) == 1
        assert args.files[0].endswith(".cw")

        cwd = os.getcwd()
        mp: mod_pool.ModPool = mod_pool.ModPool(pathlib.Path(cwd) / "Lib")
        main = str(pathlib.Path(args.files[0][:-3]).resolve())
        mp.ReadModulesRecursively([main], add_builtin=True)
        mod_topo_order = mp.ModulesInTopologicalOrder()
        fun_id_gens = identifier.IdGenCache()
        symbolize.MacroExpansionDecorateASTWithSymbols(
            mod_topo_order, fun_id_gens)
        for mod in mod_topo_order:
            cwast.StripFromListRecursively(mod, cwast.DefMacro)
        tc = type_corpus.TypeCorpus(type_corpus.STD_TARGET_X64)
        typify.DecorateASTWithTypes(mod_topo_order, tc)
        eval.DecorateASTWithPartialEvaluation(mod_topo_order)

        for mod in mod_topo_order:
            PrettyPrintHTML(mod)
        return 0

    exit(main())
