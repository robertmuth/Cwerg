#!/usr/bin/python3

"""
Translator from C to a hypothetical Three-Address-Code IR

This is not even close to being done and mostly a horrible
unprincipled hack.

EmitIR() is the main work-horse which traverse the AST recursively.

It usually does a post-order traversal where results from
the children are stored int the node_value map.
For some node types, however, we follow a pre-order approach.

"""
import operator
import re
import sys

from pycparser import c_ast, parse_file

import canonicalize
import common
import meta

RE_NUMBER = re.compile("^[-+]?[0-9]*[.]?[0-9]+([eE][-+]?[0-9]+)?$")

POINTER = ("*",)

TYPE_TRANSLATION_64 = {
    ("char",): "s8",
    ("char", "unsigned",): "u8",
    ("short",): "s16",
    ("short", "unsigned",): "u16",
    ("int",): "s32",
    ("int", "unsigned",): "u32",
    ("long",): "s64",
    ("long", "unsigned",): "u64",
    ("long", "long",): "s64",
    ("long", "long", "unsigned",): "u64",
    ("float",): "f32",
    ("double",): "f64",
    ("void",): None,
    POINTER: "a64",
}

TYPE_TRANSLATION_32 = {
    ("char",): "s8",
    ("char", "unsigned",): "u8",
    ("short",): "s16",
    ("short", "unsigned",): "u16",
    ("int",): "s32",
    ("int", "unsigned",): "u32",
    ("long",): "s32",
    ("long", "unsigned",): "u32",
    ("long", "long",): "s64",
    ("long", "long", "unsigned",): "u64",
    ("float",): "f32",
    ("double",): "f64",
    ("void",): None,
    POINTER: "a32",
}

TYPE_TRANSLATION = TYPE_TRANSLATION_64

tmp_counter = 0

ALL_BITS_SET = {
    "s8": -1,
    "s16": -1,
    "s32": -1,
    "s64": -1,
    "u8": (1 << 8) - 1,
    "u16": (1 << 16) - 1,
    "u32": (1 << 32) - 1,
    "u64": (1 << 64) - 1,
}


def IsNumber(s):
    return RE_NUMBER.match(s)


RE_NUMBER_SUFFIX = re.compile("(ull|ll|ul|l|u)$", re.IGNORECASE)

_NUMBER_TYPES = (int, float)


def StripNumberSuffix(s):
    m = RE_NUMBER_SUFFIX.search(s)
    if m:
        s = s[:m.start()]
    return s


def ExtractNumber(s):
    if s[0] == "'" and s[-1] == "'":
        assert len(s) == 3
        return ord(s[1])
    s = StripNumberSuffix(s)
    try:
        return int(s, 0)
    except ValueError:
        return float(s)


def align(x, a):
    return (x + a - 1) // a * a


def SizeOfAndAlignmentStruct(struct: c_ast.Struct, meta_info):
    if struct.decls is None:
        struct = meta_info.struct_links[struct]
    alignment = 1
    size = 0
    for f in struct.decls:
        s, a = SizeOfAndAlignment(f.type, meta_info)
        if a > alignment:
            alignment = a
        size = align(size, a) + s
        # print ("@@", s, a, size, alignment, f)

    return size, alignment


def GetStructOffset(struct: c_ast.Struct, field: c_ast.ID, meta_info):
    if struct.decls is None:
        struct = meta_info.struct_links[struct]
    offset = 0
    for f in struct.decls:
        if f.name == field.name:
            return offset
        s, a = SizeOfAndAlignment(f.type, meta_info)
        offset = align(offset, a) + s
    assert False, f"GetStructOffset unknown field {struct} {field}"


def SizeOfAndAlignmentUnion(node: c_ast.Union, meta_info):
    assert False, f"SizeOfAndAlignmentUnion {node}"


def SizeOfAndAlignment(node, meta_info):
    if isinstance(node, (c_ast.Typename, c_ast.Decl, c_ast.TypeDecl)):
        return SizeOfAndAlignment(node.type, meta_info)

    if isinstance(node, c_ast.Struct):
        return SizeOfAndAlignmentStruct(node, meta_info)
    elif isinstance(node, c_ast.Union):
        return SizeOfAndAlignmentUnion(node, meta_info)
    elif isinstance(node, c_ast.IdentifierType):
        type_name = TYPE_TRANSLATION[tuple(node.names)]
        bitsize = int(type_name[1:])
        return bitsize // 8, bitsize // 8
    elif isinstance(node, c_ast.ArrayDecl):
        size, align = SizeOfAndAlignment(node.type, meta_info)
        size = (size + align - 1) // align * align
        return size * int(node.dim.value), align
    elif isinstance(node, c_ast.PtrDecl):
        type_name = TYPE_TRANSLATION[POINTER]
        bitsize = int(type_name[1:])
        return bitsize // 8, bitsize // 8
    else:
        assert False, node


def IsGlobalDecl(node, parent):
    return isinstance(parent, c_ast.FileAST)


def IsLocalDecl(node, parent):
    return not isinstance(parent, (c_ast.FileAST, c_ast.ParamList, c_ast.FuncDef))


def ScalarDeclType(type):
    if isinstance(type, c_ast.TypeDecl):
        return ScalarDeclType(type.type)

    if isinstance(type, c_ast.ArrayDecl):
        return None
    elif isinstance(type, c_ast.PtrDecl):
        return TYPE_TRANSLATION[POINTER]
    elif isinstance(type, c_ast.IdentifierType):
        return TYPE_TRANSLATION[tuple(type.names)]
    elif isinstance(type, (c_ast.FuncDef, c_ast.Struct, c_ast.Union)):
        return None
    else:
        assert False, type


def GetVarKind(node, parent):
    if isinstance(parent, c_ast.ParamList):
        return "param"
    elif isinstance(parent, c_ast.FileAST):
        return "\nglobal"
    elif isinstance(parent, c_ast.FuncDef):
        return "result"
    else:
        return "local"


def StringifyType(type_or_decl):
    if isinstance(type_or_decl, (c_ast.Decl, c_ast.TypeDecl, c_ast.Typename)):
        return StringifyType(type_or_decl.type)

    if isinstance(type_or_decl, c_ast.FuncDecl):
        return "c32"
    elif isinstance(type_or_decl, c_ast.PtrDecl):
        return TYPE_TRANSLATION[POINTER]
    elif isinstance(type_or_decl, c_ast.ArrayDecl):
        return TYPE_TRANSLATION[POINTER]
    elif isinstance(type_or_decl, (c_ast.Struct, c_ast.Union)):
        return TYPE_TRANSLATION[POINTER]
    elif isinstance(type_or_decl, c_ast.IdentifierType):
        return TYPE_TRANSLATION[tuple(type_or_decl.names)]
    elif type(type_or_decl) == str:
        return type_or_decl
    else:
        assert False, type_or_decl
        # return str(type_or_decl)


def GetUnique():
    global tmp_counter
    tmp_counter += 1
    return tmp_counter


def GetTmp(type):
    assert type is not None
    return "%%%s_%s" % (StringifyType(type), GetUnique())


def HasNoResult(type):
    return isinstance(type, c_ast.IdentifierType) and type.names[0] == "void"


TAB = "  "


# x->b2->a1 = 0
#   Assignment: =
#     StructRef: .
#       UnaryOp: *
#         StructRef: .
#           UnaryOp: *
#             ID: x
#           ID: b2
#       ID: a1
#     Constant: int, 0

# xx.b1.c1.d1 = 0
# Assignment: =
#       StructRef: .
#         StructRef: .
#           StructRef: .
#             ID: xx
#             ID: b1
#           ID: c1
#         ID: d1
#       Constant: int, 0


def GetLValueAddress(lvalue, meta_info, node_value, id_gen):
    if isinstance(lvalue, c_ast.UnaryOp) and lvalue.op == "*":
        EmitIR([lvalue, lvalue.expr], meta_info, node_value, id_gen)
        node_value[lvalue] = node_value[lvalue.expr]
    elif isinstance(lvalue, c_ast.ArrayRef):
        assert False, lvalue
    elif isinstance(lvalue, c_ast.StructRef):
        struct = meta_info.type_links[lvalue.name]
        assert isinstance(struct, c_ast.Struct)

        # print ("@@", struct_def)
        EmitIR([lvalue, lvalue.name], meta_info, node_value, id_gen)

        offset = GetStructOffset(struct, lvalue.field, meta_info)
        if offset == 0:
            tmp = node_value[lvalue.name]
        else:
            kind = TYPE_TRANSLATION[POINTER]
            tmp = GetTmp(kind)
            print(
                f"{TAB}add {tmp}:{StringifyType(kind)} = {node_value[lvalue.name]} {offset}")
        node_value[lvalue] = tmp
    elif isinstance(lvalue, c_ast.ID):
        type = meta_info.type_links[lvalue]
        assert isinstance(type, (c_ast.PtrDecl, c_ast.Struct,
                                 c_ast.Union, c_ast.FuncDecl)), type
        if isinstance(type, (c_ast.Struct, c_ast.Union, c_ast.FuncDecl)):
            kind = TYPE_TRANSLATION[POINTER]
            tmp = GetTmp(kind)
            print(f"{TAB}lea {tmp}:{kind} = {lvalue.name}")
            node_value[lvalue] = tmp
        else:
            assert isinstance(type, c_ast.PtrDecl), type
            node_value[lvalue] = lvalue.name
    else:
        assert False, lvalue


def RenderList(items):
    return "[" + " ".join(items) + "]"


SPECIAL_FUNCTIONS = {
    "abort": "BUILTIN",
    "main": "MAIN",
    "malloc": "BUILTIN",
    "free": "BUILTIN",
    "memset": "BUILTIN",
    "memcpy": "BUILTIN",
    "print": "BUILTIN",
    "printf_u": "BUILTIN",
    "printf_d": "BUILTIN",
    "printf_f": "BUILTIN",
    "printf_c": "BUILTIN",
    "printf_s": "BUILTIN",
    "printf_p": "BUILTIN",
    "fopen": "BUILTIN",
    "fclose": "BUILTIN",
    "fseek": "BUILTIN",
    "ftell": "BUILTIN",
    "fread": "BUILTIN",
    "fwrite": "BUILTIN",
    "fputs": "BUILTIN",
    # "": "BUILTIN",
}


def EmitFunctionHeader(fun_name: str, fun_decl: c_ast.FuncDecl):
    return_type = StringifyType(fun_decl.type)
    params = fun_decl.args.params if fun_decl.args else []
    ins = []
    for p in params:
        ins += [StringifyType(p)]
    outs = [return_type] if return_type else []

    kind = SPECIAL_FUNCTIONS.get(fun_name, "NORMAL")
    print(f"\n\n.fun {fun_name} {kind} {RenderList(outs)} = {RenderList(ins)}")


def HandleAssignment(node: c_ast.Assignment, meta_info, node_value, id_gen):
    assert node.op == "=", node
    lvalue = node.lvalue
    EmitIR([node, node.rvalue], meta_info, node_value, id_gen)
    tmp = node_value[node.rvalue]
    # because of the canonicalization step only register promotable scalars will
    # naked like this
    if isinstance(lvalue, c_ast.ID):
        # but if address is taken
        print(f"{TAB}mov {lvalue.name} = {tmp}")
    else:
        GetLValueAddress(lvalue, meta_info, node_value, id_gen)
        if isinstance(tmp, _NUMBER_TYPES):
            kind = meta_info.type_links[node.rvalue]
            tmp2 = GetTmp(kind)
            print(f"{TAB}mov {tmp2}:{StringifyType(kind)} = {tmp}")
            tmp = tmp2
        print(f"{TAB}st {node_value[lvalue]} 0 = {tmp}")
    node_value[node] = tmp


# hack - just good enough to handle nanojpeg.c
def EmitInitData(init: c_ast.InitList, type_decl):
    assert isinstance(init, c_ast.InitList)
    values = []
    for v in init.exprs:
        assert isinstance(v, c_ast.Constant)
        assert v.type == "int"
        values.append(str(ExtractNumber(v.value)))
    assert isinstance(type_decl, c_ast.ArrayDecl)
    scalar = ScalarDeclType(type_decl.type)
    assert scalar in {"s8", "u8"}
    dim = ExtractNumber(type_decl.dim.value)
    assert dim == len(values)

    print(f'.data 1 [{" ".join(values)}]')


def HandleDecl(node_stack, meta_info, node_value, id_gen):
    decl: c_ast.Decl = node_stack[-1]
    parent = node_stack[-2]
    name = decl.name

    if IsGlobalDecl(decl, parent):
        size, align = SizeOfAndAlignment(decl, meta_info)
        assert name is not None
        print(f"\n.mem {name} {align} RW")
        if decl.init:
            EmitInitData(decl.init, decl.type)

        else:
            print(f".data {size} [0]")

    elif IsLocalDecl(decl, parent):
        # we also need to take into account if the address is taken later
        scalar = ScalarDeclType(decl.type)
        if scalar:
            print(f"{TAB}.reg [{name}] {scalar}")

            if decl.init:
                EmitIR(node_stack + [decl.init], meta_info, node_value, id_gen)
                print(f"{TAB}mov {name} = {node_value[decl.init]}")

        else:
            size, alignment = SizeOfAndAlignment(decl, meta_info)
            print(f".stk {name} {alignment} {size}")
            if decl.init:
                assert False, "stack with initialized data"
                # print("INIT-STACK", decl.init)

    else:
        assert False, decl


def HandleStructRef(node: c_ast.StructRef, parent, meta_info, node_value, id_gen):
    assert node.type == "."
    EmitIR([parent, node, node.name], meta_info, node_value, id_gen)
    kind = TYPE_TRANSLATION[POINTER]
    tmp = GetTmp(kind)
    struct = meta_info.type_links[node.name]
    assert isinstance(struct, c_ast.Struct)
    offset = GetStructOffset(struct, node.field, meta_info)
    print(f"{TAB}add {tmp}:{kind} = {node_value[node.name]} {offset}")
    if isinstance(parent, c_ast.StructRef):
        node_value[node] = tmp
    elif isinstance(parent, c_ast.UnaryOp) and parent.op == "&":
        node_value[node] = tmp
    elif isinstance(meta_info.type_links[node.field], c_ast.ArrayDecl):
        node_value[node] = tmp
    else:
        # print ("@@@@@", meta_info.type_links[node.field])
        field_type = meta_info.type_links[node.field]
        val_type = ScalarDeclType(field_type)
        val = GetTmp(val_type)
        print(f"{TAB}ld {val}:{val_type} = {tmp} 0")
        node_value[node] = val


def HandleFuncCall(node: c_ast.FuncCall, meta_info, node_value):
    # print ("ARGS", node.args)
    if HasNoResult(meta_info.type_links[node]):
        results = []
        node_value[node] = None
    else:
        kind = meta_info.type_links[node]
        tmp = GetTmp(kind)
        results = [f"{tmp}:{StringifyType(kind)}"]
        node_value[node] = tmp
    params = []
    if node.args:
        for a in node.args:
            p = node_value[a]
            kind = meta_info.type_links[a]
            if isinstance(p, _NUMBER_TYPES):
                tmp = GetTmp(kind)
                if isinstance(kind, c_ast.PtrDecl):
                    assert p == 0
                    print(f"{TAB}lea {tmp}:{StringifyType(kind)} = %nullptr")

                else:
                    print(f"{TAB}mov {tmp}:{StringifyType(kind)} = {p}")
                p = tmp
            params.append(p)
        for p in reversed(params):
            print(f"{TAB}pusharg {p}")
    print(f"{TAB}bsr {node_value[node.name]}")
    for p in results:
        print(f"{TAB}poparg {p}")


def HandleSwitch(node: c_ast.Switch, meta_info, node_value, id_gen):
    EmitIR([node, node.cond], meta_info, node_value, id_gen)
    label = "switch_%d_" % GetUnique()
    label_tab = label + "tab"
    label_end = label + "end"
    label_default = label + "default"
    cases = []
    default = None
    max_val = 0
    for s in node.stmt:
        if isinstance(s, c_ast.Case):
            val = ExtractNumber(s.expr.value)
            assert val >= 0
            if max_val < val:
                max_val = val
            block = label + str(val).replace("-", "minus")
            cases.append((val, s.stmts, block))
        else:
            assert isinstance(s, c_ast.Default), s
            cases.append((None, s.stmts, label_default))
            default = s

    lst = [f"{a} {c}" for a, b, c in cases if a is not None]
    dl = label_default if default else label_end
    switch_value = node_value[node.cond]
    print(f"{TAB}bgt {dl} {switch_value} {max_val}")
    print(f"{TAB}.jtb {label_tab} {dl} [{' '.join(lst)}] {max_val + 1}")
    print(f"{TAB}switch {label_tab} {switch_value}")
    for a, b, c in cases:
        print(f".bbl {c}")
        for s in b:
            if isinstance(s, c_ast.Break):
                print(f"{TAB}bra {label_end}")
            else:
                EmitIR([node, node.stmt, s], meta_info, node_value, id_gen)
    print(f"\n.bbl {label_end}")


MAP_COMPARE = {
    "!=": "bne",
    "==": "beq",
    "<": "blt",
    "<=": "ble",
    ">": "bgt",
    ">=": "bge"
}

MAP_COMPARE_EVAL = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.ge,
    ">=": operator.gt,
}


def EmitConditionalBranch(op: str, target: str, left, right):
    if isinstance(left, _NUMBER_TYPES) and isinstance(right, _NUMBER_TYPES):
        # partial evaluation
        if MAP_COMPARE_EVAL[op](left, right):
            print(f"{TAB}{bra} {target}")
        return
    print(f"{TAB}{MAP_COMPARE[op]} {target} {left} {right}")


def IsScalarType(type):
    if isinstance(type, c_ast.TypeDecl):
        return IsScalarType(type.type)

    return isinstance(type, c_ast.IdentifierType)


def EmitID(parent, node: c_ast.ID, meta_info: meta.MetaInfo, node_value):
    if isinstance(parent, c_ast.StructRef):
        assert parent.field != node
    type_info = meta_info.type_links[node]
    if isinstance(type_info, c_ast.IdentifierType):
        node_value[node] = node.name
        return
    elif isinstance(type_info, c_ast.Struct):
        if parent.field == node:
            node_value[node] = node.name
            return
    elif isinstance(type_info, c_ast.FuncDecl):
        node_value[node] = node.name
        return
    elif not isinstance(type_info, c_ast.ArrayDecl):
        node_value[node] = node.name
        return
    elif isinstance(type_info, c_ast.ArrayDecl):
        if type_info.dim is None:
            node_value[node] = node.name
            return

    kind = TYPE_TRANSLATION[POINTER]
    tmp = GetTmp(kind)
    print(f"{TAB}lea {tmp}:{kind} = {node.name}")
    node_value[node] = tmp


BIN_OP_MAP = {
    "*": "mul",
    "+": "add",
    "-": "sub",
    "/": "div",
    "%": "mod",
    "<<": "shl",
    ">>": "shr",
    "^": "xor",
    "|": "or",
    "&": "and",
}


def HandleBinop(node: c_ast.BinaryOp, meta_info: meta.MetaInfo, node_value, id_gen: common.UniqueId):
    node_kind = meta_info.type_links[node]
    assert node.op in BIN_OP_MAP, node.op
    left = node_value[node.left]
    right = node_value[node.right]
    if isinstance(left, _NUMBER_TYPES) and isinstance(right, _NUMBER_TYPES):
        # TODO: revisit this - partial eval is delicate
        if node.op == "*":
            node_value[node] = left * right
        elif node.op == "-":
            node_value[node] = left - right
        elif node.op == "+":
            node_value[node] = left + right
        elif node.op == "<<":
            node_value[node] = left << right
        elif node.op == "/":  # does not work for floats
            node_value[node] = left // right
        else:
            assert False, node
        return

    op = BIN_OP_MAP[node.op]
    if isinstance(node_kind, (c_ast.PtrDecl, c_ast.ArrayDecl)):
        # need to scale
        assert node.op == "+" or node.op == "-"
        element_size, _ = SizeOfAndAlignment(node_kind.type, meta_info)
        if element_size == 1:
            pass
        elif isinstance(right, _NUMBER_TYPES):
            right = str(right * element_size)
        else:
            right_kind = meta_info.type_links[node.right]
            tmp = GetTmp(right_kind)
            print(
                f"{TAB}mul {tmp}:{StringifyType(right_kind)} = {right} {element_size}")
            right = tmp
    tmp = GetTmp(node_kind)
    print(f"{TAB}{op} {tmp}:{StringifyType(node_kind)} = {left} {right}")
    node_value[node] = tmp


def EmitIR(node_stack, meta_info: meta.MetaInfo, node_value, id_gen: common.UniqueId):
    node = node_stack[-1]
    if isinstance(node, c_ast.FuncDef):
        fun_decl = node.decl.type
        EmitFunctionHeader(node.decl.name, fun_decl)
        return_type = StringifyType(fun_decl.type)
        if return_type:
            print(f".reg [%out] {return_type}")
        params = fun_decl.args.params if fun_decl.args else []
        # for p in params:
        #    print(f".reg [{p.name}] {StringifyType(p)}")
        print(f"\n.bbl %start")
        for p in params:
            print(f"{TAB}poparg {p.name}:{StringifyType(p)}")
        EmitIR(node_stack + [node.body], meta_info, node_value, id_gen)
        return
    elif isinstance(node, c_ast.Decl) and isinstance(node.type, c_ast.FuncDecl):
        EmitFunctionHeader(node.name, node.type)
        return
    elif isinstance(node, c_ast.Decl):
        if node.name is not None:
            HandleDecl(node_stack, meta_info, node_value, id_gen)
        return
    elif isinstance(node, c_ast.If):
        cond = node.cond
        if isinstance(cond, c_ast.BinaryOp) and cond.op in common.COMPARISON_INVERSE_MAP:
            EmitIR(node_stack + [cond.left], meta_info, node_value, id_gen)
            EmitIR(node_stack + [cond.right], meta_info, node_value, id_gen)
            EmitConditionalBranch(cond.op, node.iftrue.name,
                                  node_value[cond.left], node_value[cond.right])
            print(f"{TAB}bra {node.iffalse.name}")
        else:
            EmitIR(node_stack + [cond], meta_info, node_value, id_gen)
            print(
                f"{TAB}brcond {node_value[cond]} {node.iftrue.name} {node.iffalse.name}")
            assert False
        return
    elif isinstance(node, c_ast.Label):
        print(f"\n.bbl {node.name}")
        EmitIR(node_stack + [node.stmt], meta_info, node_value, id_gen)
        return
    elif isinstance(node, c_ast.Assignment):
        HandleAssignment(node, meta_info, node_value, id_gen)
        return
    elif isinstance(node, c_ast.Struct):
        return
    elif isinstance(node, c_ast.UnaryOp) and node.op == "&":
        GetLValueAddress(node.expr, meta_info, node_value, id_gen)
        node_value[node] = node_value[node.expr]
        return
    elif isinstance(node, c_ast.Switch):
        HandleSwitch(node, meta_info, node_value, id_gen)
        return
    elif isinstance(node, c_ast.StructRef):
        HandleStructRef(node, node_stack[-2], meta_info, node_value, id_gen)
        return

    for c in node:
        node_stack.append(c)
        EmitIR(node_stack, meta_info, node_value, id_gen)
        node_stack.pop(-1)

    if isinstance(node, c_ast.ID):
        EmitID(node_stack[-2], node, meta_info, node_value)
    elif isinstance(node, c_ast.Constant):
        if meta_info.type_links[node] is meta.STRING_IDENTIFIER_TYPE:
            name = id_gen.next("string_const")
            print(f".mem {name} 4 RO")
            print(".data", "1", node.value[:-1] + '\\x00"')
            kind = TYPE_TRANSLATION[POINTER]
            tmp = GetTmp(kind)
            print(f"{TAB}lea {tmp}:{kind} = {name}")
            node_value[node] = tmp
            node_value[node] = tmp
        else:
            node_value[node] = ExtractNumber(node.value)
    elif isinstance(node, c_ast.IdentifierType):
        pass
    elif isinstance(node, c_ast.Goto):
        print(f"{TAB}bra {node.name}")
    elif isinstance(node, c_ast.BinaryOp):
        HandleBinop(node, meta_info, node_value, id_gen)
    elif isinstance(node, c_ast.UnaryOp):
        assert node.op != "&"  # this is handled further up
        if node.op == "sizeof":
            expr = node.expr
            expr = meta_info.type_links.get(expr, expr)
            tmp, _ = SizeOfAndAlignment(expr, meta_info)
        elif node.op == "*":
            if isinstance(node_stack[-2], c_ast.StructRef):
                tmp = node_value[node.expr]
            else:
                kind = meta_info.type_links[node]
                tmp = GetTmp(kind)
                print(
                    f"{TAB}ld {tmp}:{StringifyType(kind)} = {node_value[node.expr]} 0")
                node_value[node] = tmp
        elif node.op == "~":
            kind = meta_info.type_links[node]
            tmp = GetTmp(kind)
            x = ALL_BITS_SET[StringifyType(kind)]
            print(
                f"{TAB}xor {tmp}:{StringifyType(kind)} = {node_value[node.expr]} {x}")
            node_value[node] = tmp
        elif node.op == "-":
            kind = meta_info.type_links[node]
            tmp = GetTmp(kind)
            print(
                f"{TAB}rsub {tmp}:{StringifyType(kind)} = {node_value[node.expr]} 0")
            node_value[node] = tmp
        else:
            assert False, node
            # tmp = GetTmp(meta_info.type_links[node])
            # print(TAB, tmp, "=", node.op, node_value[node.expr])
        node_value[node] = tmp
    elif isinstance(node, c_ast.Cast):
        dst_kind = StringifyType(meta_info.type_links[node])
        src_kind = StringifyType(meta_info.type_links[node.expr])
        if src_kind == dst_kind:
            node_value[node] = node_value[node.expr]
            return

        if isinstance(node_value[node.expr], _NUMBER_TYPES):
            if node_value[node.expr] >= 0:
                # non-negative numbers, especially zero are compatible with most things
                node_value[node] = node_value[node.expr]
            else:
                tmp = GetTmp(meta_info.type_links[node.expr])
                print(f"{TAB}mov.i {tmp}:{src_kind} = {node_value[node.expr]}")
                # needs more work especially for narrowing
                tmp2 = GetTmp(meta_info.type_links[node])
                assert dst_kind is not None
                print(f"{TAB}conv {tmp2}:{dst_kind} = {tmp}")
                node_value[node] = tmp2
        else:
            tmp = GetTmp(meta_info.type_links[node])
            assert dst_kind is not None

            print(f"{TAB}conv {tmp}:{dst_kind} = {node_value[node.expr]}")
            node_value[node] = tmp
    elif isinstance(node, c_ast.FuncCall):
        HandleFuncCall(node, meta_info, node_value)
    elif isinstance(node, c_ast.Return):
        if node.expr:
            print(f"{TAB}mov %out = {node_value[node.expr]}")
            print(f"{TAB}pusharg %out")
        print(f"{TAB}ret")
    elif isinstance(node, c_ast.EmptyStatement):
        pass
    elif isinstance(node, c_ast.ExprList):
        node_value[node] = node_value[node.exprs[-1]]
    elif isinstance(node, (c_ast.TypeDecl, c_ast.PtrDecl, c_ast.ArrayDecl, c_ast.FuncDecl, c_ast.Typename)):
        pass
    elif isinstance(node, (c_ast.EllipsisParam, c_ast.ParamList, c_ast.Compound, c_ast.FuncDef, c_ast.FileAST)):
        pass
    else:
        assert False, node


def main(argv):
    for filename in argv:
        print("#" * 60)
        print("#", filename)
        print("#" * 60)
        print(".mem %nullptr 0 FIX")
        ast = parse_file(filename, use_cpp=True)
        canonicalize.SimpleCanonicalize(ast, use_specialized_printf=True)
        meta_info = meta.MetaInfo(ast)
        canonicalize.Canonicalize(ast, meta_info, skip_constant_casts=False)
        global_id_gen = common.UniqueId()
        EmitIR([ast], meta_info, {}, global_id_gen)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
