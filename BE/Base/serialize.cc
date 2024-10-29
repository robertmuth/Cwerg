// (c) Robert Muth - see LICENSE for more info

#include "BE/Base/serialize.h"

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <string_view>

#include "BE/Base/opcode_gen.h"
#include "Util/parse.h"

namespace cwerg::base {
namespace {

using DirHandler = bool (*)(const std::vector<std::string_view>& token,
                            Unit mod);

int PopulateSig(const std::vector<std::string_view>& token, int start,
                DK sig[MAX_PARAMETERS]) {
  if (token[start][0] != '[') {
    std::cerr << "unexpected vector start: " << token[start] << "\n";
    return -1;
  }
  for (int i = 0; i < MAX_PARAMETERS; ++i) {
    std::string_view s = token[start + 1 + i];
    if (s[0] == ']') return i;
    sig[i] = DKFromString(s);
    if (sig[i] == DK::INVALID) {
      std::cerr << "cannot parse: " << s << "\n";
      return -1;
    }
  }
  std::cerr << "too many args\n";
  return -1;
}

bool FunHandler(const std::vector<std::string_view>& token, Unit unit) {
  const Str name = StrNew(token[1]);
  const FUN_KIND kind = FKFromString(token[2]);
  Fun fun = UnitFunFind(unit, name);
  if (fun.isnull()) {
    fun = FunNew(name, kind);
    UnitFunAddBst(unit, fun);
  } else if (FunKind(fun) == FUN_KIND::INVALID) {
    ASSERT(UnitFunList::Prev(fun).isnull(), "must be unlinked");
    FunKind(fun) = kind;
  } else if (FunKind(fun) == FUN_KIND::EXTERN || kind == FUN_KIND::EXTERN) {
    unsigned t = 3;
    for (unsigned i = 0; i < FunNumOutputTypes(fun); ++i, ++t) {
      ASSERT(FunOutputTypes(fun)[i] == DKFromString(token[t]), "");
    }
    t += 2;  // skip brackets
    for (unsigned i = 0; i < FunNumInputTypes(fun); ++i, ++t) {
      ASSERT(FunInputTypes(fun)[i] == DKFromString(token[t]), "");
    }
    if (kind == FUN_KIND::EXTERN) return true;  // ignore extern
    // fun.kind  is extern and kind is not. Make sure fun is current by
    // moving it to the end of the list
    UnitFunUnlink(fun);
    UnitFunAppendList(unit, fun);
  }

  // handle input/output sig
  const int num_outputs = PopulateSig(token, 3, FunOutputTypes(fun));
  if (num_outputs < 0) return false;
  FunNumOutputTypes(fun) = num_outputs;
  const int num_inputs =
      PopulateSig(token, 3 + 2 + num_outputs, FunInputTypes(fun));
  if (num_inputs < 0) return false;
  FunNumInputTypes(fun) = num_inputs;

  UnitFunAppendList(unit, fun);
  return true;
}

bool MemHandler(const std::vector<std::string_view>& token, Unit unit) {
  const Str name = StrNew(token[1]);
  const auto num = ParseInt<uint64_t>(token[2]);
  if (!num) {
    std::cerr << "cannot parse alignment: [" << token[2] << "]\n";
    return false;
  }
  const MEM_KIND kind = MKFromString(token[3]);
  Mem mem = UnitMemFind(unit, name);
  if (!mem.isnull()) {
    std::cerr << "mem already defined: " << token[1] << "\n";
    return false;
  }
  mem = MemNew(name, kind, num.value());

  UnitMemAddBst(unit, mem);
  UnitMemAppendList(unit, mem);
  return true;
}

bool JtbHandler(const std::vector<std::string_view>& token, Unit unit) {
  if ("[" != token[4] || "]" != token.back()) {
    std::cerr << "malformed jtb";
    return false;
  }
  // get "current" fun
  const Fun fun = UnitFunList::Tail(unit);
  if (fun.isnull()) {
    std::cerr << "jtb outside of fun";
    return false;
  }

  const Str name = StrNew(token[1]);
  Jtb jtb = FunJtbFind(fun, name);
  if (!jtb.isnull()) {
    std::cerr << "jtb already defined: " << token[1] << "\n";
    return false;
  }

  const auto size = ParseInt<uint64_t>(token[2]);
  if (!size) {
    std::cerr << "cannot parse jtb size: " << token[2] << "\n";
    return false;
  }

  Bbl def_bbl = FunBblFindOrForwardDeclare(fun, StrNew(token[3]));

  jtb = JtbNew(name, size.value(), def_bbl);
  FunJtbAdd(fun, jtb);
  for (size_t i = 5; i < token.size() - 1; i += 2) {
    const auto pos = ParseInt<uint64_t>(token[i]);
    if (!pos) {
      std::cerr << "cannot parse table entry: " << token[i] << "\n";
      return false;
    }
    Bbl bbl = FunBblFindOrForwardDeclare(fun, StrNew(token[i + 1]));
    const Jen jen = JenNew(pos.value(), bbl);
    if (!JtbJenAdd(jtb, jen)) {
      std::cerr << "duplicate table entry: " << token[i] << "\n";
      return false;
    }
  }
  return true;
}

bool StkHandler(const std::vector<std::string_view>& token, Unit unit) {
  // get "current" fun
  const Fun fun = UnitFunList::Tail(unit);
  if (fun.isnull()) {
    std::cerr << "stk outside of fun";
    return false;
  }

  const Str name = StrNew(token[1]);
  Stk stk = FunStkFind(fun, name);
  if (!stk.isnull()) {
    std::cerr << "stk already defined: " << token[1] << "\n";
    return false;
  }
  const auto alignment = ParseInt<uint64_t>(token[2]);
  if (!alignment) {
    std::cerr << "bad alignment: " << token[2] << "\n";
    return false;
  }

  const auto count = ParseInt<uint64_t>(token[3]);
  if (!count) {
    std::cerr << "bad count: " << token[3] << "\n";
    return false;
  }

  stk = StkNew(name, alignment.value(), count.value());
  FunStkAdd(fun, stk);
  return true;
}

bool BblHandler(const std::vector<std::string_view>& token, Unit unit) {
  const Str name = StrNew(token[1]);
  // get "current" fun
  const Fun fun = UnitFunList::Tail(unit);
  if (fun.isnull()) {
    std::cerr << "bbl outside of fun";
    return false;
  }
  Bbl bbl = FunBblFindOrForwardDeclare(fun, name);
  ASSERT(FunBblList::Prev(bbl).isnull(), "must be unlinked");
  FunBblAppendList(fun, bbl);
  return true;
}

bool RegHandler(const std::vector<std::string_view>& token, Unit unit) {
  const Fun fun = UnitFunList::Tail(unit);
  // cout << "Reg " << token[1] << " " << Name(fun) << "\n";
  const DK rk = DKFromString(token[1]);
  ASSERT(token[2][0] == '[', "expected [");
  ASSERT(token.back()[0] == ']', "expected ]");
  for (size_t i = 3; i < token.size() - 1; ++i) {
    const Str name = StrNew(token[i]);
    const Reg reg = RegNew(rk, name);
    if (!FunRegFind(fun, name).isnull()) {
      std::cerr << "Duplicate reg " << token[i] << "\n";
      return false;
    }
    FunRegAdd(fun, reg);
  }

  return true;
}

bool DataHandler(const std::vector<std::string_view>& token, Unit unit) {
  const Mem mem = UnitMemList::Tail(unit);
  if (mem.isnull()) {
    std::cerr << "addr.mem outside of mem\n";
    return false;
  }
  const auto repeat = ParseInt<uint64_t>(token[1]);
  size_t len;
  char buffer[4096];

  if (token[2] == "[") {
    if (token.back() != "]") {
      std::cerr << "malformed .data directive\n";
      return false;
    }
    len = token.size() - 4;
    for (size_t i = 0; i < len; ++i) {
      const auto x = ParseInt<uint64_t>(token[i + 3]);
      if (!x || x.value() > 255) {
        std::cerr << "malformed .data directive, value out of range "
                  << token[i + 3] << "\n";
      }
      buffer[i] = x.value();
    }
  } else if (token[2][0] == '"') {
    len = token[2].size() - 2;
    if (token[2][len + 1] != '"') {
      std::cerr << "malformed .data directive\n";
      return false;
    }
    if (len != 0)
      len = EscapedStringToBytes({token[2].data() + 1, len}, buffer);
  } else {
    std::cerr << "malformed .data directive\n";
    return false;
  }

  Str target = StrNew({buffer, len});  // note this is not really a str
  Data data = DataNew(target, len, repeat.value());
  MemDataAdd(mem, data);
  return true;
}

bool AddrMemHandler(const std::vector<std::string_view>& token, Unit unit) {
  const Mem mem = UnitMemList::Tail(unit);
  if (mem.isnull()) {
    std::cerr << "addr.mem outside of mem\n";
    return false;
  }
  const auto size = ParseInt<uint64_t>(token[1]);
  const Str name = StrNew(token[2]);
  const Mem target = UnitMemFind(unit, name);
  const auto extra = ParseInt<int64_t>(token[3]);
  if (!size || target.isnull() || !extra) return false;
  Data data = DataNew(target, size.value(), extra.value());
  MemDataAdd(mem, data);
  return true;
}

bool AddrFunHandler(const std::vector<std::string_view>& token, Unit unit) {
  const Mem mem = UnitMemList::Tail(unit);
  if (mem.isnull()) {
    std::cerr << "addr.fun outside of mem\n";
    return false;
  }

  const auto size = ParseInt<uint64_t>(token[1]);
  const Str name = StrNew(token[2]);
  const Fun target = UnitFunFind(unit, name);
  if (!size || target.isnull()) return false;
  Data data = DataNew(target, size.value(), 0);
  MemDataAdd(mem, data);
  return true;
}

const DirHandler Handlers[] = {
    nullptr,
    &MemHandler,      // DIR_MEM = 0x01,
    &DataHandler,     // DIR_DATA = 0x02,
    &AddrFunHandler,  // DIR_ADDR_FUN = 0x03,
    &AddrMemHandler,  // DIR_ADDR_MEM = 0x04,
    &FunHandler,      // DIR_FUN = 0x05,
    &BblHandler,      // DIR_BBL = 0x06,
    &RegHandler,      // DIR_REG = 0x07,
    &StkHandler,      // DIR_STK = 0x08,
    &JtbHandler,      // DIR_JTB = 0x09,
};

struct RegFragments {
  std::string_view reg_name;
  std::string_view kind_name;
  std::string_view cpu_reg_name;
};

// strings look like:  $r10@rax  or addr:A64
RegFragments ParseRegString(std::string_view s) {
  RegFragments out;
  const auto cpu_reg_pos = s.rfind('@');
  if (cpu_reg_pos != std::string_view::npos) {
    out.cpu_reg_name = s.substr(cpu_reg_pos + 1);
    s = s.substr(0, cpu_reg_pos);
  }
  const auto kind_pos = s.rfind(':');
  if (kind_pos != std::string_view::npos) {
    out.kind_name = s.substr(kind_pos + 1);
    s = s.substr(0, kind_pos);
  }
  out.reg_name = s;
  return out;
}

Handle GetRegOrConstInsOperand(
    OP_KIND ok, TC tc, std::string_view s, Fun fun, DK last_kind,
    const std::map<std::string_view, CpuReg>& cpu_reg_map) {
  if (ok == OP_KIND::REG_OR_CONST) {
    ok = IsLikelyNum(s) ? OP_KIND::CONST : OP_KIND::REG;
  }

  if (ok == OP_KIND::REG) {
    const RegFragments frags = ParseRegString(s);
    Reg reg;
    const Str name = StrNew(frags.reg_name);
    if (frags.kind_name.empty()) {
      reg = FunRegFind(fun, name);
      if (reg.isnull()) {
        std::cerr << "undefined reg [" << s << "]\n";
        return HandleInvalid;
      }
    } else {
      const DK rk = DKFromString(frags.kind_name);
      ASSERT(rk != DK::INVALID,
             "bad type: [" << frags.kind_name << "] in " << s);
      reg = FunRegFind(fun, name);
      if (!reg.isnull()) {
        std::cerr << "reg already defined [" << frags.reg_name << "]\n";
        return Reg(0);
      }
      reg = RegNew(rk, name);
      FunRegAdd(fun, reg);
    }

    if (!frags.cpu_reg_name.empty()) {
      Handle cpu_reg;
      if (frags.cpu_reg_name == "STK") {
        cpu_reg = StackSlotNew(0);
      } else {
        auto it = cpu_reg_map.find(frags.cpu_reg_name);
        ASSERT(it != cpu_reg_map.end(),
               "unknown cpu reg " << frags.cpu_reg_name);
        cpu_reg = it->second;
      }
      if (RegCpuReg(reg).isnull()) {
        RegCpuReg(reg) = CpuReg(cpu_reg);
      } else {
        ASSERT(RegCpuReg(reg) == CpuReg(cpu_reg), "");
      }
    }
    return reg;
  } else if (ok == OP_KIND::CONST) {
    auto colon_pos = s.rfind(':');
    Const num;
    if (colon_pos != std::string_view::npos) {
      std::string_view val(s.data(), colon_pos);
      std::string_view ext(s.data() + colon_pos + 1, s.size() - colon_pos - 1);
      const DK rk = DKFromString(ext);
      ASSERT(rk != DK::INVALID, "bad type: " << ext);
      num = ConstNew(rk, val);
    } else if (tc == TC::SAME_AS_PREV) {
      num = ConstNew(last_kind, s);
    } else if (tc == TC::OFFSET) {
      num = ConstNewOffset(s);
    } else if (tc == TC::UINT) {
      num = ConstNewUint(s);
    }
    return num;
  } else {
    ASSERT(false, "");
    return HandleInvalid;
  }
}

Handle GetOtherInsOperand(OP_KIND ok, std::string_view s, Unit mod, Fun fun) {
  switch (ok) {
    case OP_KIND::BBL: {
      const Str name = StrNew(s);
      Bbl bbl = FunBblFind(fun, name);
      if (bbl.isnull()) {
        bbl = BblNew(name);
        FunBblAddBst(fun, bbl);
      }
      return bbl;
    }

    case OP_KIND::MEM: {
      const Str name = StrNew(s);
      const Mem mem = UnitMemFind(mod, name);
      if (mem.isnull()) {
        std::cerr << "undefined mem: " << s << "\n";
      }
      return mem;
    }
    case OP_KIND::STK: {
      const Str name = StrNew(s);
      Stk stk = FunStkFind(fun, name);
      if (stk.isnull()) {
        std::cerr << "undefined stk: " << s << "\n";
      }
      return stk;
    }

    case OP_KIND::FUN: {
      const Str name = StrNew(s);
      Fun fun_op = UnitFunFind(mod, name);
      if (fun_op.isnull()) {
        fun_op = FunNew(name, FUN_KIND::INVALID);
        UnitFunAddBst(mod, fun_op);
      }
      return fun_op;
    }

    case OP_KIND::JTB: {
      const Str name = StrNew(s);
      Jtb jtb = FunJtbFind(fun, name);
      ASSERT(!jtb.isnull(), "undefined jtb " << s);
      return jtb;
    }
      // case OK::FIELD: return Handle();
    case OP_KIND::BYTES: {
      ASSERT(s.size() >= 2 && s[0] == '"', "expected quoted string got " << s);
      return StrNew({s.data() + 1, s.size() - 2});
    }
    default:
      ASSERT(false, "unreachable " << base::EnumToString(ok));
      return Handle();
  }
}

bool GetAllInsOperands(const Opcode& opcode,
                       const std::vector<std::string_view>& token, Unit mod,
                       Fun fun,
                       const std::map<std::string_view, CpuReg>& cpu_reg_map,
                       Handle operands[]) {
  const size_t num_ops = opcode.num_operands;
  // cout << opcode.name << " " << num_ops << " " << token.size() - 1 << "\n";
  if (num_ops != token.size() - 1) {
    if (num_ops != token.size() - 2 || token[token.size() - 1][0] == '#') {
      std::cerr << "not enough operands for " << token[0] << "\n";
      return false;
    }
  }

  DK last_type = DK::INVALID;
  for (unsigned i = 0; i < opcode.num_operands; ++i) {
    const OP_KIND ok = opcode.operand_kinds[i];
    std::string_view op_str = token[i + 1];

    if (ok == OP_KIND::INVALID) {
      operands[i] = Handle();
      continue;
    }

    Handle op;
    if (ok == OP_KIND::REG || ok == OP_KIND::CONST ||
        ok == OP_KIND::REG_OR_CONST) {
      op = GetRegOrConstInsOperand(ok, opcode.constraints[i], op_str, fun,
                                   last_type, cpu_reg_map);
      last_type =
          op.kind() == RefKind::REG ? RegKind(Reg(op)) : ConstKind(Const(op));
    } else {
      op = GetOtherInsOperand(ok, op_str, mod, fun);
    }
    if (op.isnull()) {
      std::cerr << "bad operand " << op_str << "\n";
      return false;
    }
    operands[i] = op;
  }
  return true;
}

// TODO: get rid of this hack which simplifies FrontEndC/translate.py a bit
OPC MaybeRewritePseudoOpcodes(std::vector<std::string_view>* token, Unit unit,
                              Fun fun) {
  if ((*token)[0] != "lea") {
    return OPC::INVALID;
  }

  const Str src = StrNew((*token)[2]);
  if (!UnitFunFind(unit, src).isnull()) return OPC::LEA_FUN;

  if (token->size() == 3) {
    token->push_back("0");
  }
  if (!FunRegFind(fun, src).isnull()) {
    // in case the register name is shadows a global
    return OPC::LEA;
  } else if (!FunStkFind(fun, src).isnull()) {
    return OPC::LEA_STK;
  } else if (!UnitMemFind(unit, src).isnull()) {
    return OPC::LEA_MEM;
  } else {
    // could be a constant
    return OPC::LEA;
  }
}

}  // namespace

void InsRenderToAsm(Ins ins, std::ostream* output) {
  const Opcode& opcode = InsOpcode(ins);
  *output << opcode.name;
  const unsigned num_ops = opcode.num_operands;
  for (unsigned i = 0; i < num_ops; ++i) {
    const Handle op = InsOperand(ins, i);
    switch (op.kind()) {
      case RefKind::REG: {
        *output << " " << Name(Reg(op));
        Handle cpu_reg = RegCpuReg(Reg(op));
        if (cpu_reg.kind() == RefKind::CPU_REG) {
          *output << "@" << Name(CpuReg(cpu_reg));
        } else if (cpu_reg.kind() == RefKind::STACK_SLOT) {
          *output << "@STK";
        }
        break;
      }
      case RefKind::CONST:
        *output << " " << Const(op);
        if (opcode.constraints[i] != TC::OFFSET &&
            opcode.constraints[i] != TC::SAME_AS_PREV) {
          *output << ":" << EnumToString(ConstKind(Const(op)));
        }
        break;
      case RefKind::BBL:
        *output << " " << Name(Bbl(op));
        break;
      case RefKind::MEM:
        *output << " " << Name(Mem(op));
        break;
      case RefKind::FUN:
        *output << " " << Name(Fun(op));
        break;
      case RefKind::STK:
        *output << " " << Name(Stk(op));
        break;
      case RefKind::JTB:
        *output << " " << Name(Jtb(op));
        break;
      case RefKind::STR:
        *output << " \"" << StrData(Str(op)) << "\"";
        break;
      default:
        ASSERT(false, "unsupported operand kind " << int(op.kind()));
        break;
    }
  }
}

void RenderRegBitVec(Fun fun, BitVec bv, std::ostream* output) {
  const unsigned num_regs = FunNumRegs(fun);
  const HandleVec reg_map = FunRegMap(fun);
  std::vector<std::string_view> live;

  for (unsigned i = 0; i < num_regs; ++i) {
    if (bv.BitGet(i)) {
      live.emplace_back(StrData(Name(Reg(reg_map.Get(i)))));
    }
  }
  std::sort(live.begin(), live.end());

  *output << "[";
  const char* sep = "";
  for (const auto str : live) {
    *output << sep << str;
    sep = "  ";
  }
  *output << "]";
}

void BblRenderToAsm(Bbl bbl, Fun fun, std::ostream* output, bool number) {
  *output << ".bbl " << Name(bbl);
  const char* group_sep = "  #  ";

#if 1
  if (!BblSuccEdgList::IsEmpty(bbl)) {
    std::vector<std::string> succs;
    for (Edg edg : BblSuccEdgIter(bbl)) {
      if (edg.isnull()) {
        succs.emplace_back("INVALID_EDG");
        break;
      }
      succs.emplace_back(StrData(Name(EdgSuccBbl(edg))));
    }
    std::sort(succs.begin(), succs.end());
    *output << group_sep << "edge_out[";
    group_sep = "  ";
    const char* sep = "";
    for (const auto& str : succs) {
      *output << sep << str;
      sep = "  ";
    }
    *output << "]";
  }
#endif
#if 0
  if (!BblPredEdgList::IsEmpty(bbl)) {
    std::vector<std::string> preds;
    for (Edg edg : BblPredEdgIter(bbl)) {
      if (edg.isnull()) {
        preds.push_back("INVALID_EDG");
        break;
      }
      preds.push_back(StrData(Name(EdgPredBbl(edg))) + std::string (":") +
                      std::string(ToDecString(edg.index(), buf)));
    }
    std::sort(preds.begin(), preds.end());
    *output << group_sep << " edge_in[";
    group_sep = "  ";
    const char* sep = "";
    for (const auto str : preds) {
      *output << sep << str;
      sep = "  ";
    }
    *output << "]";
  }
#endif

  const BitVec live_out = BblLiveOut(bbl);
  if (!fun.isnull() && live_out != BitVecInvalid) {
    if (live_out.Popcnt() > 0) {
      // std::sort(live.begin(), live.end(), cmp);
      *output << group_sep << "live_out";
      group_sep = "  ";
      RenderRegBitVec(fun, BblLiveOut(bbl), output);
    }
  }
  *output << "\n";
  unsigned count = 0;
  for (Ins ins : BblInsIter(bbl)) {
    if (number) {
      *output << std::setw(3) << count++ << " ";
    } else {
      *output << "    ";
    }
    InsRenderToAsm(ins, output);
    *output << "\n";
  }
}

void EmitParamList(unsigned num_types, DK* types, std::ostream* output) {
  *output << "[";
  const char* sep = "";
  for (int i = 0; i < num_types; ++i) {
    *output << sep << EnumToString(types[i]);
    sep = " ";
  }
  *output << "]";
}

void MaybeEmitCpuRegList(unsigned num_regs, CpuReg* regs,
                         std::string_view prefix, std::ostream* output) {
  if (num_regs == 0) return;

  *output << prefix << ": [";
  const char* sep = "";
  for (int i = 0; i < num_regs; ++i) {
    *output << sep << Name(regs[i]);
    sep = " ";
  }
  *output << "]\n";
}

void FunRenderToAsm(Fun fun, std::ostream* output, bool number) {
  *output << ".fun"
          << " " << Name(fun) << " " << EnumToString(FunKind(fun)) << " ";
  EmitParamList(FunNumOutputTypes(fun), FunOutputTypes(fun), output);
  *output << " = ";
  EmitParamList(FunNumInputTypes(fun), FunInputTypes(fun), output);
  *output << "\n";
  MaybeEmitCpuRegList(FunNumCpuLiveIn(fun), FunCpuLiveIn(fun), "# live_in",
                      output);
  MaybeEmitCpuRegList(FunNumCpuLiveOut(fun), FunCpuLiveOut(fun), "# live_out",
                      output);
  MaybeEmitCpuRegList(FunNumCpuLiveClobber(fun), FunCpuLiveClobber(fun),
                      "# live_clobber", output);

  // Regs
  std::map<DK, std::vector<Reg>> regs_by_kind;
  for (Reg reg : FunRegIter(fun)) {
    regs_by_kind[RegKind(reg)].push_back(reg);
  }
  for (auto [key, val] : regs_by_kind) {
    std::sort(val.begin(), val.end(), [](const Reg& a, const Reg& b) {
      return StrCmpLt(Name(a), Name(b));
    });
    *output << ".reg " << EnumToString(key) << " [";
    const char* sep = "";
    for (const Reg reg : val) {
      *output << sep << Name(reg);
      Handle cpu_reg = RegCpuReg(reg);
      if (cpu_reg.kind() == RefKind::CPU_REG) {
        *output << "@" << Name(CpuReg(cpu_reg));
      } else if (cpu_reg.kind() == RefKind::STACK_SLOT) {
        *output << "@STK";
      }
      sep = " ";
    }
    *output << "]\n";
  }

  // Stks
  for (Stk stk : FunStkIter(fun)) {
    *output << ".stk " << Name(stk) << " " << StkAlignment(stk) << " "
            << StkSize(stk) << "\n";
  }

  // JTB
  for (Jtb jtb : FunJtbIter(fun)) {
    *output << ".jtb " << Name(jtb) << " " << JtbSize(jtb) << " "
            << Name(JtbDefBbl(jtb)) << " [";
    const char* sep = "";
    for (Jen jen : JtbJenIter(jtb)) {
      *output << sep << gJenBst[jen].pos << " " << Name(JenBbl(jen));
      sep = " ";
    }

    *output << "]\n";
  }

  for (Bbl bbl : FunBblIter(fun)) {
    BblRenderToAsm(bbl, fun, output, number);
  }
}

void MemRenderToAsm(Mem mem, std::ostream* output) {
  *output << ".mem " << Name(mem) << " " << MemAlignment(mem) << " "
          << EnumToString(MemKind(mem)) << "\n";
  for (Data data : MemDataIter(mem)) {
    const uint32_t size = DataSize(data);
    const int32_t extra = DataExtra(data);
    Handle target = DataTarget(data);
    switch (target.kind()) {
      case RefKind::STR: {
        uint32_t len = size;
        char buffer[4096];
        if (len > 0) {
          len = BytesToEscapedString({StrData(Str(target)), len}, buffer);
        }
        buffer[len] = 0;
        *output << "    .data " << extra << " \"" << buffer << "\"\n";
      } break;
      case RefKind::MEM:
        *output << "    .addr.mem " << size << " " << Name(Mem(target)) << " "
                << extra << "\n";
        break;
      case RefKind::FUN:
        *output << "    .addr.fun " << size << " " << Name(Fun(target)) << "\n";
        break;
      default:
        ASSERT(false, "unsupported target for data " << int(target.kind()));
        break;
    }
  }
}

void UnitRenderToAsm(Unit unit, std::ostream* output) {
  for (Mem mem : UnitMemIter(unit)) MemRenderToAsm(mem, output);
  for (Fun fun : UnitFunIter(unit)) {
    *output << "\n";
    FunRenderToAsm(fun, output);
  }
}

bool UnitAppendFromAsm(Unit unit, std::string_view input,
                       const std::vector<CpuReg>& cpu_regs) {
  std::map<std::string_view, CpuReg> cpu_reg_map;
  for (const CpuReg reg : cpu_regs) {
    cpu_reg_map[StrData(Name(reg))] = reg;
  }

  Handle operands[MAX_OPERANDS];
  std::vector<std::string_view> vec;
  for (unsigned line_num = 0; !input.empty(); ++line_num) {
    const size_t new_line_pos = input.find('\n');
    std::string_view line = new_line_pos == input.npos
                                ? input
                                : std::string_view(input.data(), new_line_pos);
    input.remove_prefix(line.size() + 1);
    vec.clear();
    if (!ParseLineWithStrings(line, false, &vec)) {
      std::cerr << "Error while parsing line " << line_num << "\n" << line;
      return false;
    }

    // std::cerr << "@@reading: " << line << "\n";
    std::vector<std::string_view> token;
    for (const std::string_view s : vec) {
      if (s != "=") token.push_back(s);
    }
    if (token.empty()) continue;
    if (token[0][0] == '#') continue;
    if (token.back()[0] == '#') {
      token.pop_back();
      if (token.empty()) continue;
    }

    OPC opc = OPCFromString(token[0]);
    if (opc == OPC::LEA && !UnitFunList::Tail(unit).isnull()) {
      opc = MaybeRewritePseudoOpcodes(&token, unit, UnitFunList::Tail(unit));
    }
    if (opc == OPC::INVALID) {
      std::cerr << "Unknown opcode: " << line << "\n";
      return false;
    }

    const Opcode& opcode = GlobalOpcodes[uint8_t(opc)];
    if (opcode.kind == OPC_KIND::DIRECTIVE) {
      auto handler = Handlers[uint8_t(opc)];
      ASSERT(handler != nullptr, "unsupported directive: " << opcode.name);
      if (!handler(token, unit)) {
        std::cerr << "Error processing line::\n" << line;
        return false;
      }
    } else {
      const Fun fun = UnitFunList::Tail(unit);
      ASSERT(!fun.isnull(), "");
      const Bbl bbl = FunBblList::Tail(fun);
      ASSERT(!bbl.isnull(), "");
      if (!GetAllInsOperands(opcode, token, unit, fun, cpu_reg_map, operands)) {
        std::cerr << "Error parsing operands:\n" << line;
        return false;
      }
      ASSERT(MAX_OPERANDS == 5, "Fix the call below if this fires");
      const Ins ins = InsNew(opc, operands[0], operands[1], operands[2],
                             operands[3], operands[4]);

      BblInsAdd(bbl, ins);
      // std::cerr << opcode.name << "\n";
    }
  }
  return true;
}

}  // namespace cwerg::base
