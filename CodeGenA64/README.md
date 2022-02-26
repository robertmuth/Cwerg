# A64 (aka ARM64/AArch64) Backend

The backend has the same structure at [A32 Backend](../CodeGenA32).

It also uses the same approach to [Instruction Selection](../Docs/instruction_selection.md)
which is a straight forward expansion of the IR opcodes into zero or more A64 opcodes.

[isel_tab.py](isel_tab.py) contains the necessary tables which 
are also use to generate C++ code.


## Code Generation Phases

Code generation goes through the following phases which 
massage the IR until it becomes almost trivial to generate
A64 code from it.

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
* widening most integer operands to 32 or 64bit. This allows us to keep the instruction 
  selector simple as it does not have to support 8 and 16 bit integers.
* add unconditional branches and invert conditional branches to linearize the CFG
  this may undo the canonicalization occasionally
* deal with out of range immediates:
  replace all const operands not supported by ISA with regs that
  received the immediate via a `mov` (see `InsArm32RewriteOutOfBoundsImmediates`)
  This is done by using the instruction selector to find the best expansion match and
  then check if the integers immediates satisfies the constraints of the expansion.
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
* add `nop1` for those case where we likely need a scratch register 
* Allocate registers for local registers.  
* Eliminate `mov`s where CPU registers of the `src` and `dst` operands are identical 

## Comparing against gcc's instruction selector

https://godbolt.org/  (use ARM64 gcc or armv8-clang with flags `-O3 -ffast-math`) 

```
aarch64-linux-gnu-gcc test.c -c -O3  -o test.o ; aarch64-linux-gnu-objdump -D test.o
```

To convert from the hex code reported by objdump to the Cwerg A64 instruction run:
```
../CpuA64/disassembler_tool.py <32 bit hex code>
```
