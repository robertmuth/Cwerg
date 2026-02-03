"""Translator from AST to Cwerg IR"""

import logging
import dataclasses
import enum
import math

from typing import Union, Any, Optional

from Util.parse import BytesToEscapedString

from FE import symbolize
from FE import type_corpus
from FE import cwast
from FE import eval
from FE import identifier

from IR import opcode_tab as o

logger = logging.getLogger(__name__)

TAB = "  "

ZEROS = [b"\0" * i for i in range(128)]


_DUMMY_VOID_REG = "@DUMMY_FOR_VOID_RESULTS@"


def _IterateValVec(points: list[cwast.ValPoint], dim, srcloc):
    """Pairs given ValPoints from a ValCompound repesenting a Vec with their indices"""
    curr_index = 0
    for init in points:
        if isinstance(init.point_or_undef, cwast.ValUndef):
            yield init
            curr_index += 1
            continue
        index = init.point_or_undef.x_eval.val
        assert isinstance(index, int)
        while curr_index < index:
            yield None
            curr_index += 1
        yield init
        curr_index += 1
    if curr_index > dim:
        cwast.CompilerError(
            srcloc, f"Out of bounds array access at {curr_index}. Array size is  {dim}")
    while curr_index < dim:
        yield None
        curr_index += 1


@enum.unique
class STORAGE_KIND(enum.Enum):
    """Macro Parameter Kinds"""
    INVALID = enum.auto()
    REGISTER = enum.auto()
    STACK = enum.auto()
    DATA = enum.auto()


def _IsDefVarOnStack(node: cwast.DefVar) -> bool:
    if node.ref:
        return True
    return node.x_type.ir_regs == o.DK.MEM


def _StorageKindForId(node: cwast.Id) -> STORAGE_KIND:
    def_node = node.x_symbol
    if isinstance(def_node, cwast.DefGlobal):
        return STORAGE_KIND.DATA
    elif isinstance(def_node, cwast.FunParam):
        return STORAGE_KIND.REGISTER
    elif isinstance(def_node, cwast.DefFun):
        return STORAGE_KIND.REGISTER
    elif isinstance(def_node, cwast.DefVar):
        return STORAGE_KIND.STACK if _IsDefVarOnStack(def_node) else STORAGE_KIND.REGISTER
    else:
        assert False, f"Unexpected ID {def_node}"


def _FunMachineTypes(ct: cwast.CanonType) -> tuple[list[str], list[str]]:
    assert ct.is_fun()
    res_types: list[str] = []
    if ct.result_type().ir_regs != o.DK.NONE:
        res_types.append(str(ct.result_type().ir_regs))
    arg_types: list[str] = []
    for p in ct.parameter_types():
        assert p.ir_regs not in (o.DK.NONE, o.DK.MEM)
        arg_types.append(str(p.ir_regs))

    return res_types, arg_types


def MakeFunSigName(ct: cwast.CanonType) -> str:
    res_types, arg_types = _FunMachineTypes(ct)
    if not res_types:
        res_types.append("void")
    if not arg_types:
        arg_types = ["void"]
    assert len(res_types) == 1
    return f"$sig/{res_types[0]}_{'_'.join(arg_types)}"


def _EmitFunctionProlog(fun: cwast.DefFun,
                        id_gen: identifier.IdGenIR):
    print(f".bbl {id_gen.NewName('entry')}")
    for p in fun.params:
        # TODO: NewName returns a str but p.name is really a NAME
        # this uniquifies names
        # Name translation!
        p.name = id_gen.NewName(str(p.name))
        print(f"{TAB}poparg {p.name}:{p.x_type.get_single_register_type()}")


ZERO_INDEX = "0"


@dataclasses.dataclass()
class BaseOffset:
    """Represents and address as pair of base and offset"""
    base: str
    offset_num: int = 0

    def AddScaledOffsetExpr(self, offset_expr, scale: int, ta: type_corpus.TargetArchConfig, id_gen) -> "BaseOffset":
        if offset_expr.x_eval is not None:
            return BaseOffset(self.base, offset_expr.x_eval.val * scale)
        offset = _EmitExpr(offset_expr, ta, id_gen)
        if scale != 1:
            scaled = id_gen.NewName("scaled")
            print(
                f"{TAB}conv {scaled}:{ta.get_sint_reg_type()} = {offset}")
            print(
                f"{TAB}mul {scaled} = {scaled} {scale}")
            offset = scaled
        new_base = id_gen.NewName("new_base")
        print(
            f"{TAB}lea {new_base}:{ta.get_data_address_reg_type()} = {self.base} {offset}")
        return BaseOffset(new_base, self.offset_num)

    def AddOffset(self, offset) -> "BaseOffset":
        return BaseOffset(self.base, self.offset_num + offset)

    def MaterializeBase(self, ta, id_gen) -> str:
        if self.offset_num == 0:
            return self.base

        res = id_gen.NewName("at")
        print(
            f"{TAB}lea {res}:{ta.get_data_address_reg_type()} = {self.base} {self.offset_num}")
        return res


@dataclasses.dataclass()
class ReturnResultLocation:
    """Where to store a return expression

    if type is str, the result must fit into a register whose name is provide.
    Otherwise the result is to be copied into the memory location provided.
    """
    dst: Union[str, BaseOffset]
    end_label: str


_STORAGE_TO_MEM_SUFFIX = {
    STORAGE_KIND.DATA: "mem",
    STORAGE_KIND.STACK: "stk",
}


def _GetLValueAddress(node, ta: type_corpus.TargetArchConfig,
                      id_gen: identifier.IdGenIR) -> BaseOffset:
    if isinstance(node, cwast.ExprDeref):
        return BaseOffset(_EmitExpr(node.expr, ta, id_gen))
    elif isinstance(node, cwast.ExprField):
        bo = _GetLValueAddress(node.container, ta, id_gen)
        return bo.AddOffset(node.field.GetRecFieldRef().x_offset)
    elif isinstance(node, cwast.Id):
        name = node.x_symbol.name
        base = id_gen.NewName("lhsaddr")
        kind = ta.get_data_address_reg_type()
        storage = _StorageKindForId(node)
        print(
            f"{TAB}lea.{_STORAGE_TO_MEM_SUFFIX[storage]} {base}:{kind} = {name} 0")
        return BaseOffset(base)
    elif isinstance(node, cwast.ExprNarrow):
        #
        assert node.expr.x_type.is_untagged_union()
        return _GetLValueAddress(node.expr, ta, id_gen)
    elif isinstance(node, cwast.ExprStmt):
        # Only a few expressions can generate l-values or objects whose
        # address can be taken, basically ExprCall and ExprStmt
        # That latter often occurs after inlining functions.
        # We rewrite function signatures with complex result types
        # so that space for the result is allocated at the call site.
        # So here we only have to deal with StmtExpr
        ct = node.x_type
        assert ct.ir_regs is o.DK.MEM
        name = id_gen.NewName("expr_stk_var")
        assert ct.size > 0
        print(f"{TAB}.stk {name} {ct.alignment} {ct.size}")
        base = id_gen.NewName("stmt_stk_base")
        kind = ta.get_data_address_reg_type()
        print(f"{TAB}lea.stk {base}:{kind} {name} 0")
        EmitExprToMemory(node,  BaseOffset(base), ta, id_gen)
        return BaseOffset(base)
    else:
        assert False, f"unsupported node for lvalue {node} at {node.x_srcloc}"


_MAP_COMPARE = {
    cwast.BINARY_EXPR_KIND.NE: "bne",
    cwast.BINARY_EXPR_KIND.EQ: "beq",
    cwast.BINARY_EXPR_KIND.LT: "blt",
    cwast.BINARY_EXPR_KIND.LE: "ble",
}

_MAP_COMPARE_INVERT = {
    cwast.BINARY_EXPR_KIND.NE: cwast.BINARY_EXPR_KIND.EQ,
    cwast.BINARY_EXPR_KIND.EQ:  cwast.BINARY_EXPR_KIND.NE,
    cwast.BINARY_EXPR_KIND.LT: cwast.BINARY_EXPR_KIND.GE,
    cwast.BINARY_EXPR_KIND.LE: cwast.BINARY_EXPR_KIND.GT,
    cwast.BINARY_EXPR_KIND.GT:  cwast.BINARY_EXPR_KIND.LE,
    cwast.BINARY_EXPR_KIND.GE:  cwast.BINARY_EXPR_KIND.LT,
}


def _GetBranchOpcode(kind: cwast.BINARY_EXPR_KIND, invert: bool) -> tuple[str, bool]:
    swap = False
    if invert:
        kind = _MAP_COMPARE_INVERT[kind]
    # reduce comparison to what can be easily tranalate IR

    if kind is cwast.BINARY_EXPR_KIND.GT:
        kind = cwast.BINARY_EXPR_KIND.LT
        swap = True
    elif kind is cwast.BINARY_EXPR_KIND.GE:
        kind = cwast.BINARY_EXPR_KIND.LE
        swap = True
    return _MAP_COMPARE[kind], swap


def _ChangesControlFlow(node):
    return isinstance(node, (cwast.StmtBreak, cwast.StmtContinue, cwast.StmtReturn))


def _EmitId(node, id_gen: identifier.IdGenIR) -> str:
    if node.x_type.size == 0:
        # TODO: This is a bit hackish
        return "@@@@@ BAD, DO NOT USE @@@@@@ "
    def_node = node.x_symbol
    if isinstance(def_node, cwast.DefGlobal):
        res = id_gen.NewName("globread")
        print(
            f"{TAB}ld.mem {res}:{node.x_type.get_single_register_type()} = {def_node.name} 0")
        return res
    elif isinstance(def_node, cwast.FunParam):
        return str(def_node.name)
    elif isinstance(def_node, cwast.DefFun):
        res = id_gen.NewName("funaddr")
        print(
            f"{TAB}lea.fun {res}:{node.x_type.get_single_register_type()} = {def_node.name}")
        return res
    elif isinstance(def_node, cwast.DefVar):
        if _IsDefVarOnStack(def_node):
            res = id_gen.NewName("stkread")
            print(
                f"{TAB}ld.stk {res}:{node.x_type.get_single_register_type()} = {def_node.name} 0")
            return res
        else:
            return str(def_node.name)
    else:
        assert False, f"Unexpected ID {def_node}"


def _EmitConditionalExpr2(cond, invert: bool, label_f: str, ta: type_corpus.TargetArchConfig,
                          id_gen: identifier.IdGenIR):
    kind: cwast.BINARY_EXPR_KIND = cond.binary_expr_kind
    if kind is cwast.BINARY_EXPR_KIND.ANDSC:
        if invert:
            _EmitConditional(cond.expr1, True, label_f, ta, id_gen)
            _EmitConditional(cond.expr2, True, label_f, ta, id_gen)
        else:
            failed = id_gen.NewName("br_failed_and")
            _EmitConditional(cond.expr1, True, failed, ta, id_gen)
            _EmitConditional(cond.expr2, False, label_f, ta, id_gen)
            print(f".bbl {failed}")
    elif kind is cwast.BINARY_EXPR_KIND.ORSC:
        if invert:
            failed = id_gen.NewName("br_failed_or")
            _EmitConditional(cond.expr1, False, failed, ta, id_gen)
            _EmitConditional(cond.expr2, True, label_f, ta, id_gen)
            print(f".bbl {failed}")
        else:
            _EmitConditional(cond.expr1, False, label_f, ta, id_gen)
            _EmitConditional(cond.expr2, False, label_f, ta, id_gen)
    elif kind in (cwast.BINARY_EXPR_KIND.AND, cwast.BINARY_EXPR_KIND.OR,
                  cwast.BINARY_EXPR_KIND.XOR):
        op = _EmitExpr(cond, ta, id_gen)
        branch = "beq" if invert else "bne"
        print(f"{TAB}{branch} {op} 0 {label_f}")
    else:
        assert cond.expr1.x_type.ir_regs not in (
            o.DK.MEM, o.DK.NONE), f"NYI Expr2 for {cond} {cond.expr1.x_type}"
        op1 = _EmitExpr(cond.expr1, ta, id_gen)
        op2 = _EmitExpr(cond.expr2, ta, id_gen)
        branch, swap = _GetBranchOpcode(kind, invert)
        if swap:
            op1, op2 = op2, op1
        print(
            f"{TAB}{branch} {op1} {op2} {label_f}")


def _EmitConditional(cond, invert: bool, label_false: str, ta: type_corpus.TargetArchConfig,
                     id_gen: identifier.IdGenIR):
    """The emitted code assumes that the not taken label immediately succceeds the code generated here"""
    assert cond.x_type.is_bool()
    if cond.x_eval is not None:
        # TODO: we probably should check for side effects, though it seems hard to imagine how
        #       we can partially eval in the presence of side-effects
        if cond.x_eval.val != invert:
            print(f"{TAB}bra {label_false}")
    elif isinstance(cond, cwast.Expr1):
        assert cond.unary_expr_kind is cwast.UNARY_EXPR_KIND.NOT
        _EmitConditional(cond.expr, not invert, label_false, ta, id_gen)
    elif isinstance(cond, cwast.Expr2):
        _EmitConditionalExpr2(cond, invert, label_false, ta, id_gen)
    elif isinstance(cond, (cwast.ExprCall, cwast.ExprStmt, cwast.ExprField, cwast.ExprDeref)):
        op = _EmitExpr(cond, ta, id_gen)
        branch = "beq" if invert else "bne"
        print(f"{TAB}{branch} {op} 0 {label_false}")
    elif isinstance(cond, cwast.Id):
        op = _EmitId(cond, id_gen)
        branch = "beq" if invert else "bne"
        print(f"{TAB}{branch} {op} 0 {label_false}")
    else:
        assert False, f"unexpected expression {cond}"


_BIN_OP_MAP = {
    cwast.BINARY_EXPR_KIND.MUL: "mul",
    cwast.BINARY_EXPR_KIND.ADD: "add",
    cwast.BINARY_EXPR_KIND.SUB: "sub",
    cwast.BINARY_EXPR_KIND.DIV: "div",
    cwast.BINARY_EXPR_KIND.MOD: "rem",
    cwast.BINARY_EXPR_KIND.SHL: "shl",
    cwast.BINARY_EXPR_KIND.SHR: "shr",
    cwast.BINARY_EXPR_KIND.XOR: "xor",
    cwast.BINARY_EXPR_KIND.OR: "or",
    cwast.BINARY_EXPR_KIND.AND: "and",
}


def _EmitExpr2(node: cwast.Expr2, res, op1, op2, id_gen: identifier.IdGenIR):
    kind = node.binary_expr_kind
    ct = node.x_type
    res_type = ct.get_single_register_type()
    op = _BIN_OP_MAP.get(kind)
    if op is not None:
        print(f"{TAB}{op} {res}:{res_type} = {op1} {op2}")
    elif kind is cwast.BINARY_EXPR_KIND.PDELTA:
        conv_op1 = id_gen.NewName("pdelta1")
        conv_op2 = id_gen.NewName("pdelta2")
        print(f"{TAB}bitcast {conv_op1}:{res_type} = {op1}")
        print(f"{TAB}bitcast {conv_op2}:{res_type} = {op2}")

        print(f"{TAB}sub {res}:{res_type} = {conv_op1} {conv_op2}")
        print(f"{TAB}div {res} = {res} {
              node.expr1.x_type.underlying_type().aligned_size()}")
    elif kind is cwast.BINARY_EXPR_KIND.MAX:
        print(
            f"{TAB}cmplt {res}:{res_type} = {op1} {op2} {op2} {op1}")
    elif kind is cwast.BINARY_EXPR_KIND.MIN:
        print(
            f"{TAB}cmplt {res}:{res_type} = {op1} {op2} {op1} {op2}")
    else:
        assert False, f"unsupported expression {kind}"


def _EmitExpr1(node, ta: type_corpus.TargetArchConfig, id_gen: identifier.IdGenIR):
    ct = node.x_type
    kind = node.unary_expr_kind
    op = _EmitExpr(node.expr, ta, id_gen)
    res = id_gen.NewName("expr1")
    res_type = ct.get_single_register_type()
    if kind is cwast.UNARY_EXPR_KIND.NEG:
        print(f"{TAB}sub {res}:{res_type} = 0 {op}")
    elif kind is cwast.UNARY_EXPR_KIND.NOT:
        ff: int = (1 << (8 * node.x_type.base_type_kind.ByteSize())) - 1
        print(f"{TAB}xor {res}:{res_type} = 0x{ff:x} {op}")
    elif kind is cwast.UNARY_EXPR_KIND.ABS:
        # TODO: special case unsigned
        print(f"{TAB}sub {res}:{res_type} = 0 {op}")
        print(f"{TAB}cmplt {res} = {res} {op} {op} {0}")
    elif kind is cwast.UNARY_EXPR_KIND.SQRT:
        # TODO: check float type
        print(f"{TAB}sqrt {res}:{res_type} = {op}")
    else:
        assert False, f"unsupported expression {kind}"
    return res


def _FormatNumber(val: cwast.ValNum) -> str:
    suffix = ":" + str(val.x_type.get_single_register_type())
    assert isinstance(val.x_eval, eval.EvalNum)
    bt = val.x_type.get_unwrapped_base_type_kind()
    assert bt == val.x_eval.kind, f"{val.x_eval} {bt} {val.x_eval.kind}"
    num = val.x_eval.val
    assert num is not None, f"{val.x_eval}"

    if bt is cwast.BASE_TYPE_KIND.BOOL:
        return "1" + suffix if num else "0" + suffix
    elif bt.IsInt():
        return str(num) + suffix
    elif bt.IsReal():
        if math.isnan(num) or math.isinf(num):
            # note, python renders -nan and +nan as just nan
            sign = math.copysign(1, num)
            num = abs(num)
            return ("+" if sign >= 0 else "-") + str(num) + suffix
        return str(num) + suffix
    else:
        assert False, f"unsupported scalar: {bt} {val}"


def _EmitCast(expr, src_ct, dst_ct, id_gen: identifier.IdGenIR) -> str:
    assert dst_ct.size > 0
    src_reg_type = src_ct.get_single_register_type()
    dst_reg_type = dst_ct.get_single_register_type()
    if src_reg_type == dst_reg_type:
        return expr
    res = id_gen.NewName("bitcast")
    print(f"{TAB}bitcast {res}:{dst_reg_type} = {expr}")
    return res


_OP_DO_NOT_USE = "@DO_NOT_USE@"


def _EmitExprCall(node, ta: type_corpus.TargetArchConfig, id_gen: identifier.IdGenIR) -> Any:
    callee = node.callee
    fun_ct: cwast.CanonType = callee.x_type
    assert fun_ct.is_fun()
    arg_ops = [_EmitExpr(a, ta, id_gen) for a in node.args]
    for a in reversed(arg_ops):
        print(f"{TAB}pusharg {a}")
    if isinstance(callee, cwast.Id) and isinstance(callee.x_symbol, cwast.DefFun):
        print(f"{TAB}bsr {callee.x_symbol.name}")
    else:
        op = _EmitExpr(callee, ta, id_gen)
        print(f"{TAB}jsr {op} {MakeFunSigName(fun_ct)}")

    res_ct = fun_ct.result_type()
    if res_ct.size == 0:
        return _OP_DO_NOT_USE

    res = id_gen.NewName("call")
    print(f"{TAB}poparg {res}:{res_ct.get_single_register_type()}")
    return res


def _EmitExpr(node, ta: type_corpus.TargetArchConfig, id_gen: identifier.IdGenIR) -> Any:
    """Returns None if the type is void"""
    ct_dst: cwast.CanonType = node.x_type
    ir_reg = ct_dst.ir_regs
    assert ir_reg != o.DK.MEM, f"{node} ct={ct_dst}"
    if isinstance(node, cwast.ExprCall):
        return _EmitExprCall(node, ta, id_gen)
    elif isinstance(node, cwast.ValNum):
        return _FormatNumber(node)
    elif isinstance(node, cwast.Id):
        return _EmitId(node, id_gen)
    elif isinstance(node, cwast.ExprAddrOf):
        return _GetLValueAddress(node.expr_lhs, ta, id_gen).MaterializeBase(ta, id_gen)
    elif isinstance(node, cwast.Expr1):
        return _EmitExpr1(node, ta, id_gen)
    elif isinstance(node, cwast.Expr2):
        op1 = _EmitExpr(node.expr1, ta, id_gen)
        op2 = _EmitExpr(node.expr2, ta, id_gen)
        res = id_gen.NewName("expr2")
        _EmitExpr2(node, res, op1, op2, id_gen)
        return res
    elif isinstance(node, cwast.ExprPointer):
        base = BaseOffset(_EmitExpr(node.expr1, ta, id_gen))
        # TODO: add range check
        # assert isinstance(node.expr_bound_or_undef, cwast.ValUndef)
        ct: cwast.CanonType = node.expr1.x_type
        if node.pointer_expr_kind is cwast.POINTER_EXPR_KIND.INCP:
            base = base.AddScaledOffsetExpr(
                node.expr2, ct.underlying_type().aligned_size(), ta, id_gen)
            return base.MaterializeBase(ta, id_gen)
        else:
            assert False, f"unsupported expression {node}"
    elif isinstance(node, cwast.ExprBitCast):
        expr = _EmitExpr(node.expr, ta, id_gen)
        return _EmitCast(expr, node.expr.x_type, node.type.x_type, id_gen)
    elif isinstance(node, cwast.ExprNarrow):
        addr = _GetLValueAddress(
            node.expr, ta, id_gen).MaterializeBase(ta, id_gen)
        if ct_dst.size == 0:
            return _OP_DO_NOT_USE
        ct_src: cwast.CanonType = node.expr.x_type
        assert ct_src.is_union() or ct_src.original_type.is_union()
        res = id_gen.NewName("union_access")
        print(
            f"{TAB}ld {res}:{ct_dst.get_single_register_type()} = {addr} 0")
        return res
    elif isinstance(node, cwast.ExprAs):
        ct_src: cwast.CanonType = node.expr.x_type
        if ct_src.is_base_type() and ct_dst.is_base_type():
            # more compatibility checking needed
            expr = _EmitExpr(node.expr, ta, id_gen)
            res = id_gen.NewName("as")
            print(
                f"{TAB}conv {res}:{ct_dst.get_single_register_type()} = {expr}")
            return res
        elif ct_src.is_pointer() and ct_dst.is_pointer():
            return _EmitExpr(node.expr, ta, id_gen)
        else:
            assert False, f"unsupported cast {
                node.expr} ({ct_src.name}) -> {ct_dst.name}"
    elif isinstance(node, (cwast.ExprWrap, cwast.ExprUnwrap)):
        return _EmitExpr(node.expr, ta, id_gen)
    elif isinstance(node, cwast.ExprDeref):
        addr = _EmitExpr(node.expr, ta, id_gen)
        res = id_gen.NewName("deref")
        print(
            f"{TAB}ld {res}:{node.x_type.get_single_register_type()} = {addr} 0")
        return res
    elif isinstance(node, cwast.ExprStmt):
        if node.x_type.size == 0:
            result = _DUMMY_VOID_REG
        else:
            result = id_gen.NewName("expr")
            print(
                f"{TAB}.reg {node.x_type.get_single_register_type()} [{result}]")
        end_label = id_gen.NewName("end_expr")
        for c in node.body:
            _EmitStmt(c, ReturnResultLocation(result, end_label), ta, id_gen)
        print(f".bbl {end_label}")
        return result
    elif isinstance(node, cwast.ExprFront):
        assert node.container.x_type.is_vec(), f"unexpected {node}"
        return _GetLValueAddress(node.container, ta, id_gen).MaterializeBase(ta, id_gen)
    elif isinstance(node, cwast.ExprField):
        recfield: cwast.RecField = node.field.GetRecFieldRef()
        res = id_gen.NewName(recfield.name.name)
        addr = _GetLValueAddress(
            node.container, ta, id_gen).MaterializeBase(ta, id_gen)
        if node.x_type.size == 0:
            return _OP_DO_NOT_USE
        print(
            f"{TAB}ld {res}:{node.x_type.get_single_register_type()} = {addr} {recfield.x_offset}")
        return res
    elif isinstance(node, cwast.ExprWiden):
        # this should only happen for widening empty untagged unions
        # assert node.x_type.size == 0, f"{node} {node.x_type}"
        # make sure we evaluate the rest for side-effects
        tmp = _EmitExpr(node.expr, ta, id_gen)
        dst_ct = node.type.x_type
        if dst_ct.size == 0:
            return _OP_DO_NOT_USE
        if node.expr.x_type.size == 0:
            assert tmp is _OP_DO_NOT_USE, f"{tmp} {node.expr}"
            # TODO: does this work for all types?
            return "0"
        return _EmitCast(tmp, node.expr.x_type, dst_ct, id_gen)
    elif isinstance(node, cwast.ValVoid):
        return _OP_DO_NOT_USE
    # elif isinstance(node, cwast.ValCompound):
    #    assert node.x_type.size == 0, f"{node} {node.x_type} {node.x_type.size}"
    #    return None
    else:
        assert False, f"unsupported expression {node.x_srcloc} {node} {node.x_type.ir_regs}"


def _EmitZero(dst: BaseOffset, length, alignment,
              _id_gen: identifier.IdGenIR):
    width = alignment  # TODO: may be capped at 4 for 32bit platforms
    curr = 0
    while curr < length:
        while width > (length - curr):
            width //= 2
        while curr + width <= length:
            print(f"{TAB}st {dst.base} {dst.offset_num + curr} = 0:U{width * 8}")
            curr += width


def EmitExprToMemory(init_node, dst: BaseOffset,
                     ta: type_corpus.TargetArchConfig,
                     id_gen: identifier.IdGenIR):
    """This will instantiate objects on the stack or heap.

    Note, that this can occur in two ways:
    1) we populate the object from the information AST
    2) we copy the contents from a global const location
       (this works in conjunction with the GlobalConstantPool)
    """
    assert init_node.x_type.size > 0, f"{init_node}"
    if isinstance(init_node, (cwast.ExprCall, cwast.ValNum, cwast.ExprAddrOf,
                              cwast.Expr1, cwast.Expr2, cwast.ExprPointer, cwast.ExprFront)):
        reg = _EmitExpr(init_node, ta, id_gen)
        print(f"{TAB}st {dst.base} {dst.offset_num} = {reg}")
    elif isinstance(init_node, cwast.ExprBitCast):
        # both imply scalar and both do not change the bits
        reg = _EmitExpr(init_node.expr, ta, id_gen)
        print(f"{TAB}st {dst.base} {dst.offset_num} = {reg}")
    elif isinstance(init_node, (cwast.ExprWrap, cwast.ExprUnwrap)):
        # these do NOT imply scalars
        EmitExprToMemory(init_node.expr, dst, ta, id_gen)
    elif isinstance(init_node, cwast.ExprAs):
        # this implies scalar
        # TODO: add the actual conversion step using IR opcode `conv`
        #       bools may need special treatment
        assert init_node.x_type == init_node.type.x_type, f"ExprAs {
            init_node.type.x_type} ->  {init_node.x_type}"
        assert init_node.x_type.ir_regs not in (o.DK.MEM, o.DK.NONE
                                                ), f"{init_node} {init_node.x_type}"
        reg = _EmitExpr(init_node, ta, id_gen)
        print(f"{TAB}st {dst.base} {dst.offset_num} = {reg}")
    elif isinstance(init_node, cwast.ExprNarrow):
        # if we are narrowing the dst determines the size
        ct: cwast.CanonType = init_node.x_type
        if ct.size != 0:
            src_base = _GetLValueAddress(
                init_node.expr, ta, id_gen)
            _EmitCopy(dst, src_base, ct.size, ct.alignment, id_gen)
    elif isinstance(init_node, cwast.ExprWiden):
        assert init_node.x_type.is_untagged_union()
        ct: cwast.CanonType = init_node.expr.x_type
        if ct.size != 0:
            EmitExprToMemory(init_node.expr, dst, ta, id_gen)
    elif isinstance(init_node, cwast.Id) and _StorageKindForId(init_node) is STORAGE_KIND.REGISTER:
        reg = _EmitId(init_node, id_gen)
        print(f"{TAB}st {dst.base} {dst.offset_num} = {reg}")
    elif isinstance(init_node, (cwast.Id, cwast.ExprDeref, cwast.ExprField)):
        src_base = _GetLValueAddress(init_node, ta, id_gen)
        src_type = init_node.x_type
        # if isinstance(init_node,  cwast.ExprField):
        #    print ("@@@@@@", init_node, src_type)
        _EmitCopy(dst, src_base, src_type.size, src_type.alignment, id_gen)
    elif isinstance(init_node, cwast.ExprStmt):
        end_label = id_gen.NewName("end_expr")
        for c in init_node.body:
            _EmitStmt(c, ReturnResultLocation(dst, end_label), ta, id_gen)
        print(f".bbl {end_label}")
    elif isinstance(init_node, cwast.ValString):
        assert False, f"NYI {init_node}"
    elif isinstance(init_node, cwast.ValAuto):
        # TODO: check if auto is legit (maybe add a check for this in another phase)
        _EmitZero(dst, init_node.x_type.size,
                  init_node.x_type.alignment, id_gen)
    elif isinstance(init_node, cwast.ValCompound):
        src_type = init_node.x_type
        if src_type.is_rec():
            if not init_node.inits:
                _EmitZero(dst, src_type.size, src_type.alignment, id_gen)
                return
            for field, init in symbolize.IterateValRec(init_node.inits, src_type):
                if init is None:
                    _EmitZero(BaseOffset(dst.base, dst.offset_num+field.x_offset),
                              field.x_type.size, field.x_type.alignment, id_gen)
                elif isinstance(init.value_or_undef, cwast.ValUndef):
                    pass
                elif init.value_or_undef.x_type.size == 0:
                    pass
                else:
                    EmitExprToMemory(init.value_or_undef, BaseOffset(
                        dst.base, dst.offset_num+field.x_offset), ta, id_gen)
        else:
            assert src_type.is_vec()
            element_size: int = src_type.array_element_size()
            for index, c in enumerate(_IterateValVec(init_node.inits,
                                                     init_node.x_type.array_dim(),
                                                     init_node.x_srcloc)):
                if c is None:
                    continue
                if isinstance(c.value_or_undef, cwast.ValUndef):
                    continue
                EmitExprToMemory(
                    c.value_or_undef, BaseOffset(dst.base, dst.offset_num + element_size * index), ta, id_gen)
    else:
        assert False, f"NYI: {init_node}"


def _EmitCopy(dst: BaseOffset, src: BaseOffset, length, alignment,
              id_gen: identifier.IdGenIR):
    width = alignment  # TODO: may be capped at 4 for 32bit platforms
    curr = 0
    while curr < length:
        while width > (length - curr):
            width //= 2
        tmp = id_gen.NewName(f"copy{width}")
        print(f"{TAB}.reg U{width*8} [{tmp}]")
        while curr + width <= length:
            print(f"{TAB}ld {tmp} = {src.base} {src.offset_num + curr}")
            print(f"{TAB}st {dst.base} {dst.offset_num + curr} = {tmp}")
            curr += width


def _EmitStmt(node, result: Optional[ReturnResultLocation], ta: type_corpus.TargetArchConfig,
              id_gen: identifier.IdGenIR):
    if isinstance(node, cwast.DefVar):
        # name translation!
        node.name = id_gen.NewName(str(node.name))

        ct: cwast.CanonType = node.x_type
        init = node.initial_or_undef_or_auto
        if ct.size == 0:
            if not isinstance(init, cwast.ValUndef):
                # still need to evaluate the expression for the side effect
                _EmitExpr(init, ta, id_gen)
        elif _IsDefVarOnStack(node):
            assert ct.size > 0
            print(f"{TAB}.stk {node.name} {
                  ct.alignment} {ct.size}")
            if not isinstance(init, cwast.ValUndef):
                base = id_gen.NewName("var_stk_base")
                print(
                    f"{TAB}lea.stk {base}:{ta.get_data_address_reg_type()} {node.name} 0")
                EmitExprToMemory(init, BaseOffset(base), ta, id_gen)
        elif isinstance(init, cwast.ValUndef):
            print(
                f"{TAB}.reg {ct.get_single_register_type()} [{node.name}]")
        else:
            out = _EmitExpr(init, ta, id_gen)
            assert out is not None, f"Failure to gen code for {init}"
            print(
                f"{TAB}mov {node.name}:{ct.get_single_register_type()} = {out}")
    elif isinstance(node, cwast.StmtBlock):
        label = str(node.label)
        if not label:
            label = "_"

        node.label = id_gen.NewName(label)

        print(f".bbl {node.label}")
        for c in node.body:
            _EmitStmt(c, result, ta, id_gen)
        print(f".bbl {node.label}.end")
    elif isinstance(node, cwast.StmtReturn):
        if isinstance(node.x_target, cwast.ExprStmt):
            assert result is not None

            # for this kind of return we need to save the computed value
            # and the branch to the end of the ExprStmt
            if node.expr_ret.x_type.size != 0:
                if isinstance(result.dst, str):
                    out = _EmitExpr(node.expr_ret, ta, id_gen)
                    print(f"{TAB}mov {result.dst} {out}")
                else:
                    EmitExprToMemory(node.expr_ret, result.dst, ta, id_gen)
            else:
                # nothing to save here
                _EmitExpr(node.expr_ret, ta, id_gen)
            print(f"{TAB}bra {result.end_label}")
        else:
            out = _EmitExpr(node.expr_ret, ta, id_gen)
            if node.expr_ret.x_type.size != 0:
                print(f"{TAB}pusharg {out}")
            print(f"{TAB}ret")
    elif isinstance(node, cwast.StmtBreak):
        block = node.x_target.label + ".end"
        print(f"{TAB}bra {block}  # break")
    elif isinstance(node, cwast.StmtContinue):
        block = node.x_target.label
        print(f"{TAB}bra {block}  # continue")
    elif isinstance(node, cwast.StmtExpr):
        ct: cwast.CanonType = node.expr.x_type
        if ct.ir_regs != o.DK.MEM:
            _EmitExpr(node.expr, ta, id_gen)
        else:
            assert ct.size > 0
            name = id_gen.NewName("stmt_stk_var")
            print(f"{TAB}.stk {name} {ct.alignment} {ct.size}")
            base = id_gen.NewName("stmt_stk_var_addr")
            kind = ta.get_data_address_reg_type()
            print(f"{TAB}lea.stk {base}:{kind} {name} 0")
            EmitExprToMemory(node.expr,  BaseOffset(base), ta, id_gen)
    elif isinstance(node, cwast.StmtIf):
        label_join = id_gen.NewName("br_join")
        if node.body_t and node.body_f:
            label_f = id_gen.NewName("br_f")
            _EmitConditional(node.cond, True, label_f, ta, id_gen)
            for c in node.body_t:
                _EmitStmt(c, result, ta, id_gen)
            if not _ChangesControlFlow(node.body_t[-1]):
                print(f"{TAB}bra {label_join}")
            print(f".bbl {label_f}")
            for c in node.body_f:
                _EmitStmt(c, result, ta, id_gen)
        elif node.body_t:
            _EmitConditional(node.cond, True, label_join, ta, id_gen)
            for c in node.body_t:
                _EmitStmt(c, result, ta, id_gen)
        else:  # also works for the case where body_f is empty
            _EmitConditional(node.cond, False, label_join, ta, id_gen)
            for c in node.body_f:
                _EmitStmt(c, result, ta, id_gen)
        print(f".bbl {label_join}")
    elif isinstance(node, cwast.StmtAssignment):
        lhs = node.lhs
        assert lhs.x_type.size != 0
        if isinstance(lhs, cwast.Id) and _StorageKindForId(lhs) is STORAGE_KIND.REGISTER:
            out = _EmitExpr(node.expr_rhs, ta, id_gen)
            print(f"{TAB}mov {lhs.x_symbol.name} = {out}")
        else:
            lhs = _GetLValueAddress(lhs, ta, id_gen)
            assert node.expr_rhs.x_type.size > 0, f"{node.expr_rhs} {node.x_srcloc} {node.expr_rhs.x_type}"
            EmitExprToMemory(node.expr_rhs, lhs, ta, id_gen)
    elif isinstance(node, cwast.StmtTrap):
        print(f"{TAB}trap")
    else:
        assert False, f"cannot generate code for {node}"


def RLE(data: bytes):
    last = None
    count = 0
    for d in data:
        if d != last:
            if last is not None:
                yield count, last
            last = d
            count = 1
        else:
            count += 1
    yield count, last


def _is_repeated_single_char(data: bytes):
    c = data[0]
    for x in data:
        if x != c:
            return False
    return True


def _EmitMemRepeatedByte(b, count: int, offset: int, purpose: str, purpose2="") -> int:
    print(f".data {count} [{b[0]}] # {offset} {count} {purpose}{purpose2}")
    return count


def _EmitMem(data, offset: int, purpose: str) -> int:
    if len(data) == 0:
        print(f'.data 0 []  # {offset} 0 {purpose}')
    elif _is_repeated_single_char(data):
        return _EmitMemRepeatedByte(data[0:1], len(data), offset, purpose)
    elif isinstance(data, (bytes, bytearray)):
        if len(data) < 100:
            print(
                f'.data 1 "{BytesToEscapedString(data)}" # {offset} {len(data)} {purpose}')
        else:
            for count, value in RLE(data):
                print(f".data {count} [{value}] # {offset} {count} {purpose}")
                offset += count
    else:
        assert False
    return len(data)


def _InitDataForBaseType(x_type: cwast.CanonType, val: Union[eval.EvalNum, eval.EvalUndef]) -> bytes:
    assert isinstance(val, eval.EvalNum), f"{val} {x_type}"
    assert (x_type.get_unwrapped_base_type_kind() == val.kind)
    return eval.SerializeBaseType(val)


_BYTE_ZERO = b"\0"
_BYTE_UNDEF = b"\0"
_BYTE_PADDING = b"\x6f"   # intentionally not zero?


def _EmitInitializerRec(node, ct: cwast.CanonType, offset: int, ta: type_corpus.TargetArchConfig) -> int:
    print(f"# rec: {ct.name}")
    if isinstance(node, cwast.ValAuto):
        return _EmitMemRepeatedByte(_BYTE_ZERO, ct.size, offset, "auto")
    assert isinstance(
        node, cwast.ValCompound), f"unexpected value {node}"
    rel_off = 0
    # note node.x_type may be compatible but not equal to ct
    for f, i in symbolize.IterateValRec(node.inits, node.x_type):
        if f.x_offset > rel_off:
            rel_off += _EmitMemRepeatedByte(_BYTE_PADDING,
                                            f.x_offset - rel_off, offset+rel_off, "padding")
        if i is None or isinstance(i.value_or_undef, cwast.ValUndef):
            rel_off += _EmitMemRepeatedByte(_BYTE_UNDEF, f.type.x_type.size, offset+rel_off,
                                            f.type.x_type.name)
        else:
            rel_off += _EmitInitializerRecursively(i.value_or_undef,
                                                   f.type.x_type, offset + rel_off, ta)
    return rel_off


def _EmitInitializerVec(node, ct: cwast.CanonType, offset: int, ta: type_corpus.TargetArchConfig) -> int:
    """When does  node.x_type != ct not hold?"""
    if isinstance(node, cwast.ValAuto):
        return _EmitMemRepeatedByte(_BYTE_ZERO, ct.size, offset, "auto ", ct.name)
    assert isinstance(
        node, (cwast.ValCompound, cwast.ValString)), f"{node}"
    width = ct.array_dim()
    if isinstance(node, cwast.ValString):
        assert isinstance(node.x_eval, eval.EvalBytes)
        value = node.x_eval.data
        assert len(
            value) == width, f"length mismatch {len(value)} vs {width} [{value}]"
        return _EmitMem(value, offset, ct.name)

    et = ct.underlying_type().get_unwrapped()
    assert isinstance(node, cwast.ValCompound), f"{node}"
    if et.is_base_type():
        # this special case creates a smaller IR
        out = bytearray()
        last = _InitDataForBaseType(et,
                                    eval.GetDefaultForBaseType(et.base_type_kind))
        for init in _IterateValVec(node.inits, width, node.x_srcloc):
            if init is not None:
                if isinstance(init.value_or_undef, cwast.ValUndef):
                    last = ZEROS[et.size]
                else:
                    last = _InitDataForBaseType(et, init.x_eval)
            out += last
        return _EmitMem(out, offset, ct.name)
    else:
        print(f"# vec: {ct.name}")
        last = cwast.ValUndef()
        stride = ct.size // width
        assert stride * width == ct.size, f"{ct.size} {width}"
        for i, init in enumerate(_IterateValVec(node.inits, width, node.x_srcloc)):
            if init is not None:
                last = init.value_or_undef
            count = _EmitInitializerRecursively(
                last, et, offset + i * stride, ta)
            if count != stride:
                _EmitMemRepeatedByte(_BYTE_PADDING, stride - count,
                                     offset + stride - count, "padding")
        return ct.size


def _EmitDataAddress(node, ct, offset, ta) -> int:
    assert isinstance(node, cwast.Id), f"{node} is not a symbol"
    assert isinstance(node.x_symbol, cwast.DefGlobal), f"{node.x_symbol}"
    name = node.x_symbol.name
    print(f".addr.mem {ta.get_data_address_size()} {name} 0")
    return ta.get_data_address_size()


def _EmitCodeAddress(node, ct, offset, ta) -> int:
    assert isinstance(node, cwast.DefFun), f"{node}"
    print(f".addr.fun {ta.get_code_address_size()} {node.name}")
    return ta.get_code_address_size()


def _EmitInitializerRecursively(node, ct: cwast.CanonType, offset: int, ta: type_corpus.TargetArchConfig) -> int:
    """When does  node.x_type != ct not hold?"""
    if ct.size == 0:
        # global data initialization may not have side-effects
        return 0
    assert offset == type_corpus.align(offset, ct.alignment)
    # TODO: support references to DefFun
    if isinstance(node, cwast.ValUndef):
        return _EmitMemRepeatedByte(_BYTE_UNDEF, ct.size, offset,  "undef ", ct.name)
    elif isinstance(node, cwast.Id):
        node_def = node.x_symbol
        if isinstance(node_def, cwast.DefFun):
            return _EmitCodeAddress(node_def, ct, offset, ta)
        assert isinstance(node_def, cwast.DefGlobal), f"{node_def}"
        return _EmitInitializerRecursively(node_def.initial_or_undef_or_auto, ct, offset, ta)
    elif isinstance(node, cwast.ExprFront):
        return _EmitDataAddress(node.container, ct, offset, ta)
    elif isinstance(node, cwast.ExprAddrOf):
        return _EmitDataAddress(node.expr_lhs, ct, offset, ta)
    elif isinstance(node, cwast.ExprWiden):
        count = _EmitInitializerRecursively(
            node.expr, node.expr.x_type, offset, ta)
        target = node.x_type.size
        if target != count:
            _EmitMemRepeatedByte(_BYTE_PADDING, target - count,
                                 offset + count, "widen_padding")
        return target
    elif isinstance(node, cwast.ValNum):
        assert ct.get_unwrapped().is_base_type()
        assert node.x_eval
        return _EmitMem(_InitDataForBaseType(ct, node.x_eval), offset, ct.name)

    #
    if ct.is_wrapped():
        assert isinstance(node, cwast.ExprWrap)
        return _EmitInitializerRecursively(node.expr, node.expr.x_type, offset, ta)
    elif ct.is_vec():
        return _EmitInitializerVec(node, ct, offset, ta)
    elif ct.is_rec():
        return _EmitInitializerRec(node, ct, offset, ta)

    else:
        assert False, f"unhandled node: {node} {ct.name}"


def EmitDefGlobal(node: cwast.DefGlobal, ta: type_corpus.TargetArchConfig) -> int:
    """Note there is some similarity to  EmitIRExprToMemory

    returns the amount of bytes emitted
    """
    def_type: cwast.CanonType = node.type_or_auto.x_type
    if def_type.get_unwrapped().is_void():
        # Note: we currently cannot use ct.size == 0 here because
        # we have globals like [0]U8 for empty strings
        return 0
    print(
        f"\n.mem {node.name} {def_type.alignment} {'RW' if node.mut else 'RO'}")

    return _EmitInitializerRecursively(node.initial_or_undef_or_auto,
                                       node.type_or_auto.x_type, 0, ta)


def EmitFunctionHeader(sig_name, kind, ct: cwast.CanonType):
    res_types, arg_types = _FunMachineTypes(ct)
    print(
        f"\n\n.fun {sig_name} {kind} [{r' '.join(res_types)}] = [{' '.join(arg_types)}]")


def EmitDefFun(node: cwast.DefFun, ta: type_corpus.TargetArchConfig, id_gen: identifier.IdGenIR):
    if not node.extern:
        EmitFunctionHeader(node.name, "NORMAL", node.x_type)
        _EmitFunctionProlog(node, id_gen)
        for c in node.body:
            _EmitStmt(c, None, ta, id_gen)
