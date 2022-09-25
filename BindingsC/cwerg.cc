#include "BindingsC/cwerg.h"

#include "Base/ir.h"
#include "Base/serialize.h"

#include <cstdlib>

using namespace cwerg;
using namespace cwerg::base;

namespace {
template <typename T>
T Make(CW_Handle h) {
  return T(Handle(h));
}
}  // namespace

/* ============================================================ */
/* Constructors */
/* ============================================================ */

extern "C" CW_Jtb CW_JtbNew(const char* name, uint32_t size, CW_Bbl def_bbl,
                            int num_entries, const CW_JtbEntry entries[]) {
  Jtb jtb = JtbNew(StrNew(name), size, Make<Bbl>(def_bbl));
  for (int i = 0; i < num_entries; ++i) {
    JtbJenAdd(jtb, JenNew(entries[i].pos, Make<Bbl>(entries[i].bbl)));
  }
  return jtb.value;
}

extern "C" CW_Reg CW_RegNew(CW_DK kind, const char* name) {
  return RegNew(DK(kind), StrNew(name)).value;
}

/* create unsigned int constant - must be of kind Ux */
extern "C" CW_Const CW_ConstNewU(CW_DK kind, uint64_t value) {
  return ConstNewU(DK(kind), value).value;
}

/* create unsigned int constant - must be of kind Sx, Ax  or Cx */
extern "C" CW_Const CW_ConstNewS(CW_DK kind, int64_t value) {
  return ConstNewACS(DK(kind), value).value;
}

/* create unsigned int constant - must be of kind Fx */
extern "C" CW_Const ConstNewF(CW_DK kind, double value) {
  return ConstNewF(DK(kind), value).value;
}

extern "C" CW_Ins CW_InsNew0(CW_OPC opc) { return InsNew(OPC(opc)).value; }

extern "C" CW_Ins CW_InsNew1(CW_OPC opc, CW_Handle op1) {
  return InsNew(OPC(opc), Handle(op1)).value;
}

extern "C" CW_Ins CW_InsNew2(CW_OPC opc, CW_Handle op1, CW_Handle op2) {
  return InsNew(OPC(opc), Handle(op1), Handle(op2)).value;
}

extern "C" CW_Ins CW_InsNew3(CW_OPC opc, CW_Handle op1, CW_Handle op2,
                             CW_Handle op3) {
  return InsNew(OPC(opc), Handle(op1), Handle(op2), Handle(op3)).value;
}

extern "C" CW_Ins CW_InsNew4(CW_OPC opc, CW_Handle op1, CW_Handle op2,
                             CW_Handle op3, CW_Handle op4) {
  return InsNew(OPC(opc), Handle(op1), Handle(op2), Handle(op3), Handle(op4))
      .value;
}

extern "C" CW_Ins CW_InsNew5(CW_OPC opc, CW_Handle op1, CW_Handle op2,
                             CW_Handle op3, CW_Handle op4, CW_Handle op5) {
  return InsNew(OPC(opc), Handle(op1), Handle(op2), Handle(op3), Handle(op4),
                Handle(op4))
      .value;
}

extern "C" CW_Stk CW_StkNew(const char* name, uint32_t alignment,
                            uint32_t size) {
  return StkNew(StrNew(name), alignment, size).value;
}

extern "C" CW_Bbl CW_BblNew(const char* name) {
  return BblNew(StrNew(name)).value;
}

extern "C" CW_Fun CW_FunNew(const char* name, enum CW_FUN_KIND kind,
                            int num_out_args, const enum CW_DK out_args[],
                            int num_in_args, const enum CW_DK in_args[]) {
  Fun fun = FunNew(StrNew(name), FUN_KIND(kind));
  FunNumOutputTypes(fun) = num_out_args;
  for (int i = 0; i < num_out_args; ++i) {
    FunOutputTypes(fun)[i] = DK(out_args[i]);
  }
  FunNumInputTypes(fun) = num_in_args;
  for (int i = 0; i < num_in_args; ++i) {
    FunInputTypes(fun)[i] = DK(in_args[i]);
  }
  return fun.value;
}

extern "C" CW_Unit CW_UnitNew(const char* name) {
  return UnitNew(StrNew(name)).value;
}

extern "C" CW_Data CW_DataNewBytes(uint32_t num_bytes, const char bytes[],
                                   int repeat) {
  Str str = StrNew(std::string_view{bytes, num_bytes});
  return DataNew(str, num_bytes, repeat).value;
}

extern "C" CW_Data CW_DataNewMem(uint32_t num_bytes, CW_Mem mem) {
  return DataNew(Make<Mem>(mem), num_bytes, 0).value;
}

extern "C" CW_Data CW_DataNewFun(uint32_t num_bytes, CW_Fun fun) {
  return DataNew(Make<Fun>(fun), num_bytes, 0).value;
}

extern "C" CW_Mem CW_MemNew(const char* name, enum CW_MEM_KIND kind,
                            uint32_t alignment) {
  return MemNew(StrNew(name), MEM_KIND(kind), alignment).value;
}

/* ============================================================ */
/* Linkers */
/* ============================================================ */

extern "C" CW_Data CW_MemDataAdd(CW_Mem mem, CW_Data data) {
  MemDataAdd(Make<Mem>(mem), Make<Data>(data));
  return data;
}

extern "C" CW_Mem CW_UnitMemAdd(CW_Unit unit, CW_Mem mem) {
  UnitMemAdd(Make<Unit>(unit), Make<Mem>(mem));
  return mem;
}

extern "C" CW_Fun CW_UnitFunAdd(CW_Unit unit, CW_Fun fun) {
  UnitFunAdd(Make<Unit>(unit), Make<Fun>(fun));
  return fun;
}

extern "C" CW_Bbl CW_FunBblAdd(CW_Fun fun, CW_Bbl bbl) {
  FunBblAdd(Make<Fun>(fun), Make<Bbl>(bbl));
  return bbl;
}

extern "C" CW_Ins CW_BblInsAdd(CW_Bbl bbl, CW_Ins ins) {
  BblInsAdd(Make<Bbl>(bbl), Make<Ins>(ins));
  return ins;
}

extern "C" CW_Reg CW_FunRegAdd(CW_Fun fun, CW_Reg reg) { return reg; }

extern "C" CW_Jtb CW_FunJtbAdd(CW_Fun fun, CW_Jtb jtb) {
  FunJtbAdd(Make<Fun>(fun), Make<Jtb>(jtb));
  return jtb;
}

extern "C" CW_Stk CW_FunStkAdd(CW_Fun fun, CW_Stk stk) {
  FunStkAdd(Make<Fun>(fun), Make<Stk>(stk));
  return stk;
}

/* ============================================================ */
/* Misc */
/* ============================================================ */

extern "C" char* CW_UnitDump(CW_Unit unit) {
  std::ostringstream ss;
  UnitRenderToAsm(Make<Unit>(unit), &ss);
  char* buf = (char*)malloc(1 + ss.str().size());
  strcpy(buf, ss.str().c_str());
  return buf;
}

extern "C" int CW_UnitAppendFromAsm(CW_Unit unit, const char* buf) {
    return UnitAppendFromAsm(Make<Unit>(unit), buf, {});
}

extern "C" void CW_Init(uint32_t stripe_multiplier) {
    InitStripes(stripe_multiplier);
}