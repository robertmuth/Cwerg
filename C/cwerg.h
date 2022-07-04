#ifndef CWERG_H
#define CWERG_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t Handle; /* represent any of the typedefs below */
typedef uint32_t Reg;    /* virtual register */
typedef uint32_t Const;  /* concrete value that maybe stored in a register */
typedef uint32_t Stk;    /* stack slot */
typedef uint32_t Ins;    /* instruction */
typedef uint32_t Bbl;    /* basic block */
typedef uint32_t Fun;    /* function */
typedef uint32_t Unit;   /* top level container for translation unit */

typedef uint32_t Jtb;  /* jump table */
typedef uint32_t Mem;  /* named/addressable block of global memory */
typedef uint32_t Data; /* Data Slice inside a Mem */
typedef uint32_t Stk;  /* Stack slot */

struct JtbEntry {
  uint32_t pos;  // must be positive - value of case statement */
  Bbl bbl;       // target of case statement */
};

/* @AUTOGEN-START@ */
enum OPC {
    INVALID = 0x00,

    ADD = 0x10,
    SUB = 0x11,
    MUL = 0x12,
    DIV = 0x13,
    XOR = 0x18,
    AND = 0x19,
    OR = 0x1a,
    SHL = 0x1b,
    SHR = 0x1c,
    REM = 0x1d,
    CLMUL = 0x1e,

    BEQ = 0x20,
    BNE = 0x21,
    BLT = 0x22,
    BLE = 0x23,
    SWITCH = 0x28,
    BRA = 0x29,
    RET = 0x2a,
    BSR = 0x2b,
    JSR = 0x2c,
    SYSCALL = 0x2d,
    TRAP = 0x2e,

    PUSHARG = 0x30,
    POPARG = 0x31,
    CONV = 0x32,
    BITCAST = 0x33,
    MOV = 0x34,
    CMPEQ = 0x35,
    CMPLT = 0x36,
    LEA = 0x38,
    LEA_MEM = 0x39,
    LEA_STK = 0x3a,
    LEA_FUN = 0x3b,

    LD = 0x40,
    LD_MEM = 0x41,
    LD_STK = 0x42,
    ST = 0x44,
    ST_MEM = 0x45,
    ST_STK = 0x46,
    CAS = 0x48,
    CAS_MEM = 0x49,
    CAS_STK = 0x4a,

    CEIL = 0x50,
    FLOOR = 0x51,
    ROUND = 0x52,
    TRUNC = 0x53,
    COPYSIGN = 0x54,
    SQRT = 0x55,

    CNTLZ = 0x60,
    CNTTZ = 0x61,
    CNTPOP = 0x62,

    NOP = 0x70,
    NOP1 = 0x71,
    INLINE = 0x78,
    GETFP = 0x79,
    GETSP = 0x7a,
    GETTP = 0x7b,

    DIR_MEM = 0x01,
    DIR_DATA = 0x02,
    DIR_ADDR_FUN = 0x03,
    DIR_ADDR_MEM = 0x04,
    DIR_FUN = 0x05,
    DIR_BBL = 0x06,
    DIR_REG = 0x07,
    DIR_STK = 0x08,
    DIR_JTB = 0x09,
};

enum FUN_KIND {
    INVALID = 0,
    BUILTIN = 1,
    EXTERN = 2,
    NORMAL = 3,
    SIGNATURE = 4,
};

enum MEM_KIND {
    INVALID = 0,
    RO = 1,
    RW = 2,
    TLS = 3,
    FIX = 4,
    EXTERN = 5,
    BUILTIN = 6,
};

enum DK {
    INVALID = 0,
    S8 = 16,
    S16 = 17,
    S32 = 18,
    S64 = 19,
    U8 = 32,
    U16 = 33,
    U32 = 34,
    U64 = 35,
    F8 = 48,
    F16 = 49,
    F32 = 50,
    F64 = 51,
    A32 = 66,
    A64 = 67,
    C32 = 82,
    C64 = 83,
};
/* @AUTOGEN-END@ */



/* ============================================================ */
/* constructors */
/* ============================================================ */
Jtb JtbNew(const char* name, uint32_t size, Bbl def_bbl, int num_entries,
           const JtbEntry entries[]);

Reg RegNew(DK kind, const char* name);

/* create unsigned int constant - must be of kind Ux */
Const ConstNewU(DK kind, uint64_t value);

/* create unsigned int constant - must be of kind Sx, Ax  or Cx */
Const ConstNewS(DK kind, int64_t value);

/* create unsigned int constant - must be of kind Fx */
Const ConstNewF(DK kind, double value);

Ins InsNew0(OPC opc);
Ins InsNew1(OPC opc, Handle op1);
Ins InsNew2(OPC opc, Handle op1, Handle op2);
Ins InsNew3(OPC opc, Handle op1, Handle op2, Handle op3);
Ins InsNew4(OPC opc, Handle op1, Handle op2, Handle op3, Handle op4);
Ins InsNew5(OPC opc, Handle op1, Handle op2, Handle op3, Handle op4,
            Handle op5);

Stk StkNew(const char* const, uint32_t alignment, uint32_t size);

Bbl BblNew(const char* name);
Fun FunNew(const char* name, FUN_KIND kind, int num_out_args, DK out_args[],
           int num_in_args, DK in_argsp[]);
Unit UnitNew(const char* name);

/* Add raw bytes to Mem */
Data DataNewBytes(int num_bytes, const char* bytes, int repeat);
  /* store address of Mem to Mem (num_bytes should be large enough to avoid information loss) */
Data DataNewMem(int num_bytes, Mem mem);
 /* store address of Fun to Mem* (num_bytes should be large enough to avoid information loss) */
Data DataNewFun(int num_bytes, Fun fun); 

/* ============================================================ */
/* linkers */
/* ============================================================ */
Data MemDataAdd(Mem mem, Data data);

Mem UnitMemAdd(Unit unit, Mem mem);
Fun UnitFunAdd(Unit unit, Fun fun);
Bbl FunBblAdd(Fun fun, Bbl bbl);
Ins BblInsAdd(Bbl bbl, Ins ins);

Reg FunRegAdd(Fun fun, Reg reg);
Jtb FunJtbAdd(Fun, Jtb jtb);
Stk FunStkAdd(Fun, Stk stk);

/* ============================================================ */
/* */
/* ============================================================ */

#ifdef __cplusplus
}
#endif

#endif CWERG_H