#!/usr/bin/python3

"""AST Nodes and SExpr reader/writer for the Cwerg frontend


"""

import sys
import re
import logging

from typing import List, Dict, Set, Optional, Union, Any

from FrontEnd import cwast

logger = logging.getLogger(__name__)
############################################################
# S-Expression Serialization (Introspection driven)
############################################################


# Note: we rely on the matching being done greedily
# we also allow for non-terminated string for better error handling
_TOKEN_CHAR = r"['](?:[^'\\]|[\\].)*(?:[']|$)"
_TOKEN_STR = r'"(?:[^"\\]|[\\].)*(?:"|$)'
_TOKEN_R_STR = r'r"(?:[^"])*(?:"|$)'
_TOKEN_NAMENUM = r'[^\[\]\(\)\' \r\n\t]+'
_TOKEN_OP = r'[\[\]\(\)]'

_TOKEN_MULTI_LINE_STR_START = r'"""(?:["]{0,2}(?:[^"\\]|[\\].))*(?:["]{3,5}|$)'
_TOKEN_R_MULTI_LINE_STR_START = r'r"""(?:["]{0,2}[^"])*(?:["]{3,5}|$)'

_RE_MULTI_LINE_STR_END = re.compile(
    r'^(?:["]{0,2}(?:[^"\\]|[\\].))*(?:["]{3,5}|$)')

_RE_R_MULTI_LINE_STR_END = re.compile(
    r'^(?:["]{0,2}[^"])*(?:["]{3,5}|$)')

_RE_TOKENS_ALL = re.compile("|".join(["(?:" + x + ")" for x in [
    # order is important: multi-line before regular
    _TOKEN_MULTI_LINE_STR_START, _TOKEN_R_MULTI_LINE_STR_START,
    _TOKEN_STR, _TOKEN_R_STR, _TOKEN_CHAR, _TOKEN_OP, _TOKEN_NAMENUM]]))


_RE_TOKEN_ID = re.compile(
    r'([_A-Za-z$][_A-Za-z$0-9]*::)*([_A-Za-z$%][_A-Za-z$0-9]*)(%[0-9]+)?')


_RE_TOKEN_NUM = re.compile(r'-?[.0-9][-+_.a-z0-9]*')


class ReadTokens:
    def __init__(self, fp, filename):
        self._fp = fp
        self.line_no = 0
        self._filename = filename
        self._tokens: List[str] = []

    def __iter__(self):
        return self

    def srcloc(self):
        return f"{self._filename}:{self.line_no}"

    def pushback(self, token):
        # TODO: line number fix up in rare cases
        self._tokens.append(token)

    def __next__(self):
        while not self._tokens:
            self._tokens = re.findall(_RE_TOKENS_ALL, next(self._fp))
            self._tokens.reverse()
            self.line_no += 1
        out = self._tokens.pop(-1)
        if not self._tokens:
            if not out.endswith('"""') and (out.startswith('"""') or out.startswith('r"""')):
                # hack for multi-line strings
                # print("@@ multiline string partial start", self.srcloc(), out)
                regex = _RE_R_MULTI_LINE_STR_END if out.startswith(
                    "r") else _RE_MULTI_LINE_STR_END
                while True:
                    line = next(self._fp)
                    self.line_no += 1
                    m: re.Match = regex.match(line)
                    if not m:
                        cwast.CompilerError(
                            self.srcloc(), "cannot parse multiline string constant")
                    g = m.group()
                    # print("@@ multiline string cont", g)
                    out += g
                    if len(g) != len(line):
                        rest = line[len(g):]
                        self._tokens = re.findall(_RE_TOKENS_ALL, rest)
                        self._tokens.reverse()
                        break
        return out


_SCALAR_TYPES = [
    #
    cwast.BASE_TYPE_KIND.SINT,
    cwast.BASE_TYPE_KIND.S8,
    cwast.BASE_TYPE_KIND.S16,
    cwast.BASE_TYPE_KIND.S32,
    cwast.BASE_TYPE_KIND.S64,
    #
    cwast.BASE_TYPE_KIND.UINT,
    cwast.BASE_TYPE_KIND.U8,
    cwast.BASE_TYPE_KIND.U16,
    cwast.BASE_TYPE_KIND.U32,
    cwast.BASE_TYPE_KIND.U64,
    #
    cwast.BASE_TYPE_KIND.R32,
    cwast.BASE_TYPE_KIND.R64,
]


def _MakeTypeBaseLambda(kind: cwast.BASE_TYPE_KIND):
    return lambda srcloc: cwast.TypeBase(kind, x_srcloc=srcloc)


# maps "atoms" to the nodes they will be expanded to
_SHORT_HAND_NODES = {
    "auto": lambda srcloc: cwast. TypeAuto(x_srcloc=srcloc),
    #
    "noret": _MakeTypeBaseLambda(cwast.BASE_TYPE_KIND.NORET),
    "bool": _MakeTypeBaseLambda(cwast.BASE_TYPE_KIND.BOOL),
    "void": _MakeTypeBaseLambda(cwast.BASE_TYPE_KIND.VOID),
    #
    "auto_val": lambda srcloc: cwast.ValAuto(x_srcloc=srcloc),
    "void_val": lambda srcloc: cwast.ValVoid(x_srcloc=srcloc),
    "undef": lambda srcloc: cwast.ValUndef(x_srcloc=srcloc),
    "true": lambda srcloc: cwast.ValTrue(x_srcloc=srcloc),
    "false": lambda srcloc: cwast.ValFalse(x_srcloc=srcloc),
    # see cwast.OPTIONAL_FIELDS
    "break": lambda srcloc: cwast.StmtBreak(target="", x_srcloc=srcloc),
    "continue": lambda srcloc: cwast.StmtContinue(target="", x_srcloc=srcloc),
}


for t in _SCALAR_TYPES:
    name = t.name.lower()
    _SHORT_HAND_NODES[name] = _MakeTypeBaseLambda(t)


def IsWellFormedStringLiteral(t: str):
    if t.endswith('"""'):
        return len(t) >= 6 and t.startswith('"""') or len(t) >= 7 and t.startswith('r"""')
    elif t.endswith('"'):
        return len(t) >= 2 and t.startswith('"') or len(t) >= 3 and t.startswith('r"')
    else:
        return False


def ExpandShortHand(t: str, srcloc) -> Any:
    """Expands atoms, ids, and numbers to proper nodes"""
    x = _SHORT_HAND_NODES.get(t)
    if x is not None:
        return x(srcloc)

    if IsWellFormedStringLiteral(t):
        logger.info("STRING %s at %s", t, srcloc)
        if t.startswith("r"):
            return cwast.ValString(True, t[1:], x_srcloc=srcloc)
        else:
            return cwast.ValString(False, t, x_srcloc=srcloc)
    elif _RE_TOKEN_ID.fullmatch(t):
        if t in cwast.NODES_ALIASES:
            cwast.CompilerError(srcloc, f"Reserved name used as ID: {t}")
        if t[0] == "$":
            return cwast.MacroId(t, x_srcloc=srcloc)
        logger.info("ID %s at %s", t, srcloc)
        return cwast.Id(t, x_srcloc=srcloc)
    elif _RE_TOKEN_NUM.fullmatch(t):
        logger.info("NUM %s at %s", t, srcloc)
        return cwast.ValNum(t, x_srcloc=srcloc)
    elif len(t) >= 2 and t[0] == "'" and t[-1] == "'":
        logger.info("CHAR %s at %s", t, srcloc)
        return cwast.ValNum(t, x_srcloc=srcloc)
    else:
        cwast.CompilerError(srcloc, f"unexpected token {repr(t)}")


def ReadNodeList(stream: ReadTokens, parent_cls):
    out = []
    while True:
        token = next(stream)
        if token == "]":
            break
        if token == "(":
            out.append(ReadSExpr(stream, parent_cls))
        else:
            out.append(ExpandShortHand(token, stream.srcloc()))
    return out


def ReadNodeColonList(stream: ReadTokens, parent_cls):
    out = []
    while True:
        token = next(stream)
        if token == ")" or token == ":" or token == "[":
            stream.pushback(token)
            break
        if token == "(":
            out.append(ReadSExpr(stream, parent_cls))
        else:
            out.append(ExpandShortHand(token, stream.srcloc()))
    return out


def ReadStrList(stream: ReadTokens) -> List[str]:
    out = []
    while True:
        token = next(stream)
        if token == "]":
            break
        else:
            out.append(token)
    return out


def ReadStrColonList(stream: ReadTokens) -> List[str]:
    out = []
    while True:
        token = next(stream)
        if token == ")" or token == ":" or token == "[":
            stream.pushback(token)
            break
        else:
            out.append(token)
    return out


def ReadPiece(field, token, stream: ReadTokens, parent_cls) -> Any:
    """Read a single component of an SExpr including lists."""
    nfd = cwast. ALL_FIELDS_MAP[field]
    if nfd.kind is cwast.NFK.FLAG:
        return bool(token)
    elif nfd.kind is cwast.NFK.STR:
        return token
    elif nfd.kind is cwast.NFK.INT:
        return token
    elif nfd.kind is cwast.NFK.KIND:
        assert nfd.extra is not None, f"{field} {token}"
        try:
            return nfd.extra[token]
        except KeyError:
            cwast.CompilerError(
                stream.srcloc(), f"Cannot convert {token} for {field}")
    elif nfd.kind is cwast.NFK.NODE:
        if token == "(":
            return ReadSExpr(stream, parent_cls)
        out = ExpandShortHand(token, stream.srcloc())
        if out is None:
            cwast.CompilerError(
                stream.srcloc(), f"Cannot expand {token} for {field}")
        return out
    elif nfd.kind is cwast.NFK.STR_LIST:
        if token == "[":
            return ReadStrList(stream)
        elif token == ":":
            return ReadStrColonList(stream)
        else:
            assert False, f"expected list start for: {field} {token}"

    elif nfd.kind is cwast.NFK.LIST:
        if token == "[":
            return ReadNodeList(stream, parent_cls)
        elif token == ":":
            return ReadNodeColonList(stream, parent_cls)
        else:
            assert False, f"expected list start in {parent_cls.__name__} for: {field} {token} at {stream.srcloc()}"

    else:
        assert None


def ReadMacroInvocation(tag, stream: ReadTokens):
    parent_cls = cwast.MacroInvoke
    srcloc = stream.srcloc()
    logger.info("Readdng MACRO INVOCATION %s at %s", tag, srcloc)
    args = []
    while True:
        token = next(stream)
        if token == ")":
            return cwast.MacroInvoke(tag, args, x_srcloc=srcloc)
        elif token == "(":
            args.append(ReadSExpr(stream, parent_cls))
        elif token == "[":
            args.append(cwast.EphemeralList(False, ReadNodeList(
                stream, parent_cls), x_srcloc=srcloc))
        elif token == ":":
            args.append(cwast.EphemeralList(True, ReadNodeColonList(
                stream, parent_cls), x_srcloc=srcloc))
        else:
            out = ExpandShortHand(token, stream.srcloc())
            assert out is not None, f"while processing {tag} unexpected macro arg: {token}"
            args.append(out)
    return args


def ReadRestAndMakeNode(cls, pieces: List[Any], fields: List[str], stream: ReadTokens):
    """Read the remaining componts of an SExpr (after the tag).

    Can handle optional bools at the beginning and an optional 'tail'
    """
    srcloc = stream.srcloc()
    logger.info("Readding TAG %s at %s", cls.__name__, srcloc)
    token = next(stream)
    flags = {}
    while token.startswith("@"):
        flags[token[1:]] = True
        token = next(stream)

    for field, nfd in fields:
        if token == ")":
            # we have reached the end before all the fields were processed
            # fill in default values
            optional_val = cwast.GetOptional(field, srcloc)
            if optional_val is None:
                cwast.CompilerError(
                    stream.srcloc(), f"in {cls.__name__} unknown optional (or missing) field: {field}")
            pieces.append(optional_val)
        elif nfd.kind is cwast.NFK.FLAG:
            if field in flags:
                pieces.append(True)
            else:
                pieces.append(False)
        else:
            pieces.append(ReadPiece(field, token, stream, cls))
            token = next(stream)
    if token != ")":
        cwast.CompilerError(stream.srcloc(
        ), f"while parsing {cls.__name__} expected node-end but got {token}")
    return cls(*pieces, x_srcloc=srcloc)


def ReadSExpr(stream: ReadTokens, parent_cls) -> Any:
    """The leading '(' has already been consumed"""
    tag = next(stream)
    if tag in cwast.UNARY_EXPR_SHORTCUT:
        return ReadRestAndMakeNode(cwast.Expr1, [cwast.UNARY_EXPR_SHORTCUT[tag]],
                                   cwast.Expr1.FIELDS[1:], stream)
    elif tag in cwast.BINARY_EXPR_SHORTCUT:
        return ReadRestAndMakeNode(cwast.Expr2, [cwast.BINARY_EXPR_SHORTCUT[tag]],
                                   cwast.Expr2.FIELDS[1:], stream)
    elif tag in cwast.POINTER_EXPR_SHORTCUT:
        return ReadRestAndMakeNode(cwast.ExprPointer, [cwast.POINTER_EXPR_SHORTCUT[tag]],
                                   cwast.ExprPointer.FIELDS[1:], stream)
    elif tag in cwast.ASSIGNMENT_SHORTCUT:
        return ReadRestAndMakeNode(cwast.StmtCompoundAssignment, [cwast.ASSIGNMENT_SHORTCUT[tag]],
                                   cwast.StmtCompoundAssignment.FIELDS[1:], stream)
    else:
        cls = cwast.NODES_ALIASES.get(tag)
        if not cls:
            # unknown node name - assume it is a macro
            return ReadMacroInvocation(tag, stream)
        assert cls is not None, f"[{stream.line_no}] Non node: {tag}"

        # This helps catching missing closing braces early
        if cwast.NF.TOP_LEVEL in cls.FLAGS:
            if parent_cls is not cwast.DefMod:
                cwast.CompilerError(stream.srcloc(
                ), f"toplevel node {cls.__name__} not allowed in {parent_cls.__name__}")

        return ReadRestAndMakeNode(cls, [], cls.FIELDS, stream)


def ReadModsFromStream(fp, fn="stdin") -> List[cwast.DefMod]:
    asts = []
    stream = ReadTokens(fp, fn)
    try:
        failure = False
        while True:
            t = next(stream)
            failure = True
            if t != "(":
                cwast.CompilerError(
                    stream.srcloc(), f"expect start of new node, got '{t}']")
            mod = ReadSExpr(stream, None)
            assert isinstance(mod, cwast.DefMod)
            cwast.DecorateIdsWithModule(mod)
            cwast.CheckAST(mod, set())
            asts.append(mod)
            failure = False
    except StopIteration:
        assert not failure, f"truncated file"
    return asts


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    ReadModsFromStream(sys.stdin)
