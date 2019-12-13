#!/usr/bin/python3

"""
Translator from C to a hypothetical Three-Address-Code IR

This is not even close to being done
"""

import sys

from pycparser import c_ast, parse_file

import canonicalize
import common
import meta

TYPE_TRANSLATION = {
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
    ("void",): None
}


tmp_counter = 0


def SizeOf(node):
    assert isinstance(node, c_ast.Typename), node
    if isinstance(node.type, c_ast.TypeDecl):
        type_name = TYPE_TRANSLATION[tuple(node.type.type.names)]
        bitsize = int(type_name[1:])
        return bitsize // 8
    else:
        assert False, node


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
    if isinstance(type_or_decl, c_ast.Typename):
        return StringifyType(type_or_decl.type)
    elif isinstance(type_or_decl, c_ast.FuncDecl):
        return "c32"
    elif isinstance(type_or_decl, c_ast.PtrDecl):
        return "a32"
    elif isinstance(type_or_decl, c_ast.ArrayDecl):
        return "a32"
    elif isinstance(type_or_decl, c_ast.TypeDecl):
        return StringifyType(type_or_decl.type)
    elif isinstance(type_or_decl, c_ast.Decl):
        return StringifyType(type_or_decl.type)
    elif isinstance(type_or_decl, c_ast.IdentifierType):
        return TYPE_TRANSLATION[tuple(type_or_decl.names)]
    elif type(type_or_decl) == str:
        return type_or_decl
    else:
        assert False, type_or_decl
        return str(type_or_decl)


def GetTmp(type):
    global tmp_counter
    tmp_counter += 1
    return "%%%s_%s" % (StringifyType(type), tmp_counter)


def HasNoResult(type):
    return isinstance(type, c_ast.IdentifierType) and type.names[0] == "void"


TAB = "  "


def RenderItemList(items):
    return "[" + " ".join(items) + "]"


def EmitFunctionHeader(fun_name: str, fun_decl: c_ast.FuncDecl):
    return_type = StringifyType(fun_decl.type)
    params = fun_decl.args.params if fun_decl.args else []
    parameter_types = [StringifyType(p) for p in params]
    parameter_names = [p.name for p in params]
    print("")
    print(".sig", "%sig_" + fun_name, "[" + (return_type if return_type else "") + "]", "=",
          RenderItemList(parameter_types))
    print(".fun", fun_name, "%sig_" + fun_name, "[%out]" if return_type else "[]", "=",
          RenderItemList(parameter_names))


def HandleStore(node: c_ast.Assignment, meta_info, node_value, id_gen):
    lvalue = node.lvalue
    EmitIR([node, node.rvalue], meta_info, node_value, id_gen)
    tmp = node_value[node.rvalue]
    if isinstance(lvalue, c_ast.UnaryOp) and lvalue.op == "*":
        EmitIR([node, lvalue.expr], meta_info, node_value, id_gen)
        print (TAB, "store", node_value[lvalue.expr], "=", tmp)
    else:
        EmitIR([node, lvalue], meta_info, node_value, id_gen)
        print (TAB, node_value[lvalue], "=", tmp)
    node_value[node] = tmp



def EmitIR(node_stack, meta_info, node_value, id_gen: common.UniqueId):
    node = node_stack[-1]
    if isinstance(node, c_ast.FuncDef):
        EmitFunctionHeader(node.decl.name, node.decl.type)
        print("@%start")
        EmitIR(node_stack + [node.body], meta_info, node_value, id_gen)
        return
    if isinstance(node, c_ast.Decl) and isinstance(node.type, c_ast.FuncDecl):
        EmitFunctionHeader(node.name, node.type)
        return

    if isinstance(node, c_ast.If):
        cond = node.cond
        if isinstance(cond, c_ast.BinaryOp) and cond.op in common.COMPARISON_INVERSE_MAP:
            EmitIR(node_stack + [cond.left], meta_info, node_value, id_gen)
            EmitIR(node_stack + [cond.right], meta_info, node_value, id_gen)
            print(TAB, "brcond", node_value[cond.left], cond.op, node_value[cond.right], node.iftrue.name,
                  node.iffalse.name)
        else:
            EmitIR(node_stack + [cond], meta_info, node_value, id_gen)
            print(TAB, "brcond", node_value[cond], node.iftrue.name, node.iffalse.name)
        return
    elif isinstance(node, c_ast.Label):
        print("@" + node.name)
        EmitIR(node_stack + [node.stmt], meta_info, node_value, id_gen)
        return
    elif isinstance(node, c_ast.Assignment):
        HandleStore(node, meta_info, node_value, id_gen)
        return

    for c in node:
        node_stack.append(c)
        EmitIR(node_stack, meta_info, node_value, id_gen)
        node_stack.pop(-1)

    if isinstance(node, c_ast.ID):
        node_value[node] = node.name
    elif isinstance(node, c_ast.Constant):
        if meta_info.type_links[node] is meta.STRING_IDENTIFIER_TYPE:
            name = id_gen.next("string_const")
            print(".mem", name, "4", "ro")
            print(".data", "1", node.value)
            print(".data", "1", "[0]")
            tmp = GetTmp("a32")
            print(TAB, tmp, "=", name)
            node_value[node] = tmp
        elif isinstance(node_stack[-2], c_ast.ExprList):
            tmp = GetTmp(meta_info.type_links[node])
            print(TAB, tmp, "=", node.value)
            node_value[node] = tmp
        else:
            node_value[node] = node.value
    elif isinstance(node, c_ast.IdentifierType):
        pass
    elif isinstance(node, c_ast.Goto):
        print(TAB, "br", node.name)
    elif isinstance(node, c_ast.Decl):
        parent = node_stack[-2]
        kind = GetVarKind(node, parent)
        type_str = StringifyType(node.type)
        print(kind, node.name, type_str)
    elif isinstance(node, c_ast.BinaryOp):
        tmp = GetTmp(meta_info.type_links[node])
        print(TAB, tmp, "=", node_value[node.left], node.op, node_value[node.right])
        node_value[node] = tmp
    elif isinstance(node, c_ast.UnaryOp):
        if node.op == "sizeof":
            val = SizeOf(node.expr)
            if isinstance(node_stack[-2], c_ast.ExprList):
                tmp = GetTmp(meta_info.type_links[node])
                print(TAB, tmp, "=", val)
            else:
                tmp = val
        elif node.op == "*":
            tmp = GetTmp(meta_info.type_links[node])
            print (TAB, "load", tmp, "=", node_value[node.expr])
            node_value[node] = tmp
        else:
            tmp = GetTmp(meta_info.type_links[node])
            print(TAB, tmp, "=", node.op, node_value[node.expr])
        node_value[node] = tmp
    elif isinstance(node, c_ast.Cast):
        tmp = GetTmp(meta_info.type_links[node])
        print(TAB, tmp, "=", "(cast)", node_value[node.expr])
        node_value[node] = tmp
    elif isinstance(node, c_ast.FuncCall):
        #print ("ARGS", node.args)
        if HasNoResult(meta_info.type_links[node]):
            results = []
            node_value[node] = None
        else:
            tmp = GetTmp(meta_info.type_links[node])
            results = [tmp]
            node_value[node] = tmp
        params = []
        if node.args:
            params = [node_value[a] for a in node.args]
        print(TAB, "call", node_value[node.name], RenderItemList(results), "=", RenderItemList(params))
    elif isinstance(node, c_ast.Return):
        if node.expr:
            print(TAB, "%out", "=", node_value[node.expr])
        print(TAB, "ret")
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
    filename = argv[0]
    ast = parse_file(filename, use_cpp=True)
    meta_info = meta.MetaInfo(ast)
    canonicalize.Canonicalize(ast, meta_info, True, True)
    global_id_gen = common.UniqueId()
    EmitIR([ast], meta_info, {}, global_id_gen)
    # generator = c_generator.CGenerator()
    # print(generator.visit(ast))


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
