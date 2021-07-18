#pragma once
// (c) Robert Muth - see LICENSE for more info

/*
All the basic abstractions and their stripes.
*/

#include "Base/opcode_gen.h"
#include "Util/assert.h"
#include "Util/bitvec.h"
#include "Util/bst.h"
#include "Util/handle.h"
#include "Util/handlevec.h"
#include "Util/list.h"
#include "Util/stripe.h"

#include <cstdint>
#include <cstring>
#include <vector>

namespace cwerg::base {

const unsigned kMaxIdLength = 1024;

// Handle Wrappers for the primary abstractions.
// We only take advantage of Interned strings being a Handle is for DataNew
struct Str : public Handle {
  explicit Str(uint32_t index = 0) : Handle(index, RefKind::STR) {}
  explicit Str(Handle ref) : Handle(ref.value) {}
};

struct Ins : public Handle {
  explicit constexpr Ins(uint32_t index = 0) : Handle(index, RefKind::INS) {}
  explicit constexpr Ins(Handle ref) : Handle(ref.value) {}
};

struct Edg : public Handle {
  explicit constexpr Edg(uint32_t index = 0) : Handle(index, RefKind::EDG) {}
  explicit constexpr Edg(Handle ref) : Handle(ref.value) {}
};

struct Bbl : public Handle {
  explicit constexpr Bbl(uint32_t index = 0) : Handle(index, RefKind::BBL) {}
  explicit constexpr Bbl(Handle ref) : Handle(ref.value) {}
};

struct Fun : public Handle {
  explicit constexpr Fun(uint32_t index = 0) : Handle(index, RefKind::FUN) {}
  explicit constexpr Fun(Handle ref) : Handle(ref.value) {}
};

struct Unit : public Handle {
  explicit constexpr Unit(uint32_t index = 0) : Handle(index, RefKind::UNIT) {}
  explicit constexpr Unit(Handle ref) : Handle(ref.value) {}
};

struct Reg : public Handle {
  explicit constexpr Reg(uint32_t index = 0) : Handle(index, RefKind::REG) {}
  explicit constexpr Reg(Handle ref) : Handle(ref.value) {}
};

struct CpuReg : public Handle {
  explicit constexpr CpuReg(uint32_t index = 0)
      : Handle(index, RefKind::CPU_REG) {}
  explicit constexpr CpuReg(Handle ref) : Handle(ref.value) {}
};

struct Const : public Handle {
  explicit constexpr Const(uint32_t index = 0)
      : Handle(index, RefKind::CONST) {}
  explicit constexpr Const(Handle ref) : Handle(ref.value) {}
};

struct Stk : public Handle {
  explicit constexpr Stk(uint32_t index = 0) : Handle(index, RefKind::STK) {}
  explicit constexpr Stk(Handle ref) : Handle(ref.value) {}
};

struct Mem : public Handle {
  explicit constexpr Mem(uint32_t index = 0) : Handle(index, RefKind::MEM) {}
  explicit constexpr Mem(Handle ref) : Handle(ref.value) {}
};

struct Data : public Handle {
  explicit constexpr Data(uint32_t index = 0) : Handle(index, RefKind::DATA) {}
  explicit constexpr Data(Handle ref) : Handle(ref.value) {}
};

struct Jtb : public Handle {
  explicit constexpr Jtb(uint32_t index = 0) : Handle(index, RefKind::JTB) {}
  explicit constexpr Jtb(Handle ref) : Handle(ref.value) {}
};

struct Jen : public Handle {
  explicit constexpr Jen(uint32_t index = 0) : Handle(index, RefKind::JEN) {}
  explicit constexpr Jen(Handle ref) : Handle(ref.value) {}
};

constexpr const Handle UnlinkedRef(0, RefKind::INVALID);
constexpr const Handle HandleInvalid(0, RefKind::INVALID);

// =======================================
// Data (chunk of pre-allocated (neither heap nor stack) data)
// =======================================
struct DataCore {
  Data next;
  Data prev;
  // The type of target determines what directive is modelled:
  // Str: .data      (size holds length of data, extra holds repeat)
  // Fun: .addr.fun  (size holds width of fun addr, extra must hold zero num)
  // Mem: .addr.mem  (size holds width of mem addr, extra holds offset)
  Handle target;
  uint32_t size;
  int32_t extra;
};

extern struct Stripe<DataCore, Data> gDataCore;
extern struct StripeGroup gStripeGroupData;

inline uint32_t& DataSize(Data data) { return gDataCore[data].size; }
inline int32_t& DataExtra(Data data) { return gDataCore[data].extra; }
inline Handle& DataTarget(Data data) { return gDataCore[data].target; }

inline Data DataNew(Handle target, uint32_t size, int32_t extra) {
  Data out = Data(gStripeGroupData.New().index());
  gDataCore[out] = {Data(0), Data(0), target, size, extra};
  return out;
}

// =======================================
// Mem (pre-allocated memory region)
// =======================================
struct MemCore {
  Mem next;
  Mem prev;
  uint32_t alignment;
  MEM_KIND kind;
  Data data_head;  // Each memory object consists of several data chunks
  Data data_tail;
};

struct MemBst {
  Mem left, right, parent;
  Str name;
};

extern struct Stripe<MemCore, Mem> gMemCore;
extern struct Stripe<MemBst, Mem> gMemBst;
extern struct StripeGroup gStripeGroupMem;

inline Str& Name(Mem mem) { return gMemBst[mem].name; }

inline Mem MemNew(MEM_KIND kind, uint32_t alignment, Str name) {
  Mem out = Mem(gStripeGroupMem.New().index());
  gMemCore[out] = {Mem(0), Mem(0), alignment, kind, Data(out), Data(out)};
  Name(out) = name;
  return out;
}

inline MEM_KIND& MemKind(Mem mem) { return gMemCore[mem].kind; }
inline uint32_t& MemAlignment(Mem mem) { return gMemCore[mem].alignment; }

struct MemDataList {
  using ITEM = Data;
  using CONT = Mem;
  static bool IsSentinel(ITEM x) { return x.kind() == RefKind::MEM; }
  static ITEM MakeSentinel(CONT y) { return ITEM(y); }
  static ITEM& Next(ITEM x) { return gDataCore[x].next; }
  static ITEM& Prev(ITEM x) { return gDataCore[x].prev; }
  static ITEM& Tail(CONT y) { return gMemCore[y].data_tail; }
  static ITEM& Head(CONT y) { return gMemCore[y].data_head; }
};

#define MemDataInsertBefore ListInsertBefore<MemDataList>
#define MemDataAppend ListAppend<MemDataList>
#define MemDataInsertAfter ListInsertAfter<MemDataList>
#define MemDataPrepend ListPrepend<MemDataList>
#define MemDataUnlink ListUnlink<MemDataList>
#define MemDataIter ListIter<MemDataList>

inline uint32_t MemSize(Mem mem) {
  uint32_t out = 0;
  for (Data data : MemDataIter(mem)) {
    unsigned repeats =
        (DataTarget(data).kind() == RefKind::STR) ? DataExtra(data) : 1;
    out += DataSize(data) * repeats;
  }
  return out;
}

// =======================================
// Str API
//
// Note: Str is immutable
// =======================================
extern Str StrNew(std::string_view s);
extern const char* StrData(Str str);
extern int StrCmp(Str a, Str b);
extern int StrCmpLt(Str a, Str b);

// This may seem like a strange thing to sort by, but if just want to
// tests "set membership" it is much cheaper than string comparison
inline int HandleCmp(Handle a, Handle b) {
  if (a == b) return 0;
  else if (a < b) return -1;
  else return 1;
}

inline std::ostream& operator<<(std::ostream& os, Str str) {
  os << StrData(str);
  return os;
}

// =======================================
// Const (constant operand)
//
// Note: Const is immutable
// =======================================

extern Const ConstNewF(DK kind, double v);
extern Const ConstNewACS(DK kind, int64_t v);
extern Const ConstNewU(DK kind, uint64_t v);
extern Const ConstNew(DK kind, std::string_view v_str);

extern Const ConstNewOffset(int64_t v);
extern Const ConstNewOffset(std::string_view v_str);

extern Const ConstNewUint(uint64_t val);
extern Const ConstNewUint(std::string_view v_str);

extern uint64_t ConstValueU(Const num);
extern int64_t ConstValueACS(Const num);
extern double ConstValueF(Const num);

// asserts if value is out of range
extern int32_t ConstValueInt32(Const num);
extern int64_t ConstValueInt64(Const num);

extern DK ConstKind(Const num);
extern std::string_view ConstToBytes(Const num);

// This will print the Const including suffix
extern std::ostream& operator<<(std::ostream& os, Const num);

// =======================================
// Jen (jump table entry)
// =======================================
struct JenBst {
  Jen left, right, parent;
  uint32_t pos;  // must be positive
  Bbl bbl;
};

extern struct Stripe<JenBst, Jen> gJenBst;
extern struct StripeGroup gStripeGroupJen;

inline Jen JenNew(uint32_t pos, Bbl bbl) {
  Jen out = Jen(gStripeGroupJen.New().index());
  gJenBst[out] = {Jen(0), Jen(0), Jen(0), pos, bbl};
  return out;
}

inline Bbl& JenBbl(Jen jen) { return gJenBst[jen].bbl; }
inline uint32_t& JenPos(Jen jen) { return gJenBst[jen].pos; }

// =======================================
// Jtb (jump table)
// =======================================
struct JtbCore {
  uint32_t size;
  Bbl def_bbl;
  Jen entries;
};

struct JtbBst {
  Jtb left, right, parent;
  Str name;
};

extern struct Stripe<JtbCore, Jtb> gJtbCore;
extern struct Stripe<JtbBst, Jtb> gJtbBst;
extern struct StripeGroup gStripeGroupJtb;

inline Str& Name(Jtb jtb) { return gJtbBst[jtb].name; }

inline Jtb JtbNew(Str name, uint32_t size, Bbl def_bbl) {
  Jtb out = Jtb(gStripeGroupJtb.New().index());
  gJtbCore[out] = {size, def_bbl, Jen(0)};
  Name(out) = name;
  return out;
}

inline Bbl& JtbDefBbl(Jtb jtb) { return gJtbCore[jtb].def_bbl; }
inline uint32_t& JtbSize(Jtb jtb) { return gJtbCore[jtb].size; }

struct JtbJenBst {
  using ITEM = Jen;
  using CONT = Jtb;
  using KEY = uint32_t;
  static KEY Key(ITEM x) { return gJenBst[x].pos; }
  static ITEM& Left(ITEM x) { return gJenBst[x].left; }
  static ITEM& Right(ITEM x) { return gJenBst[x].right; }
  static ITEM& Parent(ITEM x) { return gJenBst[x].parent; }
  static int Cmp(KEY a, KEY b) { return (a < b) ? -1 : (a > b); }
  static ITEM& Root(CONT y) { return gJtbCore[y].entries; }
};

#define JtbJenAdd BstAdd<JtbJenBst>
#define JtbJenIter BstIter<JtbJenBst>

// =======================================
// CpuReg (machine register)
// =======================================

struct CpuRegCore {
  uint16_t no;
  uint8_t kind;
  Str name;
};

extern struct Stripe<CpuRegCore, CpuReg> gCpuRegCore;
extern struct StripeGroup gStripeGroupCpuReg;

inline Str& Name(CpuReg reg) { return gCpuRegCore[reg].name; }
inline uint16_t& CpuRegNo(CpuReg reg) { return gCpuRegCore[reg].no; }
inline uint8_t& CpuRegKind(CpuReg reg) { return gCpuRegCore[reg].kind; }

inline CpuReg CpuRegNew(uint16_t no, uint8_t kind, Str name) {
  CpuReg out = CpuReg(gStripeGroupCpuReg.New().index());
  gCpuRegCore[out] = {no, kind, name};
  return out;
}

// =======================================
// Reg (register operand)
// =======================================
enum class REG_FLAG : uint8_t {
  GLOBAL = 1 << 0,
  MULTI_DEF = 1 << 2,
  LAC = 1 << 3,
  IS_READ = 1 << 4,
  MULTI_READ = 1 << 5,
  ALLOCATED = 1 << 6,
  MARKED = 1 << 7
};

struct RegCore {
  uint16_t no;  // numbering used by liveness analysis
  DK kind;
  uint8_t flags;
  Ins def_ins;
  Bbl def_bbl;
  CpuReg cpu_reg;
  // The stuff below should probably go into anther stripe
  Stk spill_slot;
  // Note: last_use must be zero at all times except during LiveRange
  // computation
  uint16_t last_use;
  uint16_t use_count;
};

struct RegBst {
  Reg left, right, parent;
  Str name;
};

extern struct Stripe<RegCore, Reg> gRegCore;
extern struct Stripe<RegBst, Reg> gRegBst;
extern struct StripeGroup gStripeGroupReg;

inline Str& Name(Reg reg) { return gRegBst[reg].name; }
inline uint16_t& RegNo(Reg reg) { return gRegCore[reg].no; }
inline DK& RegKind(Reg reg) { return gRegCore[reg].kind; }
inline uint8_t& RegFlags(Reg reg) { return gRegCore[reg].flags; }
inline Ins& RegDefIns(Reg reg) { return gRegCore[reg].def_ins; }
inline Bbl& RegDefBbl(Reg reg) { return gRegCore[reg].def_bbl; }
inline CpuReg& RegCpuReg(Reg reg) { return gRegCore[reg].cpu_reg; }
inline Stk& RegSpillSlot(Reg reg) { return gRegCore[reg].spill_slot; }
inline uint16_t& RegLastUse(Reg reg) { return gRegCore[reg].last_use; }
inline uint16_t& RegUseCount(Reg reg) { return gRegCore[reg].use_count; }

inline bool RegHasFlag(Reg reg, REG_FLAG flag) {
  return (RegFlags(reg) & unsigned(flag)) != 0;
}

inline void RegClearFlag(Reg reg, REG_FLAG flag) {
  RegFlags(reg) &= ~unsigned(flag);
}

inline Reg RegNew(DK kind, Str name, CpuReg cpu_reg = CpuReg(0)) {
  Reg out = Reg(gStripeGroupReg.New().index());
  gRegCore[out] = {0, kind, 0, Ins(0), Bbl(0), cpu_reg, Stk(0), 0, 0};
  Name(out) = name;
  return out;
}

inline void RegDel(Reg reg) { gStripeGroupReg.Del(reg); }

inline DK RegOrConstKind(Handle op) {
  if (op.kind() == RefKind::REG) return RegKind(Reg(op));
  ASSERT(op.kind() == RefKind::CONST, "");
  return ConstKind(Const(op));
}
// =======================================
// Stk (stack allocated memory)
// =======================================
struct StkCore {
  uint32_t alignment;
  uint32_t size;
  uint32_t slot;  // TODO: make this a Const
};

struct StkBst {
  Stk left, right, parent;
  Str name;
};

extern struct Stripe<StkCore, Stk> gStkCore;
extern struct Stripe<StkBst, Stk> gStkBst;
extern struct StripeGroup gStripeGroupStk;

inline Str& Name(Stk stk) { return gStkBst[stk].name; }
inline uint32_t& StkAlignment(Stk stk) { return gStkCore[stk].alignment; }
inline uint32_t& StkSize(Stk stk) { return gStkCore[stk].size; }
inline uint32_t& StkSlot(Stk stk) { return gStkCore[stk].slot; }

inline Stk StkNew(Str name, uint32_t alignment, uint32_t size) {
  Stk out = Stk(gStripeGroupStk.New().index());
  gStkCore[out] = {alignment, size, 0};
  Name(out) = name;
  return out;
}

inline void StkDel(Stk stk) { gStripeGroupStk.Del(stk); }

// =======================================
// Ins (instruction)
// =======================================

struct InsCore {
  Ins prev;
  Ins next;
  OPC opcode;
  // operands are primarily Regs
  // Defined Regs preceded used Regs
  // For an "add dst, src1, src2" instruction
  // the three operands would be the registers in order
  // padded by HandleInvalid to the size of the operands.
  Handle operands[MAX_OPERANDS];
  // For each used operand Reg the Ins defining it.
  // top means multiple Ins define the value, bot means no Ins defines the
  // value.
  Ins defs[MAX_OPERANDS];
};

extern struct Stripe<InsCore, Ins> gInsCore;
extern struct StripeGroup gStripeGroupIns;

inline Ins InsInit(Ins ins,
                   OPC opcode,
                   Handle h0 = HandleInvalid,
                   Handle h1 = HandleInvalid,
                   Handle h2 = HandleInvalid,
                   Handle h3 = HandleInvalid,
                   Handle h4 = HandleInvalid) {
  gInsCore[ins].opcode = opcode;
  gInsCore[ins].operands[0] = h0;
  gInsCore[ins].operands[1] = h1;
  gInsCore[ins].operands[2] = h2;
  gInsCore[ins].operands[3] = h3;
  gInsCore[ins].operands[4] = h4;
  return ins;
}

inline Ins InsNew(OPC opcode,
                  Handle h0 = HandleInvalid,
                  Handle h1 = HandleInvalid,
                  Handle h2 = HandleInvalid,
                  Handle h3 = HandleInvalid,
                  Handle h4 = HandleInvalid) {
  return InsInit(Ins(gStripeGroupIns.New().index()), opcode, h0, h1, h2, h3,
                 h4);
}

inline void InsDel(Ins ins) { gStripeGroupIns.Del(ins); }

inline OPC_KIND InsOpcodeKind(Ins ins) {
  return GlobalOpcodes[int(gInsCore[ins].opcode)].kind;
}

inline const Opcode& InsOpcode(Ins ins) {
  return GlobalOpcodes[int(gInsCore[ins].opcode)];
}

inline OPC& InsOPC(Ins ins) { return gInsCore[ins].opcode; }

inline Handle& InsOperand(Ins ins, unsigned pos) {
  return gInsCore[ins].operands[pos];
}

inline Handle& InsDef(Ins ins, unsigned pos) { return gInsCore[ins].defs[pos]; }

inline void InsSwapOps(Ins ins, unsigned pos1, unsigned pos2) {
  Handle tmp_op = InsOperand(ins, pos1);
  InsOperand(ins, pos1) = InsOperand(ins, pos2);
  InsOperand(ins, pos2) = tmp_op;
  tmp_op = InsDef(ins, pos1);
  InsDef(ins, pos1) = InsDef(ins, pos2);
  InsDef(ins, pos2) = tmp_op;
}
// =======================================
// Edg (control flow edge between bbls)
// =======================================

struct EdgCore {
  // Double linking seems overkill - reconsider this
  Edg succ_prev;
  Edg succ_next;
  Bbl succ;

  Edg pred_prev;
  Edg pred_next;
  Bbl pred;
};

extern struct Stripe<EdgCore, Edg> gEdgCore;
extern struct StripeGroup gStripeGroupEdg;

inline Edg EdgNew(Bbl pred, Bbl succ) {
  const Edg out = Edg(gStripeGroupEdg.New().index());
  gEdgCore[out] = {Edg(succ), Edg(succ), succ, Edg(pred), Edg(pred), pred};
  return out;
}

inline Bbl& EdgPredBbl(Edg edg) { return gEdgCore[edg].pred; }
inline Bbl& EdgSuccBbl(Edg edg) { return gEdgCore[edg].succ; }

inline void EdgDel(Edg edg) { gStripeGroupEdg.Del(edg); }

// =======================================
// Bbl (basic block)
// =======================================

struct BblCore {
  Bbl prev;
  Bbl next;
  Ins ins_head;
  Ins ins_tail;
};

struct BblBst {
  Bbl left, right, parent;
  Str name;
};

struct BblEdg {
  Edg succ_edg_head, succ_edg_tail;
  Edg pred_edg_head, pred_edg_tail;
};

struct BblLiveness {
  BitVec out;
  BitVec in;
  BitVec def;
  BitVec use;
};

struct BblReachingDefs {
  HandleVec in;
  HandleVec out;
  HandleVec def;
};

extern struct Stripe<BblCore, Bbl> gBblCore;
extern struct Stripe<BblBst, Bbl> gBblBst;
extern struct Stripe<BblEdg, Bbl> gBblEdg;
extern struct Stripe<BblLiveness, Bbl> gBblLiveness;
extern struct Stripe<BblReachingDefs, Bbl> gBblReachingDefs;
extern struct StripeGroup gStripeGroupBbl;

inline Str& Name(Bbl bbl) { return gBblBst[bbl].name; }
inline BitVec& BblLiveOut(Bbl bbl) { return gBblLiveness[bbl].out; }
inline BitVec& BblLiveIn(Bbl bbl) { return gBblLiveness[bbl].in; }
inline BitVec& BblLiveUse(Bbl bbl) { return gBblLiveness[bbl].use; }
inline BitVec& BblLiveDef(Bbl bbl) { return gBblLiveness[bbl].def; }

inline HandleVec& BblReachingDefsOut(Bbl bbl) {
  return gBblReachingDefs[bbl].out;
}
inline HandleVec& BblReachingDefsIn(Bbl bbl) {
  return gBblReachingDefs[bbl].in;
}
inline HandleVec& BblReachingDefsDef(Bbl bbl) {
  return gBblReachingDefs[bbl].def;
}

inline Bbl BblNew(Str name) {
  Bbl out = Bbl(gStripeGroupBbl.New().index());
  gBblCore[out] = {Bbl(0), Bbl(0), Ins(out), Ins(out)};
  gBblBst[out] = {Bbl(0), Bbl(0), Bbl(0), name};
  gBblEdg[out] = {Edg(out), Edg(out), Edg(out), Edg(out)};
  gBblLiveness[out] = {BitVecInvalid, BitVecInvalid, BitVecInvalid,
                       BitVecInvalid};
  gBblReachingDefs[out] = {HandleVecInvalid, HandleVecInvalid,
                           HandleVecInvalid};

  return out;
}

inline void BblDel(Bbl bbl) { gStripeGroupBbl.Del(bbl); }

struct BblInsList {
  using ITEM = Ins;
  using CONT = Bbl;
  static bool IsSentinel(ITEM x) { return x.kind() == RefKind::BBL; }
  static ITEM MakeSentinel(CONT y) { return ITEM(y); }
  static ITEM& Next(ITEM x) { return gInsCore[x].next; }
  static ITEM& Prev(ITEM x) { return gInsCore[x].prev; }
  static ITEM& Tail(CONT y) { return gBblCore[y].ins_tail; }
  static ITEM& Head(CONT y) { return gBblCore[y].ins_head; }
  static bool IsEmpty(CONT y) { return IsSentinel(Head(y)); }
};

#define BblInsInsertBefore ListInsertBefore<BblInsList>
#define BblInsAddList ListAppend<BblInsList>
#define BblInsInsertAfter ListInsertAfter<BblInsList>
#define BblInsPrepend ListPrepend<BblInsList>
#define BblInsUnlink ListUnlink<BblInsList>
#define BblInsIter ListIter<BblInsList>
#define BblInsIterReverse ListIterReverse<BblInsList>

inline Ins BblInsAdd(Bbl bbl, Ins ins) {
  BblInsAddList(bbl, ins);
  return ins;
}

struct BblSuccEdgList {
  using ITEM = Edg;
  using CONT = Bbl;
  static bool IsSentinel(ITEM x) { return x.kind() == RefKind::BBL; }
  static ITEM MakeSentinel(CONT y) { return ITEM(y); }
  static ITEM& Next(ITEM x) { return gEdgCore[x].succ_next; }
  static ITEM& Prev(ITEM x) { return gEdgCore[x].succ_prev; }
  static ITEM& Tail(CONT y) { return gBblEdg[y].succ_edg_tail; }
  static ITEM& Head(CONT y) { return gBblEdg[y].succ_edg_head; }
  static bool IsEmpty(CONT y) { return IsSentinel(Head(y)); }
};

#define BblSuccEdgAppend ListAppend<BblSuccEdgList>
#define BblSuccEdgUnlink ListUnlink<BblSuccEdgList>
#define BblSuccEdgIter ListIter<BblSuccEdgList>

struct BblPredEdgList {
  using ITEM = Edg;
  using CONT = Bbl;
  static bool IsSentinel(ITEM x) { return x.kind() == RefKind::BBL; }
  static ITEM MakeSentinel(CONT y) { return ITEM(y); }
  static ITEM& Next(ITEM x) { return gEdgCore[x].pred_next; }
  static ITEM& Prev(ITEM x) { return gEdgCore[x].pred_prev; }
  static ITEM& Tail(CONT y) { return gBblEdg[y].pred_edg_tail; }
  static ITEM& Head(CONT y) { return gBblEdg[y].pred_edg_head; }
  static bool IsEmpty(CONT y) { return IsSentinel(Head(y)); }
};

#define BblPredEdgAppend ListAppend<BblPredEdgList>
#define BblPredEdgUnlink ListUnlink<BblPredEdgList>
#define BblPredEdgIter ListIter<BblPredEdgList>
// =======================================
// Fun (function)
// =======================================
struct FunBst {
  Fun left, right, parent;
  Str name;
};

struct FunCore {
  Fun prev;
  Fun next;

  Bbl bbl_head;
  Bbl bbl_tail;
  Bbl bbl_syms;

  Stk stk_syms;
  Reg reg_syms;
  Jtb jtb_syms;

  uint32_t scratch_reg_id;

  FUN_KIND kind;
  HandleVec reg_map;  // registers by their number
  uint32_t stack_size;
  uint16_t num_regs;
};

struct FunSig {
  DK input_types[MAX_PARAMETERS];
  DK output_types[MAX_PARAMETERS];
  CpuReg cpu_live_in[MAX_PARAMETERS];
  CpuReg cpu_live_out[MAX_PARAMETERS];
  CpuReg cpu_live_clobber[MAX_PARAMETERS];
  //
  uint8_t num_input_types;
  uint8_t num_output_types;
  uint8_t num_cpu_live_in;
  uint8_t num_cpu_live_out;
  uint8_t num_cpu_live_clobber;
};

extern struct Stripe<FunCore, Fun> gFunCore;
extern struct Stripe<FunBst, Fun> gFunBst;
extern struct Stripe<FunSig, Fun> gFunSig;
extern struct StripeGroup gStripeGroupFun;

inline Str& Name(Fun fun) { return gFunBst[fun].name; }
inline uint32_t& FunStackSize(Fun fun) { return gFunCore[fun].stack_size; }
inline uint16_t& FunNumRegs(Fun fun) { return gFunCore[fun].num_regs; }
inline HandleVec& FunRegMap(Fun fun) { return gFunCore[fun].reg_map; }
inline FUN_KIND& FunKind(Fun fun) { return gFunCore[fun].kind; }

inline DK* FunInputTypes(Fun fun) { return gFunSig[fun].input_types; }
inline uint8_t& FunNumInputTypes(Fun fun) {
  return gFunSig[fun].num_input_types;
}
inline DK* FunOutputTypes(Fun fun) { return gFunSig[fun].output_types; }
inline uint8_t& FunNumOutputTypes(Fun fun) {
  return gFunSig[fun].num_output_types;
}

inline uint8_t& FunNumCpuLiveIn(Fun fun) {
  return gFunSig[fun].num_cpu_live_in;
}
inline uint8_t& FunNumCpuLiveOut(Fun fun) {
  return gFunSig[fun].num_cpu_live_out;
}
inline uint8_t& FunNumCpuLiveClobber(Fun fun) {
  return gFunSig[fun].num_cpu_live_clobber;
}
inline CpuReg* FunCpuLiveIn(Fun fun) { return gFunSig[fun].cpu_live_in; }
inline CpuReg* FunCpuLiveOut(Fun fun) { return gFunSig[fun].cpu_live_out; }
inline CpuReg* FunCpuLiveClobber(Fun fun) {
  return gFunSig[fun].cpu_live_clobber;
}

inline Fun FunNew(Str name, FUN_KIND kind = FUN_KIND::INVALID) {
  Fun out = Fun(gStripeGroupFun.New().index());
  gFunCore[out] = {
      Fun(UnlinkedRef),
      Fun(UnlinkedRef),
      Bbl(out),
      Bbl(out),
      Bbl(0),
      Stk(0),
      Reg(0),
      Jtb(0),
      0,  // scratch_reg
      kind,
      HandleVecInvalid,  // reg_map
      0,                 // stack_size
      0                  // num_regs
  };

  memset(&gFunSig[out], 0, sizeof(gFunSig[out]));

  Name(out) = name;
  return out;
}

extern std::string_view MaybeSkipCountPrefix(std::string_view s);

extern Reg FunGetScratchReg(Fun fun,
                            DK narrow_kind,
                            std::string_view purpose,
                            bool add_kind_to_name);

extern Reg FunFindOrAddCpuReg(Fun fun, CpuReg cpu_reg, DK kind);

struct FunRegBst {
  using ITEM = Reg;
  using CONT = Fun;
  using KEY = Str;
  static KEY Key(ITEM x) { return Name(x); }
  static ITEM& Left(ITEM x) { return gRegBst[x].left; }
  static ITEM& Right(ITEM x) { return gRegBst[x].right; }
  static ITEM& Parent(ITEM x) { return gRegBst[x].parent; }
  // This is called a lot and needs to be fast
  // We do not care about alphabetical order except when rendering output.
  // We do the sorting buy name at that time.
  static int Cmp(Str a, Str b) { return HandleCmp(a, b); }
  static ITEM& Root(CONT y) { return gFunCore[y].reg_syms; }
};

extern Bbl FunBblFindOrForwardDeclare(Fun fun, Str bbl_name);

#define FunRegIter BstIter<FunRegBst>
#define FunRegFind BstFind<FunRegBst>
#define FunRegAddBst BstAdd<FunRegBst>
#define FunRegDel BstDel<FunRegBst>

inline Reg FunRegAdd(Fun fun, Reg reg) {
    FunRegAddBst(fun, reg);
    return reg;
}

inline bool FunHasReg(Fun fun, Str reg_name) {
  return !FunRegFind(fun, reg_name).isnull();
}

struct FunStkBst {
  using ITEM = Stk;
  using CONT = Fun;
  using KEY = Str;

  static KEY Key(ITEM x) { return Name(x); }
  static ITEM& Left(ITEM x) { return gStkBst[x].left; }
  static ITEM& Right(ITEM x) { return gStkBst[x].right; }
  static ITEM& Parent(ITEM x) { return gStkBst[x].parent; }
  static int Cmp(Str a, Str b) { return StrCmp(a, b); }
  static ITEM& Root(CONT y) { return gFunCore[y].stk_syms; }
};

#define FunStkFind BstFind<FunStkBst>
#define FunStkAdd BstAdd<FunStkBst>
#define FunStkIter BstIter<FunStkBst>

inline bool FunHasStk(Fun fun, Str stk) {
  return !FunStkFind(fun, stk).isnull();
}

extern void FunFinalizeStackSlots(Fun Fun);


struct FunJtbBst {
  using ITEM = Jtb;
  using CONT = Fun;
  using KEY = Str;
  static KEY Key(ITEM x) { return Name(x); }
  static ITEM& Left(ITEM x) { return gJtbBst[x].left; }
  static ITEM& Right(ITEM x) { return gJtbBst[x].right; }
  static ITEM& Parent(ITEM x) { return gJtbBst[x].parent; }
  static int Cmp(Str a, Str b) { return StrCmp(a, b); }
  static ITEM& Root(CONT y) { return gFunCore[y].jtb_syms; }
};

#define FunJtbFind BstFind<FunJtbBst>
#define FunJtbAdd BstAdd<FunJtbBst>
#define FunJtbDel BstDel<FunJtbBst>
#define FunJtbIter BstIter<FunJtbBst>

struct FunBblBst {
  using ITEM = Bbl;
  using CONT = Fun;
  using KEY = Str;
  static KEY Key(ITEM x) { return Name(x); }
  static ITEM& Left(ITEM x) { return gBblBst[x].left; }
  static ITEM& Right(ITEM x) { return gBblBst[x].right; }
  static ITEM& Parent(ITEM x) { return gBblBst[x].parent; }
  // We do not care about alphabetical order
  static int Cmp(Str a, Str b) { return HandleCmp(a, b); }
  static ITEM& Root(CONT y) { return gFunCore[y].bbl_syms; }
};

#define FunBblFind BstFind<FunBblBst>
#define FunBblAddBst BstAdd<FunBblBst>
#define FunBblDel BstDel<FunBblBst>

struct FunBblList {
  using ITEM = Bbl;
  using CONT = Fun;
  static bool IsSentinel(ITEM x) { return x.kind() == RefKind::FUN; }
  static ITEM MakeSentinel(CONT y) { return ITEM(y); }
  static ITEM& Next(ITEM x) { return gBblCore[x].next; }
  static ITEM& Prev(ITEM x) { return gBblCore[x].prev; }
  static ITEM& Tail(CONT y) { return gFunCore[y].bbl_tail; }
  static ITEM& Head(CONT y) { return gFunCore[y].bbl_head; }
  static bool IsEmpty(CONT y) { return IsSentinel(Head(y)); }
};

#define FunBblInsertBefore ListInsertBefore<FunBblList>
#define FunBblAddList ListAppend<FunBblList>
#define FunBblInsertAfter ListInsertAfter<FunBblList>
#define FunBblPrepend ListPrepend<FunBblList>
#define FunBblUnlink ListUnlink<FunBblList>
#define FunBblIter ListIter<FunBblList>
#define FunBblIterReverse ListIterReverse<FunBblList>

inline Bbl FunBblAdd(Fun fun, Bbl bbl) {
  FunBblAddBst(fun, bbl);
  FunBblAddList(fun, bbl);
  return bbl;
}

extern bool FunIsLeaf(Fun fun);
// =======================================
// Unit
// =======================================
struct UnitCore {
  Str name;

  Fun fun_head;
  Fun fun_tail;
  Fun fun_syms;

  Mem mem_head;
  Mem mem_tail;
  Mem mem_syms;
};

extern struct Stripe<UnitCore, Unit> gUnitCore;
extern struct StripeGroup gStripeGroupUnit;

inline Str& Name(Unit mod) { return gUnitCore[mod].name; }

inline Unit UnitNew(Str name) {
  Unit out = Unit(gStripeGroupUnit.New().index());
  gUnitCore[out] = {name,  //
                    Fun(out), Fun(out), Fun(0), Mem(out), Mem(out), Mem(0)};
  return out;
}

struct UnitFunBst {
  using ITEM = Fun;
  using CONT = Unit;
  using KEY = Str;
  static KEY Key(ITEM x) { return Name(x); }
  static ITEM& Left(ITEM x) { return gFunBst[x].left; }
  static ITEM& Right(ITEM x) { return gFunBst[x].right; }
  static ITEM& Parent(ITEM x) { return gFunBst[x].parent; }
  // We have UnitFunList if we care about determinism
  static int Cmp(Str a, Str b) { return HandleCmp(a, b); }
  static ITEM& Root(CONT y) { return gUnitCore[y].fun_syms; }
};

#define UnitFunFind BstFind<UnitFunBst>
#define UnitFunAddBst BstAdd<UnitFunBst>

struct UnitFunList {
  using ITEM = Fun;
  using CONT = Unit;
  static bool IsSentinel(ITEM x) { return x.kind() == RefKind::UNIT; }
  static ITEM MakeSentinel(CONT y) { return ITEM(y); }
  static ITEM& Next(ITEM x) { return gFunCore[x].next; }
  static ITEM& Prev(ITEM x) { return gFunCore[x].prev; }
  static ITEM& Tail(CONT y) { return gUnitCore[y].fun_tail; }
  static ITEM& Head(CONT y) { return gUnitCore[y].fun_head; }
};

#define UnitFunInsertBefore ListInsertBefore<UnitFunList>
#define UnitFunAddList ListAppend<UnitFunList>
#define UnitFunInsertAfter ListInsertAfter<UnitFunList>
#define UnitFunPrepend ListPrepend<UniFunList>
#define UnitFunUnlink ListUnlink<UnitFunList>
#define UnitFunIter ListIter<UnitFunList>

inline Fun  UnitFunAdd(Unit unit, Fun fun) {
  UnitFunAddBst(unit, fun);
  UnitFunAddList(unit, fun);
  return fun;
}

struct UnitMemBst {
  using ITEM = Mem;
  using CONT = Unit;
  using KEY = Str;

  static KEY Key(ITEM x) { return Name(x); }
  static ITEM& Left(ITEM x) { return gMemBst[x].left; }
  static ITEM& Right(ITEM x) { return gMemBst[x].right; }
  static ITEM& Parent(ITEM x) { return gMemBst[x].parent; }
  // We have UnitMemList if we care about determinism
  static int Cmp(Str a, Str b) { return HandleCmp(a, b); }
  static ITEM& Root(CONT y) { return gUnitCore[y].mem_syms; }
};

#define UnitMemFind BstFind<UnitMemBst>
#define UnitMemAdd BstAdd<UnitMemBst>

struct UnitMemList {
  using ITEM = Mem;
  using CONT = Unit;
  static bool IsSentinel(ITEM x) { return x.kind() == RefKind::UNIT; }
  static ITEM MakeSentinel(CONT y) { return ITEM(y); }
  static ITEM& Next(ITEM x) { return gMemCore[x].next; }
  static ITEM& Prev(ITEM x) { return gMemCore[x].prev; }
  static ITEM& Tail(CONT y) { return gUnitCore[y].mem_tail; }
  static ITEM& Head(CONT y) { return gUnitCore[y].mem_head; }
};

#define UnitMemInsertBefore ListInsertBefore<UnitMemList>
#define UnitMemAppend ListAppend<UnitMemList>
#define UnitMemInsertAfter ListInsertAfter<UnitMemList>
#define UnitMemPrepend ListPrepend<UnitMemList>
#define UnitMemUnlink ListUnlink<UnitMemList>
#define UnitMemIter ListIter<UnitMemList>

extern Mem UnitFindOrAddConstMem(Unit unit, Const num);

extern bool ConstIsZero(Const num);
extern bool ConstIsOne(Const num);

}  // namespace cwerg::base
