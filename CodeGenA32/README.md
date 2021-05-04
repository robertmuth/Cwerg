# A32 (aka ARM32) Backend

This directory contains the A32 backend which targets ISA ARMv6T2 and above.
Additionally, support for the following instructions is required:
* idiva idivt 
* movw, movt
* vfpv3 instructions

Many SOCs, including the Raspberry Pi 3 and 4, satisfy these requirements.

Supporting Thumb(2) is an explicit non-goal.

## Code Generation Stages


Code generation goes through the following stages which 
massages the IR until it becomes almost trivial to generate
A32 code from it.

### Legalization 

* eliminate addressing modes not supported by ISA, e.g. 
  `ld.stk`/`st.stk`/`lea.stk` with reg offset
* rewrite opcodes not directly supported by ISA, e.g. `mod`
* widen most operands to 32bit
* move parameters that cannot be handled by calling convention
  onto stk

### Global Register Allocation

TODO: add this

###  Stack Finalization And Fixed Register Assignment

* compute offsets of stack objects
* convert `ld.stk`/`st.stk`/`lea.stk` to `ld`/`st`/`lea` by introducing
  the `sp`  machine register
* convert `pusharg`/`poparg` to `mov`s by introducing machine registers
  as per calling convention
* run basic optimizations (mostly to help with `mov` elimination)

### Misc + Eliminate Unsupported Immediates  

* convert `ld.mem`/`st.mem` to  `lea.mem` +`ld`/`st`
* replace all const operands not supported by ISA with regs that
  received the immediate via a `mov`
  (see `InsArm32RewriteOutOfBoundsImmediates`)

* add unconditional branches

### Register Allocation 

* insert special `nop1` opcodes where needed so that the register allocator
  can set aside a register
* TODO: explain how global register are dealt with
* Allocate registers for local registers  
* `mov` elimination pass

### Code Selection

The code selection is a straight forward expansion of
the IR opcodes into zero or more A32 opcodes (see [isel_tab.py])

All the expansion patterns can be listed using `./isel_tab.py`:
```
blt [BBL REG_OR_CONST REG_OR_CONST]       # IR opcode to expand (with operand kinds)
  [* U32 U32]                             #   pattern 1 (with constraints on the IR operands): 2 reg case
    cmp [ARG.reg1 SHIFT.lsl ARG.reg2 0]   #     1. A32 instruction of the expansion
    b [PRED.cc ARG.bbl0]                  #     2. A32 instriction of the expansion
  [* U32 pos_8_bits_shifted]              #   pattern 2: 1 reg, 1 immediate case
    cmp [ARG.reg1 ARG.num2]               #     1. A32 instruction of the expansion
    b [PRED.cc ARG.bbl0]                  #     2. A32 instruction of the expansion
  [* S32 S32]                             #   pattern 3: 2 regs case (signed)
    cmp [ARG.reg1 SHIFT.lsl ARG.reg2 0]   #     1. A32 instruction of the expansion
    b [PRED.lt ARG.bbl0]                  #     2. A32 instruction of the expansion
  ...
```

If the expansion requires a scratch register, the register allocator
will be told to reserve on via the insertion of a `nop1` IR opcode.

To test the code selection run `make isel_test`.

This simplistic approach to code selection leaves some opportunities on the table, e.g.:

* combining ALU opcodes with shifts of their source operands
* combining loads/stores with shifts of their offsets
* combining loads/store with updates of the base
* combining loads with (sign) extension of the loaded value

TODO: To improve code quality the simplistic code selection should be

* replaced by either a xBURG style code selector or
* augmented by a peephole pass over the A32 code.

This should eliminate many of sign-extension ops introduced by the widening step.


## Calling Convention

A modified version of the standard calling convention is used
where registers r0-r5 are available for arguments and returns:

* r15 pc
* r14/lr link register
* r13/sp stack pointer
* r12/ip scratch register
* r6 - r11: gpr callee save - must be preserved across call
* r0 - r5: gpr in/out (argument/return) regs
* s16 - s31  (d8-d15): vfp  callee save - must be preserved across call
* s0 - s15  (d0-d7): vfp in/out (argument/return) regs

When there are more parameters than fit in the argument
registers, r5 becomes a pointer to a memory area containing
the extra arguments. This keeps the stack layout simple.


## Constant Pools

Initially we will side step dealing with constant pools 
by using movw/movt pairs for materializing 32bit constants.

floating point constants are stored in global memory.

## Jump Tables

Until we have constant pools, jump tables will NOT be interleaved with code and initially consist
of 32bit absolute code addresses.


## Branch Offsets

Both subroutine calls and regular branches have and offset range of +/-32MiB 
which should be enough to not worry about overflows initially. 
(For reference X86-64 chrome has a 120MB .text section).



