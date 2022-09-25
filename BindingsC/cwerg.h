#ifndef CWERG_H
#define CWERG_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

typedef uint32_t CW_Handle; /* represent any of the typedefs below */
typedef uint32_t CW_Reg;    /* virtual register */
typedef uint32_t CW_Const;  /* concrete value that maybe stored in a register */
typedef uint32_t CW_Stk;    /* stack slot */
typedef uint32_t CW_Ins;    /* instruction */
typedef uint32_t CW_Bbl;    /* basic block */
typedef uint32_t CW_Fun;    /* function */
typedef uint32_t CW_Unit;   /* top level container for translation unit */

typedef uint32_t CW_Jtb;  /* jump table */
typedef uint32_t CW_Mem;  /* named/addressable block of global memory */
typedef uint32_t CW_Data; /* Data Slice inside a Mem */

struct CW_JtbEntry {
  uint32_t pos;  // must be positive - value of case statement */
  CW_Bbl bbl;    // target of case statement */
};

/*
CW_OPC enumerates all the available IR instructions.
For more details see:  https://github.com/robertmuth/Cwerg/blob/master/Docs/opcodes.md
*/
  
/* @AUTOGEN-START@ */
enum CW_OPC {

  CW_ADD = 0x10,
  CW_SUB = 0x11,
  CW_MUL = 0x12,
  CW_DIV = 0x13,
  CW_XOR = 0x18,
  CW_AND = 0x19,
  CW_OR = 0x1a,
  CW_SHL = 0x1b,
  CW_SHR = 0x1c,
  CW_REM = 0x1d,
  CW_CLMUL = 0x1e,

  CW_BEQ = 0x20,
  CW_BNE = 0x21,
  CW_BLT = 0x22,
  CW_BLE = 0x23,
  CW_SWITCH = 0x28,
  CW_BRA = 0x29,
  CW_RET = 0x2a,
  CW_BSR = 0x2b,
  CW_JSR = 0x2c,
  CW_SYSCALL = 0x2d,
  CW_TRAP = 0x2e,

  CW_PUSHARG = 0x30,
  CW_POPARG = 0x31,
  CW_CONV = 0x32,
  CW_BITCAST = 0x33,
  CW_MOV = 0x34,
  CW_CMPEQ = 0x35,
  CW_CMPLT = 0x36,
  CW_LEA = 0x38,
  CW_LEA_MEM = 0x39,
  CW_LEA_STK = 0x3a,
  CW_LEA_FUN = 0x3b,

  CW_LD = 0x40,
  CW_LD_MEM = 0x41,
  CW_LD_STK = 0x42,
  CW_ST = 0x44,
  CW_ST_MEM = 0x45,
  CW_ST_STK = 0x46,
  CW_CAS = 0x48,
  CW_CAS_MEM = 0x49,
  CW_CAS_STK = 0x4a,

  CW_CEIL = 0x50,
  CW_FLOOR = 0x51,
  CW_ROUND = 0x52,
  CW_TRUNC = 0x53,
  CW_COPYSIGN = 0x54,
  CW_SQRT = 0x55,

  CW_CNTLZ = 0x60,
  CW_CNTTZ = 0x61,
  CW_CNTPOP = 0x62,

  CW_NOP = 0x70,
  CW_NOP1 = 0x71,
  CW_INLINE = 0x78,
  CW_GETFP = 0x79,
  CW_GETSP = 0x7a,
  CW_GETTP = 0x7b,

};
enum CW_DK {
  CW_INVALID = 0x00,
  CW_S8 = 0x10,
  CW_S16 = 0x11,
  CW_S32 = 0x12,
  CW_S64 = 0x13,
  CW_U8 = 0x20,
  CW_U16 = 0x21,
  CW_U32 = 0x22,
  CW_U64 = 0x23,
  CW_F8 = 0x30,
  CW_F16 = 0x31,
  CW_F32 = 0x32,
  CW_F64 = 0x33,
  CW_A32 = 0x42,
  CW_A64 = 0x43,
  CW_C32 = 0x52,
  CW_C64 = 0x53,
};

enum CW_FUN_KIND {
  CW_FUN_KIND_INVALID = 0,
  CW_FUN_KIND_BUILTIN = 1,
  CW_FUN_KIND_EXTERN = 2,
  CW_FUN_KIND_NORMAL = 3,
  CW_FUN_KIND_SIGNATURE = 4,
};

enum CW_MEM_KIND {
  CW_MEM_KIND_INVALID = 0,
  CW_MEM_KIND_RO = 1,
  CW_MEM_KIND_RW = 2,
  CW_MEM_KIND_TLS = 3,
  CW_MEM_KIND_FIX = 4,
  CW_MEM_KIND_EXTERN = 5,
  CW_MEM_KIND_BUILTIN = 6,
};
/* @AUTOGEN-END@ */

/* ============================================================ */
/* constructors */
/* ============================================================ */
CW_Jtb CW_JtbNew(const char* name, uint32_t size, CW_Bbl def_bbl,
                 int num_entries, const struct CW_JtbEntry entries[]);

CW_Reg CW_RegNew(enum CW_DK kind, const char* name);

/* create unsigned int constant - must be of kind Ux */
CW_Const CW_ConstNewU(enum CW_DK kind, uint64_t value);

/* create unsigned int constant - must be of kind Sx, Ax  or Cx */
CW_Const CW_ConstNewS(enum CW_DK kind, int64_t value);

/* create floating point constant - must be of kind Fx */
CW_Const ConstNewF(enum CW_DK kind, double value);

/* create an Ins based on number of operands */
CW_Ins CW_InsNew0(enum CW_OPC opc);
CW_Ins CW_InsNew1(enum CW_OPC opc, CW_Handle op1);
CW_Ins CW_InsNew2(enum CW_OPC opc, CW_Handle op1, CW_Handle op2);
CW_Ins CW_InsNew3(enum CW_OPC opc, CW_Handle op1, CW_Handle op2, CW_Handle op3);
CW_Ins CW_InsNew4(enum CW_OPC opc, CW_Handle op1, CW_Handle op2, CW_Handle op3,
                  CW_Handle op4);
CW_Ins CW_InsNew5(enum CW_OPC opc, CW_Handle op1, CW_Handle op2, CW_Handle op3,
                  CW_Handle op4, CW_Handle op5);

CW_Stk CW_StkNew(const char* name, uint32_t alignment, uint32_t size);

CW_Bbl CW_BblNew(const char* name);
  
/* create a new function with the given signature */
CW_Fun CW_FunNew(const char* name, enum CW_FUN_KIND kind, int num_out_args,
                 const enum CW_DK out_args[], int num_in_args,
                 const enum CW_DK in_args[]);
  
CW_Unit CW_UnitNew(const char* name);

/* Add raw bytes to Mem */
CW_Data CW_DataNewBytes(uint32_t num_bytes, const char* bytes, int repeat);
  
/* store address of Mem to Mem (num_bytes should be large enough to avoid
 * information loss) */
CW_Data CW_DataNewMem(uint32_t num_bytes, CW_Mem mem);
  
/* store address of Fun to Mem* (num_bytes should be large enough to avoid
 * information loss) */
CW_Data CW_DataNewFun(uint32_t num_bytes, CW_Fun fun);

CW_Mem CW_MemNew(const char* name, enum CW_MEM_KIND kind, uint32_t alignment);
/* ============================================================ */
/* linkers */
/* ============================================================ */
/* Add a Data item to the end of a Mem */ 
CW_Data CW_MemDataAdd(CW_Mem mem, CW_Data data);

CW_Mem CW_UnitMemAdd(CW_Unit unit, CW_Mem mem);

/* Add a Fun to the end of a Unit */ 
CW_Fun CW_UnitFunAdd(CW_Unit unit, CW_Fun fun);
CW_Bbl CW_FunBblAdd(CW_Fun fun, CW_Bbl bbl);
CW_Ins CW_BblInsAdd(CW_Bbl bbl, CW_Ins ins);

CW_Reg CW_FunRegAdd(CW_Fun fun, CW_Reg reg);
CW_Jtb CW_FunJtbAdd(CW_Fun fun, CW_Jtb jtb);
CW_Stk CW_FunStkAdd(CW_Fun fun, CW_Stk stk);

/* ============================================================ */
/* */
/* ============================================================ */
void CW_Init(uint32_t stripe_multiplier);

char* CW_UnitDump(CW_Unit unit);

int CW_UnitAppendFromAsm(CW_Unit unit, const char* buf);

#ifdef __cplusplus
}
#endif

#endif /* CWERG_H */
