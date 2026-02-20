// (c) Robert Muth - see LICENSE for more info

#include "BE/Base/ir.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <iomanip>
#include <optional>
#include <string_view>

#include "Util/assert.h"
#include "Util/immutable.h"
#include "Util/parse.h"

namespace cwerg::base {

namespace {

constexpr const char* kRefKindNames[] = {
    "INVALID",  //
    "INS",      //
    "EDG",      //
    "BBL",      //
    "FUN",      //
    "UNIT",     //
    "STR",      //
    "CONST"     //
    "REG",      //
    "STK",      //
    "MEM",      //
    "DATA",     //
    "JTB",      //
    "JEN",      //
    "CPU_REG",  //
    "STACK_SLOT",
};

}  // namespace

const char* EnumToString(RefKind x) { return kRefKindNames[unsigned(x)]; }

// =======================================
// All Stripes
// =======================================

struct Stripe<EdgCore, Edg> gEdgCore("EdgCore");
StripeBase* const gAllStripesEdg[] = {&gEdgCore, nullptr};
struct StripeGroup gStripeGroupEdg("EDG", gAllStripesEdg, 64 * 1024);

struct Stripe<InsCore, Ins> gInsCore("InsCore");
StripeBase* const gAllStripesIns[] = {&gInsCore, nullptr};
struct StripeGroup gStripeGroupIns("INS", gAllStripesIns, 256 * 1024);

struct Stripe<BblCore, Bbl> gBblCore("BblCore");
struct Stripe<BblBst, Bbl> gBblBst("BblBst");
struct Stripe<BblEdg, Bbl> gBblEdg("BblEdg");
struct Stripe<BblLiveness, Bbl> gBblLiveness("BblLiveness");

StripeBase* const gAllStripesBbl[] = {
    &gBblCore, &gBblBst, &gBblEdg, &gBblLiveness, nullptr};
struct StripeGroup gStripeGroupBbl("BBL", gAllStripesBbl, 32 * 1024);

struct Stripe<FunCore, Fun> gFunCore("FunCore");
struct Stripe<FunBst, Fun> gFunBst("FunBst");
struct Stripe<FunSig, Fun> gFunSig("FunSig");
StripeBase* const gAllStripesFun[] = {&gFunCore, &gFunBst, &gFunSig, nullptr};
struct StripeGroup gStripeGroupFun("FUN", gAllStripesFun, 4 * 1024);

struct Stripe<UnitCore, Unit> gUnitCore("UnitCore");
StripeBase* const gAllStripesUnit[] = {&gUnitCore, nullptr};
struct StripeGroup gStripeGroupUnit("UNIT", gAllStripesUnit, 1024);

struct Stripe<CpuRegCore, CpuReg> gCpuRegCore("CpuRegCore");
StripeBase* const gAllStripesCpuReg[] = {&gCpuRegCore, nullptr};
struct StripeGroup gStripeGroupCpuReg("CPU_REG", gAllStripesCpuReg, 1024);

struct Stripe<RegCore, Reg> gRegCore("RegCore");
struct Stripe<RegBst, Reg> gRegBst("RegBst");
StripeBase* const gAllStripesReg[] = {&gRegBst, &gRegCore, nullptr};
struct StripeGroup gStripeGroupReg("REG", gAllStripesReg, 256 * 1024);

struct Stripe<StkCore, Stk> gStkCore("StkCore");
struct Stripe<StkBst, Stk> gStkBst("StkBst");
StripeBase* const gAllStripesStk[] = {&gStkCore, &gStkBst, nullptr};
struct StripeGroup gStripeGroupStk("STK", gAllStripesStk, 64 * 1024);

struct Stripe<JenBst, Jen> gJenBst("JenBst");
StripeBase* const gAllStripesJen[] = {&gJenBst, nullptr};
struct StripeGroup gStripeGroupJen("JEN", gAllStripesJen, 4 * 1024);

struct Stripe<JtbCore, Jtb> gJtbCore("JtbCore");
struct Stripe<JtbBst, Jtb> gJtbBst("JtbBst");
StripeBase* const gAllStripesJtb[] = {&gJtbCore, &gJtbBst, nullptr};
struct StripeGroup gStripeGroupJtb("JTB", gAllStripesJtb, 1024);

struct Stripe<MemCore, Mem> gMemCore("MemCore");
struct Stripe<MemBst, Mem> gMemBst("MemBst");
StripeBase* const gAllStripesMem[] = {&gMemCore, &gMemBst, nullptr};
struct StripeGroup gStripeGroupMem("MEM", gAllStripesMem, 8 * 1024);

struct Stripe<DataCore, Data> gDataCore("DataCore");
StripeBase* const gAllStripesData[] = {&gDataCore, nullptr};
struct StripeGroup gStripeGroupData("DATA", gAllStripesData, 64 * 1024);

// =======================================
// Str Helpers
// =======================================

ImmutablePool StringPool(4);

Str StrNew(std::string_view s) {
  // we want a null byte at the end
  return Str(StringPool.Intern(s, 1));
}

const char* StrData(Str str) { return StringPool.Data(str.index()); }

int StrCmp(Str a, Str b) {
  if (a == b) return 0;
  return strcmp(StringPool.Data(a.index()), StringPool.Data(b.index()));
}

bool StrCmpLt(Str a, Str b) {
  if (a == b) return 0;
  return strcmp(StringPool.Data(a.index()), StringPool.Data(b.index())) < 0;
}

// =======================================
// Jtb Helpers
// =======================================
void JtbDelContent(Jtb jtb) {
  Jen last_jen = Jen(0);
  for (Jen jen : JtbJenIter(jtb)) {
    if (!last_jen.isnull()) JenDel(last_jen);
    last_jen = jen;
  }
  if (!last_jen.isnull()) JenDel(last_jen);
}

// =======================================
// Const Helpers
// =======================================

// Note this struct is designed so that for a const of bytewidth x, we
// can take the first x bytes to get the concrete representation for the
// constant. Note, that this exploits little endianess
struct ConstCore {
  union {
    float val_f32;
    double val_f64;
    uint64_t val_u64;   // little endian byte order also make this suitable
    int64_t val_acs64;  // for smaller bitwidths
  };
  DK kind;
};

ImmutablePool ConstantPool(alignof(ConstCore));

// Short integer constants are handled specially so that they do not require
// storage. We encode the value directly in the Const handle as follows:
// Recall that a Handle has the following structure:  [24bit: index][8bit: kind]
// We store small Consts in the index portion:
// [1bit: marker for short const][15bit: const value][8bit: const kind]
// Note the marker is high order bit which allows for simple testing.

bool ConstIsShort(Const num) { return int32_t(num.value) < 0; }

uint64_t ConstValueU(Const num) {
  if (ConstIsShort(num)) {
    return (num.value << 1U) >> 17U;
  }
  return ((ConstCore*)ConstantPool.Data(num.index()))->val_u64;
}

int64_t ConstValueACS(Const num) {
  if (ConstIsShort(num)) {
    // force sign extension
    return (int32_t(num.value << 1U) >> 17U);
  }
  return ((ConstCore*)ConstantPool.Data(num.index()))->val_acs64;
}

int32_t ConstValueInt32(Const num) {
  ASSERT(Kind(num) == RefKind::CONST,
         "not a const " << EnumToString(Kind(num)));
  int32_t val;
  switch (DKFlavor(ConstKind(num))) {
    case DK_FLAVOR_U:
      val = ConstValueU(num);
      ASSERT(val == ConstValueU(num), "out of range " << num);
      return val;
    case DK_FLAVOR_A:
    case DK_FLAVOR_C:
    case DK_FLAVOR_S:
      val = ConstValueACS(num);
      ASSERT(val == ConstValueACS(num), "out of range " << num);
      return val;
    default:
      ASSERT(false, "bad const " << num);
      return 0;
  }
}

int64_t ConstValueInt64(Const num) {
  ASSERT(Kind(num) == RefKind::CONST,
         "not a const " << EnumToString(Kind(num)));
  switch (DKFlavor(ConstKind(num))) {
    case DK_FLAVOR_U:
      return ConstValueU(num);
    case DK_FLAVOR_A:
    case DK_FLAVOR_C:
    case DK_FLAVOR_S:
      return ConstValueACS(num);
    default:
      ASSERT(false, "bad non int const " << num);
      return 0;
  }
}

double ConstValueF(Const num) {
  switch (ConstKind(num)) {
    case DK::R32:
      return ((ConstCore*)ConstantPool.Data(num.index()))->val_f32;
    case DK::R64:
      return ((ConstCore*)ConstantPool.Data(num.index()))->val_f64;
    default:
      ASSERT(false, "unexpected");
      return 0.0;
  }
}

DK ConstKind(Const num) {
  if (ConstIsShort(num)) {
    return DK(num.index() & 0xffU);
  }
  return ((ConstCore*)ConstantPool.Data(num.index()))->kind;
}

Const ConstNewF(DK kind, double v) {
  ConstCore num;
  // we are hashing the whole memory region - make sure it is deterministic
  memset(&num, 0, sizeof(num));
  num.kind = kind;
  if (kind == DK::R32) {
    num.val_f32 = v;
  } else {
    ASSERT(kind == DK::R64, "");
    num.val_f64 = v;
  }
  return Const(ConstantPool.Intern(std::string_view((char*)&num, sizeof(num))));
}

Const ConstNewU(DK kind, uint64_t v) {
  if (v < 32768) {
    return Const(Handle(1U << 23U | (v << 8U) | uint32_t(kind),
                        uint8_t(RefKind::CONST)));
  }
  ConstCore num;
  // we are hashing the whole memory region - make sure it is deterministic
  memset(&num, 0, sizeof(num));
  num.kind = kind;
  num.val_u64 = v;
  return Const(ConstantPool.Intern({(char*)&num, sizeof(num)}));
}

Const ConstNewACS(DK kind, int64_t v) {
  if (-16384 <= v && v < 16384) {
    return Const(Handle(1U << 23U | (v << 8U) | uint32_t(kind),
                        uint8_t(RefKind::CONST)));
  }
  ConstCore num;
  // we are hashing the whole memory region - make sure it is deterministic
  memset(&num, 0, sizeof(num));
  num.kind = kind;
  num.val_acs64 = v;
  return Const(ConstantPool.Intern({(char*)&num, sizeof(num)}));
}

Const ConstNewUint(uint64_t val) {
  if (val < (1ULL << 8U)) return ConstNewU(DK::U8, val);
  if (val < (1ULL << 16U)) return ConstNewU(DK::U16, val);
  if (val < (1ULL << 32U)) return ConstNewU(DK::U32, val);
  return ConstNewU(DK::U64, val);
}

Const ConstNewOffset(int64_t val) {
  if (val >= 0) {
    if (val < (1ULL << 7U)) return ConstNewACS(DK::S8, val);
    if (val < (1ULL << 15U)) return ConstNewACS(DK::S16, val);
    if (val < (1ULL << 31U)) return ConstNewACS(DK::S32, val);
    return ConstNewACS(DK::S64, val);
  } else {
    if (val >= -(1ULL << 7U)) return ConstNewACS(DK::S8, val);
    if (val >= -(1ULL << 15U)) return ConstNewACS(DK::S16, val);
    if (val >= -(1ULL << 31U)) return ConstNewACS(DK::S32, val);
    return ConstNewACS(DK::S64, val);
  }
}

Const ConstNewOffset(std::string_view v_str) {
  if (v_str[0] != '-') {
    return ConstNewUint(v_str);
  }
  // Must be negative
  auto val = ParseInt<int64_t>(v_str);
  ASSERT(val.has_value(), "");
  return ConstNewOffset(val.value());
}

Const ConstNewUint(std::string_view v_str) {
  auto val = ParseInt<uint64_t>(v_str);
  ASSERT(val.has_value(), "");
  return ConstNewUint(val.value());
}

Const ConstNew(DK kind, std::string_view v_str) {
  // std::cerr << "@@@ConstNew [" << RKToString(kind) <<  " " << v_str << "]\n";
  if (DKFlavor(kind) == DK_FLAVOR_F) {
    std::optional<double> val = ParseReal(v_str);
    if (!val) return Const(0);
    return ConstNewF(kind, val.value());
  } else if (DKFlavor(kind) == DK_FLAVOR_U) {
    std::optional<uint64_t> val = ParseInt<uint64_t>(v_str);
    if (!val) return Const(0);
    return ConstNewU(kind, val.value());
  } else {
    std::optional<int64_t> val = ParseInt<int64_t>(v_str);
    if (!val) return Const(0);
    return ConstNewACS(kind, val.value());
  }
}

std::ostream& operator<<(std::ostream& os, Const num) {
  const DK kind = ConstKind(num);
  const int flavor = DKFlavor(kind);
  switch (flavor) {
    default:
      os << "InvalidConstFlavor";
      return os;
    case DK_FLAVOR_U:
      os << ConstValueU(num);
      return os;
    case DK_FLAVOR_F: {
      char buffer[64];
      os << RenderRealStd(ConstValueF(num), buffer);
      return os;
    }
    case DK_FLAVOR_A:
    case DK_FLAVOR_C:
    case DK_FLAVOR_S:
      os << ConstValueACS(num);
      return os;
  }
}

bool ConstIsZero(Const num) {
  switch (ConstKind(num)) {
    default:
      ASSERT(false,
             "invalid zero test for Const " << EnumToString(ConstKind(num)));
      return false;
      //
    case DK::U8:
    case DK::U16:
    case DK::U32:
    case DK::U64:
      return ConstValueU(num) == 0;
    case DK::S8:
    case DK::S16:
    case DK::S32:
    case DK::S64:
      return ConstValueACS(num) == 0;
    case DK::R32:
    case DK::R64:
      return ConstValueF(num) == 0.0;
  }
}

bool ConstIsOne(Const num) {
  switch (ConstKind(num)) {
    default:
      ASSERT(false,
             "invalid zero test for Const " << EnumToString(ConstKind(num)));
      return false;
      //
    case DK::U8:
    case DK::U16:
    case DK::U32:
    case DK::U64:
      return ConstValueU(num) == 1;
    case DK::S8:
    case DK::S16:
    case DK::S32:
    case DK::S64:
      return ConstValueACS(num) == 1;

    case DK::R32:
    case DK::R64:
      return ConstValueF(num) == 1.0;
  }
}

std::string_view ConstToBytes(Const num) {
  ASSERT(!ConstIsShort(num), "NYI");
  const char* data = ConstantPool.Data(num.index());
  return std::string_view(data, DKBitWidth(ConstKind(num)) / 8);
}
// =======================================
// Bbl Helpers
// =======================================

// Also delete SuccEdgs
void BblDelContent(Bbl bbl) {
  Ins last_ins = Ins(0);
  for (Ins ins : BblInsIter(bbl)) {
    if (!last_ins.isnull()) InsDel(last_ins);
    last_ins = ins;
  }
  if (!last_ins.isnull()) InsDel(last_ins);

  Edg last_edg = Edg(0);
  for (Edg edg : BblSuccEdgIter(bbl)) {
    if (!last_edg.isnull()) EdgDel(last_edg);
    last_edg = edg;
  }
  if (!last_edg.isnull()) EdgDel(last_edg);
}

// =======================================
// Fun Helpers
// =======================================
std::string_view MaybeSkipCountPrefix(std::string_view s) {
  const char* cp = s.data();
  if (*cp == '$') {
    ++cp;
    while (*cp++ != '_');
  }
  return {cp, size_t(s.data() + s.size() - cp)};
}

Reg FunGetScratchReg(Fun fun, DK kind, std::string_view purpose,
                     bool add_kind_to_name) {
  ++gFunCore[fun].scratch_reg_id;
  char decbuf[32];
  auto dec = ToDecString(gFunCore[fun].scratch_reg_id, decbuf);
  ASSERT(purpose[0] != '$', "bad purpose " << purpose);

  char buf[kMaxIdLength];
  std::string_view name;
  if (add_kind_to_name) {
    name = StrCat(buf, sizeof(buf), "$", dec, "_", purpose, "_",
                  EnumToString(kind));
  } else {
    name = StrCat(buf, sizeof(buf), "$", dec, "_", purpose);
  }
  Str reg_name = StrNew(name);
  Reg reg = RegNew(kind, reg_name);
  FunRegAdd(fun, reg);
  return reg;
}

Reg FunFindOrAddCpuReg(Fun fun, CpuReg cpu_reg, DK kind) {
  char buf[kMaxIdLength];
  Str name = StrNew(StrCat(buf, sizeof(buf), "$", StrData(Name(cpu_reg)), "_",
                           EnumToString(kind)));
  Reg reg = FunRegFind(fun, name);
  if (reg.isnull()) {
    reg = RegNew(kind, name, cpu_reg);
    FunRegAdd(fun, reg);
  }
  return reg;
}

Bbl FunBblFindOrForwardDeclare(Fun fun, Str bbl_name) {
  Bbl bbl = FunBblFind(fun, bbl_name);
  if (bbl.isnull()) {
    bbl = BblNew(bbl_name);
    FunBblAddBst(fun, bbl);  // We intentionally to do call FunBblAppend() here
  }
  return bbl;
}

void FunFinalizeStackSlots(Fun fun) {
  std::vector<Reg> spilled_regs;
  for (Reg reg : FunRegIter(fun)) {
    if (Kind(RegCpuReg(reg)) == RefKind::STACK_SLOT) {
      spilled_regs.push_back(reg);
    }
  }
  auto cmp = [](const Reg& a, const Reg& b) -> bool {
    unsigned wa = DKBitWidth(RegKind(a));
    unsigned wb = DKBitWidth(RegKind(b));
    if (wa != wb) return wa < wb;
    return StrCmpLt(Name(a), Name(b));
  };
  std::sort(spilled_regs.begin(), spilled_regs.end(), cmp);

  uint32_t slot = 0;
  for (Reg reg : spilled_regs) {
    unsigned width = DKBitWidth(RegKind(reg)) / 8;
    slot += width - 1;
    slot = slot / width * width;
    RegCpuReg(reg) = StackSlotNew(slot);
    slot += width;
  }

  for (Stk stk : FunStkIter(fun)) {
    auto align = StkAlignment(stk);
    slot += align - 1;
    slot = slot / align * align;
    StkSlot(stk) = slot;
    slot += StkSize(stk);
  }
  FunStackSize(fun) = slot;
}

bool FunIsLeaf(Fun fun) {
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIter(bbl)) {
      if (InsOPC(ins) == OPC::JSR || InsOPC(ins) == OPC::BSR) return false;
    }
  }

  return true;
}

void FunDelContent(Fun fun) {
  for (Bbl bbl : FunBblIter(fun)) {
    BblDelContent(bbl);
  }
  Bbl last_bbl = Bbl(0);
  for (Bbl bbl : FunBblIter(fun)) {
    if (!last_bbl.isnull()) BblDel(last_bbl);
    last_bbl = bbl;
  }
  if (!last_bbl.isnull()) BblDel(last_bbl);

  Reg last_reg = Reg(0);
  for (Reg reg : FunRegIter(fun)) {
    if (!last_reg.isnull()) RegDel(last_reg);
    last_reg = reg;
  }
  if (!last_reg.isnull()) RegDel(last_reg);

  Stk last_stk = Stk(0);
  for (Stk stk : FunStkIter(fun)) {
    if (!last_stk.isnull()) StkDel(last_stk);
    last_stk = stk;
  }
  if (!last_stk.isnull()) StkDel(last_stk);

  for (Jtb jtb : FunJtbIter(fun)) {
    JtbDelContent(jtb);
  }

  Jtb last_jtb = Jtb(0);
  for (Jtb jtb : FunJtbIter(fun)) {
    if (!last_jtb.isnull()) JtbDel(last_jtb);
    last_jtb = jtb;
  }
  if (!last_jtb.isnull()) JtbDel(last_jtb);
}

// =======================================
// UnitHelpers
// =======================================

Str StrNewMemConstName(std::string_view data, DK kind) {
  ASSERT(data.size() < 32, "");
  char hexbuf[32 * 3];
  auto hex = ToHexDataStringWithSep(data, '_', hexbuf, sizeof(hexbuf));
  char buf[kMaxIdLength];
  return StrNew(
      StrCat(buf, sizeof(buf), "$const_", EnumToString(kind), "_", hex));
}

Mem UnitFindOrAddConstMem(Unit unit, Const num) {
  std::string_view data = ConstToBytes(num);
  Str name = StrNewMemConstName(data, ConstKind(num));
  Mem mem = UnitMemFind(unit, name);
  if (mem.isnull()) {
    mem = MemNew(name, MEM_KIND::RO, data.size());
    MemDataAdd(mem, DataNew(StrNew(data), data.size(), 1));
    UnitMemAdd(unit, mem);
  }
  return mem;
}

void BblReplaceInss(Bbl bbl, const std::vector<Ins>& inss) {
  ASSERT(!inss.empty(), "");
  Ins first = inss[0];
  BblInsList::Prev(first) = BblInsList::MakeSentinel(bbl);
  BblInsList::Head(bbl) = first;
  for (size_t i = 1; i < inss.size(); ++i) {
    BblInsList::Next(inss[i - 1]) = inss[i];
    BblInsList::Prev(inss[i]) = inss[i - 1];
  }
  Ins last = inss.back();
  BblInsList::Next(last) = BblInsList::MakeSentinel(bbl);
  BblInsList::Tail(bbl) = last;
}

}  // namespace cwerg::base
