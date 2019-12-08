from typing import List, Tuple

from pycparser import c_ast

EXPRESSION_NODES = (c_ast.ArrayRef,
                    c_ast.Assignment,
                    c_ast.BinaryOp,
                    c_ast.Cast,
                    c_ast.Constant,
                    c_ast.ExprList,
                    c_ast.FuncCall,
                    c_ast.ID,
                    c_ast.Return,
                    c_ast.StructRef,
                    c_ast.TernaryOp,
                    c_ast.UnaryOp)

NEW_SCOPE_NODE = (c_ast.Compound,
                  c_ast.For,
                  c_ast.While,
                  c_ast.DoWhile,
                  c_ast.FuncDef)

POST_INC_DEC_OPS = {
    "p--",
    "p++",
}

PRE_INC_DEC_OPS = {
    "++",
    "--",
}

SAME_TYPE_UNARY_OPS = {
    "++",
    "--",
    "p--",
    "p++",
    "-",
    "~",
}

BOOL_INT_TYPE_UNARY_OPS = {
    "!",
}

SAME_TYPE_BINARY_OPS = {
    "+",
    "-",
    "^",
    "*",
    "/",
    "|",
    "&",
    "%",
    "<<",
    ">>",
}

# Note: this would be bool in C++
BOOL_INT_TYPE_BINARY_OPS = {
    "==",
    "!=",
    "<=",
    "<",
    ">=",
    ">",
    "&&",
    "||",
}

COMPARISON_INVERSE_MAP = {
    "==": "!=",
    "!=": "==",
    "<=": ">",
    "<": ">=",
    ">=": "<",
    ">": "<=",
}

SHORT_CIRCUIT_OPS = {
    "&&",
    "||",
}

OPS_REQUIRING_BOOL_INT = {
    "&&",
    "||",
    "!",  # unary
}

# Map a canonicalized base type to a `level` and a canonical IdentifierType.
# The `level` encodes C's implicit conversion rules:
# if two values are inputs to a BinaryOp the must be implicitly converted to
# the type with the larger level.
# Note that the standard dictates: signed x unsigned -> unsigned
# (citation needed)
CANONICAL_BASE_TYPE = {
    ("char",): (1, c_ast.IdentifierType(["char"])),
    ("char", "unsigned",): (2, c_ast.IdentifierType(["char", "unsigned"])),
    ("short",): (3, c_ast.IdentifierType(["short"])),
    ("short", "unsigned",): (4, c_ast.IdentifierType(["short", "unsigned"])),
    ("int",): (5, c_ast.IdentifierType(["int"])),
    ("int", "unsigned",): (6, c_ast.IdentifierType(["int", "unsigned"])),
    ("long",): (7, c_ast.IdentifierType(["long"])),
    ("long", "unsigned",): (8, c_ast.IdentifierType(["long", "unsigned"])),
    ("long", "long",): (9, c_ast.IdentifierType(["long", "long"])),
    ("long", "long", "unsigned",): (10, c_ast.IdentifierType(["long", "long", "unsigned"])),
    ("float",): (11, c_ast.IdentifierType(["float"])),
    ("double",): (12, c_ast.IdentifierType(["double"])),
    # unrelated
    ("string",): (-1, c_ast.IdentifierType(["string"])),
    ("void",): (-1, c_ast.IdentifierType(["void"])),
}

ALLOWED_IDENTIFIER_TYPES = {t[1] for t in CANONICAL_BASE_TYPE.values()}

_CANONICAL_IDENTIFIER_TYPE_MAP = {
    ("char", "signed"): ("char",),
    ("short", "signed"): ("short",),
    ("int", "signed"): ("int",),
    ("long", "signed"): ("long",),
    ("int", "short"): ("short",),
    ("int", "long"): ("long",),
    ("signed",): ("int",),
    ("unsigned",): ("int", "unsigned"),
}


def CanonicalizeIdentifierType(names: List[str]):
    """Return a sorted and simplified string tuple"""
    n = sorted(names)
    if len(names) <= 2:
        x = _CANONICAL_IDENTIFIER_TYPE_MAP.get(tuple(n))
        return x if x else tuple(n)
    if "int" in n:
        n.remove("int")
    if "signed" in n:
        n.remove("signed")
    return tuple(n)


def GetCanonicalIdentifierType(names):
    return CANONICAL_BASE_TYPE[CanonicalizeIdentifierType(names)][1]


def TypeCompare(t1: c_ast.IdentifierType, t2: c_ast.IdentifierType):
    i1 = CANONICAL_BASE_TYPE[tuple(t1.names)][0]
    i2 = CANONICAL_BASE_TYPE[tuple(t2.names)][0]
    if i1 == i2:
        return "="
    elif i1 < i2:
        return "<"
    else:
        return ">"


def MaxType(t1, t2):
    if isinstance(t1, c_ast.PtrDecl) and isinstance(t2, c_ast.PtrDecl):
        # maybe do some more checks
        return t1

    assert isinstance(t1, c_ast.IdentifierType) and isinstance(t2, c_ast.IdentifierType)
    cmp = TypeCompare(t1, t2)
    if cmp == "=" or cmp == ">":
        return t1
    else:
        return t2


def NodePrettyPrint(node: c_ast):
    if node is None:
        return "none"
    elif isinstance(node, c_ast.ID):
        return "id[%s]" % node.name
    elif isinstance(node, c_ast.BinaryOp):
        return "op[%s]" % node.op
    elif isinstance(node, c_ast.UnaryOp):
        return "op[%s]" % node.op
    else:
        return node.__class__.__name__


def IsZeroConstant(node):
    if not isinstance(node, c_ast.Constant): return False
    # TODO: also support other int types
    if node.type != "int": return False
    return 0 == int(node.value)


def IsEmpty(node):
    return (node is None or isinstance(node, c_ast.EmptyStatement) or
            isinstance(node, c_ast.Compound) and len(node.block_items) == 0)


def ReplaceNode(parent, old_node, new_node):
    # TODO: add nodes as needed
    if isinstance(parent, c_ast.ExprList):
        for n, e in enumerate(parent.exprs):
            if e is old_node:
                parent.exprs[n] = new_node
                break
        else:
            assert False, parent
    elif isinstance(parent, c_ast.Compound):
        for n, e in enumerate(parent.block_items):
            if e is old_node:
                parent.block_items[n] = new_node
                break
        else:
            assert False, parent
    elif isinstance(parent, c_ast.For):
        if parent.next is old_node:
            parent.next = new_node
        elif parent.stmt is old_node:
            parent.stmt = new_node
        elif parent.cond is old_node:
            parent.cond = new_node
        elif parent.init is old_node:
            parent.init = new_node
        else:
            assert False, parent
    elif isinstance(parent, c_ast.If):
        if parent.cond is old_node:
            parent.cond = new_node
        elif parent.iftrue is old_node:
            parent.iftrue = new_node
        elif parent.iffalse is old_node:
            parent.iffalse = new_node
        else:
            assert False, parent
    elif isinstance(parent, c_ast.BinaryOp):
        if parent.left is old_node:
            parent.left = new_node
        elif parent.right is old_node:
            parent.right = new_node
        else:
            assert False, parent
    elif isinstance(parent, c_ast.Assignment):
        if parent.lvalue is old_node:
            parent.lvalue = new_node
        elif parent.rvalue is old_node:
            parent.rvalue = new_node
        else:
            assert False, parent
    elif isinstance(parent, c_ast.Cast):
        if parent.expr is old_node:
            parent.expr = new_node
        else:
            assert False, parent
    elif isinstance(parent, c_ast.Return):
        if parent.expr is old_node:
            parent.expr = new_node
        else:
            assert False, parent
    elif isinstance(parent, c_ast.Label):
        if parent.stmt is old_node:
            parent.stmt = new_node
        else:
            assert False, parent
    elif isinstance(parent, c_ast.ArrayRef):
        if parent.name is old_node:
            parent.name = new_node
        elif parent.subscript is old_node:
            parent.subscript = new_node
        else:
            assert False, parent
    else:
        assert False, parent
    return new_node


def ReplaceBreakAndContinue(node, parent, test_label, exit_label):
    """ Starting at `node` recursively replace
    all `continue` statements with `goto test_label` and
    all `break` statements with `goto exit_label`
    """
    if isinstance(node, c_ast.Continue):
        ReplaceNode(parent, node, c_ast.Goto(test_label))
        return
    if exit_label and isinstance(node, c_ast.Break):
        ReplaceNode(parent, node, c_ast.Goto(exit_label))
        return

    if isinstance(node, (c_ast.While, c_ast.DoWhile, c_ast.For)):
        # do not recurse into other loops
        return

    if isinstance(node, c_ast.Switch):
        # `break`s inside switches have their own meaning but we still need to replace `continue`s
        exit_label = None

    for c in node:
        ReplaceBreakAndContinue(c, node, test_label, exit_label)


def GetStatementList(node: c_ast.Node):
    if isinstance(node, (c_ast.Default, c_ast.Case)):
        return node.stmts
    elif isinstance(node, c_ast.Compound):
        return node.block_items
    elif isinstance(node, (c_ast.Case, c_ast.Default)):
        return node.stmts
    else:
        return None


def FindMatchingNodesPostOrder(node: c_ast.Node, parent: c_ast.Node, matcher):
    res: List[Tuple[c_ast.Node, c_ast.Node]] = []
    for c in node:
        res += FindMatchingNodesPostOrder(c, node, matcher)
    if matcher(node, parent):
        res.append((node, parent))
    return res


def FindMatchingNodesPreOrder(node: c_ast.Node, parent: c_ast.Node, matcher):
    res: List[Tuple[c_ast.Node, c_ast.Node]] = []
    if matcher(node, parent):
        res.append((node, parent))
    for c in node:
        res += FindMatchingNodesPreOrder(c, node, matcher)

    return res


class UniqueId:
    def __init__(self):
        self.n = 0

    def next(self, prefix):
        self.n += 1
        return "%s_%s" % (prefix, self.n)
