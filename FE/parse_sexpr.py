#!/bin/env python3

"""AST Nodes and SExpr reader/writer for the Cwerg frontend


"""

import re
import logging
import io

from typing import Any, Union
from collections.abc import Callable

from FE import cwast
from FE import string_re

logger = logging.getLogger(__name__)
############################################################
# S-Expression Serialization (Introspection driven)
############################################################


def ReCombine(lst: list[str]):
    return "|".join("(?:" + x + ")" for x in lst)


# Note: we rely on the matching being done greedily
# we also allow for non-terminated string for better error handling
_TOKEN_CHAR = r"['](?:[^'\\]|[\\].)*(?:[']|$)"

_TOKEN_NAMENUM = r'[^\[\]\(\)\' \r\n\t]+'
_TOKEN_OP = r'[\[\]\(\)]'


_RE_TOKENS_ALL = re.compile(ReCombine([
    # order is important: multi-line before regular
    string_re.MULTI_START,
    string_re.MULTI_START_R,
    string_re.MULTI_START_X,
    string_re.STR, string_re.R_STR, _TOKEN_CHAR, _TOKEN_OP, _TOKEN_NAMENUM]))

# TODO: make this stricter WRT to :: vs :
_RE_TOKEN_ID = re.compile(
    r'([_A-Za-z$][_A-Za-z$0-9]*:+)*([_A-Za-z$%][_A-Za-z$0-9]*)(%[0-9]+)?!?@?')


##
_RE_REAL_TYPE_OPT = r'(?:r32|r64)?'
_RE_INT_TYPE_OPT = r'(?:u8|u16|u32|u64|uint|s8|s16|s32|s64|sint)?'
_RE_NUM_TYPE_OPT = r'(?:u8|u16|u32|u64|uint|s8|s16|s32|s64|sint|r32|r64)?'

# Note: sign is mandatory to distinguish nans from identifiers
_RE_NUM_REAL_NAN = r'[-+](?:[.]inf|[.]nan)(?:_r32|_r64)?'
_RE_NUM_REAL_HEX = r'[-+]?0x[0-9a-f][0-9a-f_]*[.]?(?:[0-9a-f][0-9a-f_]*)?p[-+]?[0-9][0-9_]*'
# Note, some extra care so that the decimal dot can not be confused with record field accesses
_RE_NUM_REAL_DEC_EXP_OPT = r'(?:e[-+]?[0-9][_0-9]*)?'
_RE_NUM_REAL_DEC_FRAC = r'[-+]?[.]([0-9][0-9_]*)'
_RE_NUM_REAL_OR_INT_DEC = r'[-+]?[0-9][_0-9]*[.]?(?:[0-9][0-9_]*)?'
##
# Note: only lower case accepted
_RE_NUM_INT_HEX = '0x[0-9a-f][_0-9a-f]*'
_RE_NUM_INT_BIN = '0b[01][_01]*'


# hex is lower case
RE_STR_NUM = ReCombine([
    # REALs
    _RE_NUM_REAL_NAN + _RE_REAL_TYPE_OPT,
    _RE_NUM_REAL_HEX + _RE_REAL_TYPE_OPT,
    _RE_NUM_REAL_DEC_FRAC +
    _RE_NUM_REAL_DEC_EXP_OPT +
    _RE_REAL_TYPE_OPT,
    # INTs
    _RE_NUM_INT_HEX + _RE_INT_TYPE_OPT,
    _RE_NUM_INT_BIN + _RE_INT_TYPE_OPT,
    # REAL OR INT
    # This must come after HEX and Bin since it matches the leading zero
    _RE_NUM_REAL_OR_INT_DEC + _RE_NUM_REAL_DEC_EXP_OPT + _RE_NUM_TYPE_OPT
])

RE_TOKEN_NUM = re.compile(RE_STR_NUM)

assert RE_TOKEN_NUM.match("5_r32").group() == "5_r32"
assert RE_TOKEN_NUM.match("5_u16").group() == "5_u16"


def ReadAttrs(t: str, attr: dict[str, Any], stream):
    """attr is indended to be used for node creation as a  **attr parameter."""
    while t.startswith("@"):
        tag = t[1:]
        val: Union[bool, str] = True
        if tag == "doc":
            val = next(stream)
        attr[tag] = val
        t = next(stream)
    return t


_MULTI_LINE_END_RE = {
    '"""': re.compile(string_re.MULTI_END),
    'r"""': re.compile(string_re.MULTI_END_R),
    'x"""': re.compile(string_re.MULTI_END_X),
}


class ReadTokens:
    """Reader for Lexical tokens implemented as a generator"""

    def __init__(self: Any, fp: io.TextIOWrapper, filename: str):
        self._fp = fp
        self.line_no = 0
        self._filename = filename
        self._tokens: list[str] = []

    def __iter__(self):
        return self

    def srcloc(self):
        return cwast.SrcLoc(self._filename, self.line_no)

    def pushback(self, token):
        # TODO: line number fix up in rare cases
        self._tokens.append(token)

    def __next__(self: "ReadTokens"):
        while not self._tokens:
            self._tokens = re.findall(_RE_TOKENS_ALL, next(self._fp))
            self._tokens.reverse()
            self.line_no += 1
        out = self._tokens.pop(-1)
        if self._tokens:
            return out
        if not out.endswith('"""'):
            for prefix, regex in _MULTI_LINE_END_RE.items():
                if out.startswith(prefix):
                    break
            else:
                return out
            # hack for multi-line strings
            while True:
                line = next(self._fp)
                assert line, "unterminated string"
                self.line_no += 1
                m: re.Match = regex.match(line)
                if not m:
                    out += line
                    continue
                g = m.group()
                # print("@@ multiline string cont", g)
                out += g
                if len(g) != len(line):
                    rest = line[len(g):]
                    self._tokens = re.findall(_RE_TOKENS_ALL, rest)
                    self._tokens.reverse()
                    break
        return out


def _MakeTypeBaseLambda(kind: cwast.BASE_TYPE_KIND):
    def closure(**extra):
        return cwast.TypeBase(kind, **extra)
    return closure


# maps "atoms" to the nodes they will be expanded to
_SHORT_HAND_NODES: dict[str, Callable] = {
    "auto": cwast.TypeAuto,
    #
    "auto_val": cwast.ValAuto,
    "void_val": cwast.ValVoid,
    "undef": cwast.ValUndef,
    "true": cwast.ValTrue,
    "false": cwast.ValFalse,
    # see cwast.OPTIONAL_FIELDS
    "break": lambda **args: cwast.StmtBreak(target=cwast.EMPTY_NAME, **args),
    "continue": lambda **args: cwast.StmtContinue(target=cwast.EMPTY_NAME, **args),
}

# add basic type names
for basic_type in cwast.BASE_TYPE_KIND:
    if basic_type != cwast.BASE_TYPE_KIND.INVALID:
        name = cwast.BaseTypeKindToKeyword(basic_type)
        _SHORT_HAND_NODES[name] = _MakeTypeBaseLambda(basic_type)


def ExpandShortHand(t: str, srcloc, attr: dict[str, Any]) -> Any:
    """Expands atoms, ids, and numbers to proper nodes"""
    x = _SHORT_HAND_NODES.get(t)
    if x is not None:
        node = x(x_srcloc=srcloc, **attr)
        return node

    if cwast.IsWellFormedStringLiteral(t):
        return cwast.ValString(t,  **attr)
    elif RE_TOKEN_NUM.fullmatch(t):
        logger.info("NUM %s at %s", t, srcloc)
        return cwast.ValNum(t, x_srcloc=srcloc, **attr)
    elif _RE_TOKEN_ID.fullmatch(t):
        # if t in cwast.NODES_ALIASES:
        #    cwast.CompilerError(srcloc, f"Reserved name used as ID: {t}")
        if t[0] == "$":
            return cwast.MacroId(cwast.NAME.Make(t), x_srcloc=srcloc)
        logger.info("ID %s at %s", t, srcloc)
        return cwast.Id.Make(t, x_srcloc=srcloc, **attr)
    elif len(t) >= 2 and t[0] == "'" and t[-1] == "'":
        logger.info("CHAR %s at %s", t, srcloc)
        return cwast.ValNum(t, x_srcloc=srcloc, **attr)
    else:
        cwast.CompilerError(srcloc, f"unexpected token {repr(t)}")


def ReadNodeList(stream: ReadTokens, parent_cls) -> list[Any]:
    out = []
    attr: dict[str, Any] = {}
    while True:
        token = ReadAttrs(next(stream), attr, stream)
        if token == "]":
            assert not attr
            break
        if token == "(":
            expr = ReadSExpr(stream, parent_cls, attr)
        else:
            expr = ExpandShortHand(token, stream.srcloc(), attr)
        attr.clear()
        # hack for simpler array val and rec val initializers: take the expr
        # from above and wrap it into a IndexVal or FieldVal
        if parent_cls is cwast.ValCompound and not isinstance(expr, cwast.ValPoint):
            expr = cwast.ValPoint(expr, cwast.ValUndef(
                x_srcloc=expr.x_srcloc), x_srcloc=expr.x_srcloc)
        out.append(expr)

    return out


def ReadNodeColonList(stream: ReadTokens, parent_cls):
    out = []
    attr: dict[str, Any] = {}
    while True:
        token = ReadAttrs(next(stream), attr, stream)
        if token == ")" or token == ":" or token == "[":
            # no attrib may occur afterwards
            if attr:
                cwast.CompilerError(
                    stream.srcloc(),
                    f"unexpected attribs in {parent_cls.__name__}: {attr.keys()}")
            stream.pushback(token)
            break

        if token == "(":
            expr = ReadSExpr(stream, parent_cls, attr)
        else:
            expr = ExpandShortHand(token, stream.srcloc(), attr)
        out.append(expr)
        attr.clear()

    return out


def ReadPiece(field, token, stream: ReadTokens, parent_cls) -> Any:
    """Read a single component of an SExpr including lists."""
    nfd = cwast. ALL_FIELDS_MAP[field]
    if nfd.kind is cwast.NFK.ATTR_BOOL:
        return bool(token)
    elif nfd.kind is cwast.NFK.STR:
        return token
    elif nfd.kind is cwast.NFK.NAME:
        return cwast.NAME.Make(token)

    elif nfd.kind is cwast.NFK.KIND:
        assert nfd.enum_kind is not None, f"{field} {token}"
        try:
            return nfd.enum_kind[token]
        except KeyError:
            cwast.CompilerError(
                stream.srcloc(), f"Cannot convert {token} for {field} in {parent_cls}")
    elif nfd.kind is cwast.NFK.NODE:
        attr: dict[str, Any] = {}
        token = ReadAttrs(token, attr, stream)
        if token == "(":
            return ReadSExpr(stream, parent_cls, attr)
        out = ExpandShortHand(token, stream.srcloc(), attr)
        if out is None:
            cwast.CompilerError(
                stream.srcloc(), f"Cannot expand {token} for {field}")
        return out

    elif nfd.kind is cwast.NFK.LIST:
        if token == "[":
            return ReadNodeList(stream, parent_cls)
        elif token == ":":
            return ReadNodeColonList(stream, parent_cls)
        else:
            cwast.CompilerError(stream.srcloc(),
                                f"expected list start in {parent_cls.__name__} for: {field} {token}")

    else:
        assert None, f"unexpected kind {nfd.kind} for field {field}"


def ReadMacroInvocation(tag: str, stream: ReadTokens, attr: dict[str, Any]):
    """The leading '(' and `tag` have already been consumed"""
    parent_cls = cwast.MacroInvoke
    srcloc = stream.srcloc()
    logger.info("Readdng MACRO INVOCATION %s at %s", tag, srcloc)
    args: list[Any] = []
    while True:
        token = next(stream)
        if token == ")":
            return cwast.MacroInvoke(cwast.NAME.Make(tag), args, x_srcloc=srcloc, **attr)
        sub_attr: dict[str, Any] = {}
        token = ReadAttrs(token, sub_attr, stream)
        if token == "(":
            args.append(ReadSExpr(stream, parent_cls, sub_attr))
        elif token == "[":
            assert not sub_attr
            args.append(cwast.EphemeralList(ReadNodeList(
                stream, parent_cls), colon=False, x_srcloc=srcloc))
        elif token == ":":
            assert not sub_attr
            args.append(cwast.EphemeralList(ReadNodeColonList(
                stream, parent_cls), colon=True, x_srcloc=srcloc))
        else:
            out = ExpandShortHand(token, stream.srcloc(), sub_attr)
            assert out is not None, f"while processing {
                tag} unexpected macro arg: {token}"
            args.append(out)
    return args


def ReadRestAndMakeNode(cls, pieces: list[Any], fields: list[cwast.NFD], attr: dict[str, Any], stream: ReadTokens):
    """Read the remaining componts of an SExpr (after the tag and attr).

    Can handle optional bools at the beginning and an optional 'tail'
    """
    srcloc = stream.srcloc()
    logger.info("Readding TAG %s at %s", cls.__name__, srcloc)
    token = next(stream)
    try:
        for nfd in fields:
            field = nfd.name
            if token == ")":
                # we have reached the end before all the fields were processed
                # fill in default values
                optional_val = cwast.GetOptional(field, srcloc)
                if optional_val is None:
                    cwast.CompilerError(
                        stream.srcloc(),
                        f"in {cls.__name__} unknown optional (or missing) field: {field}")
                pieces.append(optional_val)

            else:
                pieces.append(ReadPiece(field, token, stream, cls))
                token = next(stream)
    except StopIteration:
        cwast.CompilerError(stream.srcloc(
        ), f"while parsing {cls.__name__} file truncated")
    if token != ")":
        cwast.CompilerError(stream.srcloc(
        ), f"while parsing {cls.__name__} expected node-end but got {token}")
    return cls(*pieces, x_srcloc=srcloc, **attr)


def ReadSExpr(stream: ReadTokens, parent_cls, attr: dict[str, Any]) -> Any:
    """The leading '(' has already been consumed"""
    tag = ReadAttrs(next(stream), attr, stream)
    if len(tag) > 1 and tag.endswith(cwast.MUTABILITY_SUFFIX) and tag != "trylet!":
        tag = tag[:-1]
        attr["mut"] = True

    if tag in cwast.UNARY_EXPR_SHORTCUT_SEXPR:
        return ReadRestAndMakeNode(cwast.Expr1, [cwast.UNARY_EXPR_SHORTCUT_SEXPR[tag]],
                                   cwast.Expr1.FIELDS[1:], attr, stream)
    elif tag in cwast.BINARY_EXPR_SHORTCUT:
        return ReadRestAndMakeNode(cwast.Expr2, [cwast.BINARY_EXPR_SHORTCUT[tag]],
                                   cwast.Expr2.FIELDS[1:], attr, stream)
    elif tag in cwast.POINTER_EXPR_SHORTCUT:
        return ReadRestAndMakeNode(cwast.ExprPointer, [cwast.POINTER_EXPR_SHORTCUT[tag]],
                                   cwast.ExprPointer.FIELDS[1:], attr, stream)
    elif tag in cwast.ASSIGNMENT_SHORTCUT:
        return ReadRestAndMakeNode(cwast.StmtCompoundAssignment, [cwast.ASSIGNMENT_SHORTCUT[tag]],
                                   cwast.StmtCompoundAssignment.FIELDS[1:], attr, stream)
    else:
        cls = cwast.NODES_ALIASES.get(tag)
        if not cls:
            if tag in cwast.ALL_BUILT_IN_MACROS or tag.endswith(cwast.MACRO_CALL_SUFFIX):
                # unknown node name - assume it is a macro
                return ReadMacroInvocation(tag, stream, attr)
            else:
                cwast.CompilerError(stream.srcloc(), "Bad sexpr")

        assert cls is not None, f"[{stream.line_no}] Non node: {tag}"

        # This helps catching missing closing braces early
        if cwast.NF.TOP_LEVEL in cls.FLAGS:
            if parent_cls is None:
                cwast.CompilerError(
                    stream.srcloc(), f"toplevel node {cls.__name__} outside of module")
            if parent_cls is not cwast.DefMod:
                cwast.CompilerError(stream.srcloc(
                ), f"toplevel node {cls.__name__} not allowed in {parent_cls.__name__}")

        return ReadRestAndMakeNode(cls, [], cls.FIELDS, attr, stream)


def ReadModFromStream(fp, fn: str, name: str) -> cwast.DefMod:
    asts = []
    stream = ReadTokens(fp, fn)
    failure = False
    try:
        while True:
            attr: dict[str, Any] = {}
            t = ReadAttrs(next(stream), attr, stream)
            failure = True
            if t != "(":
                cwast.CompilerError(
                    stream.srcloc(), f"expect start of new node, got '{t}']")
            mod = ReadSExpr(stream, None, attr)
            if not isinstance(mod, cwast.DefMod):
                cwast.CompilerError(
                    stream.srcloc(), f"expected end of module but for {mod}")
            asts.append(mod)
            failure = False
    except StopIteration:
        assert not failure, "truncated file"
    assert len(asts) == 1
    asts[0].name = cwast.NAME.Make(name)
    return asts[0]


############################################################
#
############################################################
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    assert len(sys.argv) == 2
    with open(sys.argv[1], encoding="utf8") as f:
        ReadModFromStream(f, sys.argv[1], "main_mod")
