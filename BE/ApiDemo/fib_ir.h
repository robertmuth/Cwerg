//  .fun fibonacci NORMAL [U32] = [U32]
//      .reg U32 [x in out]
//
//  .bbl start
//      poparg in
//      blt 1:U32 in difficult
//      pusharg in
//      ret
//
//  .bbl difficult
//      mov out = 0
//      sub x = in 1
//
//      pusharg x
//      bsr fibonacci
//      poparg x
//
//      add out = out x
//      sub x = in 2
//
//      pusharg x
//      bsr fibonacci
//      poparg x
//
//      add out = out x
//      pusharg out
//      ret

// Create a Unit with a single function "fib" modelled after ../TestData/fib.asm
base::Unit MakeFibonacci() {
    using namespace cwerg::base;

    Unit unit = UnitNew(StrNew("fibonacci"));
    Fun fun = UnitFunAdd(unit, FunNew(StrNew("fib"), FUN_KIND::NORMAL));
    // setup function signature
    FunOutputTypes(fun)[0] = DK::U32;
    FunNumOutputTypes(fun) = 1;
    FunInputTypes(fun)[0] = DK::U32;
    FunNumInputTypes(fun) = 1;
    Bbl bbl_start = FunBblAdd(fun, BblNew(StrNew("start")));
    Bbl bbl_difficult = FunBblAdd(fun, BblNew(StrNew("difficult")));
    Reg reg_in = FunRegAdd(fun, RegNew(DK::U32, StrNew("in")));
    Reg reg_out = FunRegAdd(fun, RegNew(DK::U32, StrNew("out")));
    Reg reg_x = FunRegAdd(fun, RegNew(DK::U32, StrNew("x")));
    Const zero = ConstNewU(DK::U32, 0);
    Const one = ConstNewU(DK::U32, 1);
    Const two = ConstNewU(DK::U32, 2);
    // populate Bbl start
    BblInsAdd(bbl_start, InsNew(OPC::POPARG, reg_in));
    BblInsAdd(bbl_start, InsNew(OPC::BLT, one, reg_in, bbl_difficult));
    BblInsAdd(bbl_start, InsNew(OPC::PUSHARG, reg_in));
    BblInsAdd(bbl_start, InsNew(OPC::RET));
    // populate Bbl difficult
    BblInsAdd(bbl_difficult, InsNew(OPC::MOV, reg_out, zero));
    BblInsAdd(bbl_difficult, InsNew(OPC::SUB, reg_x, reg_in, one));
    BblInsAdd(bbl_difficult, InsNew(OPC::PUSHARG, reg_x));
    BblInsAdd(bbl_difficult, InsNew(OPC::BSR, fun));
    BblInsAdd(bbl_difficult, InsNew(OPC::POPARG, reg_x));
    BblInsAdd(bbl_difficult, InsNew(OPC::ADD, reg_out, reg_out, reg_x));
    BblInsAdd(bbl_difficult, InsNew(OPC::SUB, reg_x, reg_in, two));
    BblInsAdd(bbl_difficult, InsNew(OPC::PUSHARG, reg_x));
    BblInsAdd(bbl_difficult, InsNew(OPC::BSR, fun));
    BblInsAdd(bbl_difficult, InsNew(OPC::POPARG, reg_x));
    BblInsAdd(bbl_difficult, InsNew(OPC::ADD, reg_out, reg_out, reg_x));
    BblInsAdd(bbl_difficult, InsNew(OPC::PUSHARG, reg_out));
    BblInsAdd(bbl_difficult, InsNew(OPC::RET));

    return unit;
}
