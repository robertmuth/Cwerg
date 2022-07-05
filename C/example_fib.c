#include "C/cwerg.h"

const enum CW_DK args[] = {CW_U32};

CW_Unit MakeFibonacci() {
  CW_Unit unit = CW_UnitNew("fibonacci");
  CW_Fun fun = CW_UnitFunAdd(
      unit, CW_FunNew("fib", CW_FUN_KIND_NORMAL, 1, args, 1, args));

  CW_Bbl bbl_start = CW_FunBblAdd(fun, CW_BblNew("start"));
  CW_Bbl bbl_difficult = CW_FunBblAdd(fun, CW_BblNew("difficult"));
  CW_Reg reg_in = CW_FunRegAdd(fun, CW_RegNew(CW_U32, "in"));
  CW_Reg reg_out = CW_FunRegAdd(fun, CW_RegNew(CW_U32, "out"));
  CW_Reg reg_x = CW_FunRegAdd(fun, CW_RegNew(CW_U32, "x"));
  CW_Const zero = CW_ConstNewU(CW_U32, 0);
  CW_Const one = CW_ConstNewU(CW_U32, 1);
  CW_Const two = CW_ConstNewU(CW_U32, 2);
  // populate Bbl start
  CW_BblInsAdd(bbl_start, CW_InsNew1(CW_POPARG, reg_in));
  CW_BblInsAdd(bbl_start, CW_InsNew3(CW_BLT, one, reg_in, bbl_difficult));
  CW_BblInsAdd(bbl_start, CW_InsNew1(CW_PUSHARG, reg_in));
  CW_BblInsAdd(bbl_start, CW_InsNew0(CW_RET));
  // populate Bbl difficult
  CW_BblInsAdd(bbl_difficult, CW_InsNew2(CW_MOV, reg_out, zero));
  CW_BblInsAdd(bbl_difficult, CW_InsNew3(CW_SUB, reg_x, reg_in, one));
  CW_BblInsAdd(bbl_difficult, CW_InsNew1(CW_PUSHARG, reg_x));
  CW_BblInsAdd(bbl_difficult, CW_InsNew1(CW_BSR, fun));
  CW_BblInsAdd(bbl_difficult, CW_InsNew1(CW_POPARG, reg_x));
  CW_BblInsAdd(bbl_difficult, CW_InsNew3(CW_ADD, reg_out, reg_out, reg_x));
  CW_BblInsAdd(bbl_difficult, CW_InsNew3(CW_SUB, reg_x, reg_in, two));
  CW_BblInsAdd(bbl_difficult, CW_InsNew1(CW_PUSHARG, reg_x));
  CW_BblInsAdd(bbl_difficult, CW_InsNew1(CW_BSR, fun));
  CW_BblInsAdd(bbl_difficult, CW_InsNew1(CW_POPARG, reg_x));
  CW_BblInsAdd(bbl_difficult, CW_InsNew3(CW_ADD, reg_out, reg_out, reg_x));
  CW_BblInsAdd(bbl_difficult, CW_InsNew1(CW_PUSHARG, reg_out));
  CW_BblInsAdd(bbl_difficult, CW_InsNew0(CW_RET));
  return unit;
}

int main() {
  CW_InitStripes(4);

  CW_Unit unit = MakeFibonacci();
  CW_UnitDump(unit);
  return 0;
}