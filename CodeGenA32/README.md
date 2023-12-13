# A32 (aka ARM32) Backend

This directory contains the A32 backend which targets ISA ARMv6T2 and above.
Additionally, support for the following instructions is required:
* idiva idivt 
* movw, movt
* vfpv3 instructions

In terms of gcc compiler flags this approximately correspods to: `-marm -march=armv7ve+fp `

Many SOCs, including the Raspberry Pi 3 and 4, satisfy these requirements.

Supporting Thumb(2) is an explicit non-goal.

64bit integer data type (S64, U64) are not supported. 

## Code Generation Phases

Code generation goes through the following phases which 
massage the IR until it becomes almost trivial to generate
A32 code from it.

### Legalization

This phase rewrites the IR so the all remaining IR instructions are covered by the 
instruction selector. It encompasses the following steps:

* replacement of `push`/`pop` instruction with `mov`s to and from CPU registers as
  required by the calling convention.
* eliminate addressing modes not supported by ISA, e.g. 
  - convert `ld.stk`/`st.stk`/`lea.stk` with reg offset to 
    `lea.stk` + `ld`/`st`/`lea`
  - convert `ld.mem`/`st.mem` to  
    `lea.mem` +`ld`/`st`
* rewriting of opcodes not directly supported by ISA, e.g. `mod`
* widening most integer operands to 32bit. This allows us to keep the instruction 
  selector simple as it does not have to support 8 and 16 bit integers.
* canonicalizing instruction to help with the next step
* add unconditional branches and invert conditional branches to linearize the CFG
  this may undo the canonicalization occasionally
* deal with out of range immediates:
  replace all const operands not supported by ISA with regs that
  received the immediate via a `mov` (see `InsArm32RewriteOutOfBoundsImmediates`)
  This is done by using the instruction selector to find the best expansion match and
  then check if the integers immediates satisfies the constraints of the expansion.
* add `nop1` for those case where we likely need a scratch register 
* enforce Cwerg shift semantics
* TODO: move parameters that cannot be handled by calling convention
  onto stk 

### Global Register Allocation

This phase assigns CPU registers to all global IR registers, so that afterwards all global IR registers have either been assigned a CPU register or have been spilled. The spilling is
done explicitly in the IR via `ld.stk`/`st.stk`.

###  Stack Finalization And Fixed Register Assignment

This phase will assign CPU register to all the remaining (local) registers 

* rename all local IR registers so that there is only on definition per register 
  similar to SSA form. We do this a Bbl at a time since all registers are local
  and hence do not need phi nodes. 
* compute offsets of stack objects
* Allocate registers for local registers.  
* Eliminate `mov`s where CPU registers of the `src` and `dst` operands are identical 

### Code Selection

The code selection is a straight forward expansion of
the IR opcodes into zero or more A32 opcodes described in
[instruction_selection.md](../Docs/instruction_selection.md)

[isel_tab.py](isel_tab.py) contains the necessary tables which 
are also use to generate C++ code.

Only the `ret` instructions is handled manually and will be expanded 
into the function epilog code sequence.

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

## Comparing against gcc's instruction selector

https://godbolt.org/  (use ARM gcc or armv7-a clang with flags `-O3 -ffast-math  -marm -march=armv7ve`) 

```
arm-linux-gnueabihf-gcc  test.c -c -O3 -marm -march=armv7ve -o test.o ; arm-linux-gnueabihf-objdump -D test.o
```

To convert from the hex code reported by objdump to the Cwerg A32 instruction run:
```
../CpuA32/disassembler_tool.py <32 bit hex code>
```
