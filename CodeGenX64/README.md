# X64 (aka x86-64) Backend

We follow the model of the A32/A64 backends of a simple expansion of Cwerg
instruction to x86-64 instruction.

Since x86-64 is essentially a two address ISA some legalization work is necessary
to convert from Cwerg's three address code.

Limitations:

* avoid  3now, mmx or x87 instructions 
* floating point handled via SSE xmmX registers 
* expect certain instruction set extensions: SSE, lzcnt, tzcnt, popcnt, ...

Eventually, the intention is to target CPUs Haswell or later.
In terms of gcc compiler flags this correspods to: `-march=haswell`

## Code Generation Phases

Code generation goes through the following phases which 
massage the IR until it becomes almost trivial to generate
X64 code from it.

### Legalization

This phase rewrites the IR so the all remaining IR instructions are covered by the 
instruction selector.

The major differences to the A32 and A64 backends are:
* no operand widening is performed as the code selector supports all widths 
* X86-64 is resembling 2 address code rather than Cwerg's 3 addresss code requiring
  a special processing descrined further down.

 Legalization encompasses the following steps:


* replacement of `push`/`pop` instruction with `mov`s to and from CPU registers as
  required by the calling convention.
* eliminate addressing modes not supported by ISA, e.g. 
  - convert `ld.stk`/`st.stk`/`lea.stk` with reg offset to 
    `lea.stk` + `ld`/`st`/`lea`
  - convert `ld.mem`/`st.mem` to  
    `lea.mem` +`ld`/`st`
* rewriting of opcodes not directly supported by ISA or the  instruction selector, e.g. `copysign`, `cmpXX`
* other special rewriting for `div`, `mod` and shifts. Note that this may introduce uses
  of CPU regs `rcx` and `rdx`.
* deal with out of range immediates
* 3-address code to 2-address code conversion
* TODO: move parameters that cannot be handled by calling convention
  onto stk 

#### 3-Address Code to 2-Address Code Conversion

Most x86 instructions for binary ops come in the following variants:

* `ins-x86` `mem_or_regA` `regB` (MR)

   (3 op equivalent: `ins-x86` `mem_or_regA` `mem_or_regA` `regB`)
* `ins-x86` `regA` `mem_or_regB` (RM) 

   (3 op equivalent `ins-x86` `regA` `regA` `mem_or_regB`)
* `ins-x86` `mem_or_regA` `imm` (MI)

   (3 op equivalent `ins-x86` `mem_or_regA` `mem_or_regA` `imm`)
      
Because memory operands can be directly encoded, spilled registers do not
always need to be explicitly rewritten before instruction selection.
However, we will need to reserve registers for some of the rewrites - currently `rax` and `xmm0`.

However we do need to rewrite the three address Cwerg instructions 
to match one of the two x86 patterns from below: 

1. `regA` `regA` `imm` 
2. `regA` `regA` `regB`  (or `regA` `regA` `regA` )

This is accomplished by first rewriting instructions so that there is at most one 
immediate which must be in the last slot and then applying the following
expansions: 


1. `<ins>` `regA` `regB` `regC` => rewrite

   `mov` `regA` `regB`; `<ins>` `regA` `regA` `regC`
   
2. `<ins>` `regA` `regB` `imm` => rewrite

   `mov` `regA` `regB`;  `<ins>` `regA` `regA` `imm`

3. `<ins>` `regA` `regB` `regA` => rewrite (with tmp reg)

   `mov` `tmp` `regB`; `<ins>` `tmp` `tmp` `regA`; `mov` `regA` `tmp`
    
   (For commutative ops a simpler rewrite is to just swap the last two operands.)
    
4. `<ins>` `regA` `regB` `regB` => rewrite

    `mov` `regA` `regB`; `<ins>` `regA` `regB` 



### Global Register Allocation

This phase assigns CPU registers to all global IR registers, so that afterwards all global IR registers have either been assigned a CPU register or have been spilled.

Unlike the A32/A64 backends, the spilling is done implicitly by using `StackSlot` objects
in lieu of CPU registers. The reason for this is that most X64-64 instruction support one memory operand which can be uses to access the stack.
This implies that the code selector distinguishes between spilled and regular
registers.

###  Stack Finalization And Fixed Register Assignment

This phase will assign CPU register to all the remaining (local) registers 

* compute offsets of stack objects
* add `nop1` for those case where we likely need a scratch register 
* Allocate registers for local registers.  
* Eliminate `mov`s where CPU registers of the `src` and `dst` operands are identical 

Just like with Global Register Allocation, the registers are spilled by assigning them
a `StackSlot.

### Instruction expansion (integers)

After register allocation a Cwerg register, `regX`, will either be assigned
to an x86-64 register, in which case we keep referring to it as `regX`, 
or it will be spilled, in which case we refer to it as `spillX`.


The patterns below show how to translate Cwerg three address instruction to
x86-64 instruction variants.


* `<ins>` `regA` `regA` `imm` => direct expansion (MI)
* `<ins>` `spillA` `spillA` `imm` => direct expansion (MI)
* `<ins>` `regA` `regA` `regA` => direct expansion (RM) or (MR)
* `<ins>` `regA` `regA` `regB` => direct expansion (RM) or (MR)
* `<ins>` `regA` `regA` `spillB` => direct expansion (RM)
* `<ins>` `spillA` `spillA` `regB` => direct expansion (MR)
* `<ins>` `spillA` `spillA` `spillB` => complex expansion (with tmp reg)
 
   `mov-x86` `tmp` `spillB`; `ins-x86` `spillA` `tmp` (MR)


This is all straight forward except for the case where all operands have been spilled.
To obtain the tmp scratch register we may need to reserve one general and one 
floating point register.

Note, the situation where two operands are spilled also occurs for `mov` and unary
instructions.

### Instruction expansion (FP)

For floating point operations only the RM variant is available. So we
get the following expansions (omitting the cases involving immediates):


* `<ins>` `regA` `regA` `regA` => direct expansion (RM)
* `<ins>` `regA` `regA` `regB` => direct expansion (RM) 
* `<ins>` `regA` `regA` `spillB` => direct expansion (RM)
* `<ins>` `spillA` `spillA` `regB` =>  complex expansion (with tmp reg)

  `mov-x86` `tmp` `spillA`; `ins-x86` `tmp` `regB` ; `mov-x86` `spillA` `tmp` (RM)
* `<ins>` `spillA` `spillA` `spillB` => complex expansion (with tmp reg)

  `mov-x86` `tmp` `spillA`; `ins-x86` `tmp` `spillB`; `mov-x86` `spillA` `tmp` (RM)


### Calling Convention (inspired by System-V ABI)

scratch: `rdi` `rsi` `rdx` `rcx` `r8` `r9` `r10` `r11` `rax` `xmm0-xmm7`
         
Callee save:  `rbx` `rbp` `r12-15` `rsp` `xmm8-xmm15`

params-in: `rdi` `rsi` `rdx` `rcx` `r8` `r9` 

params-out: `rax` `rdx`

syscalls: `rdi` `rsi` `rdx` `r10` `r8` `r9` -> `rax` 
           (note: `r10` takes the place of `rcx` )    

### Misc other Highlights

* instruction selection is somewhat simplified as most immediates can be encoded 
  directly without size restrictions in particular memory offsets can be up to 32 bit.
  
* Once we have rewritten instructions to AAB form we have to be careful with subsequent optimizations 
  
* some instructions (div/mul/shl/shr/asr) use implicit registers we handle these by adding 
  move instructions with fixed CpuRegs during legalization, e.g.
  ```
  div a b c 
  ```
  becomes
  ```
  mov RAX@rax b
  div RDX@rdx RAX@rax c  # hack: should really be div RAX@rax RAX@rax c 
  mov a RAX
  ```  
  the hack is working in conjunction with instruction selection.
  
* Spilled registers are handled directly by instruction selection so no rewrite as in the
  a64/a64 backends is necessary

* Instruction selection is handling all data kinds (DK) so no widening step as in the a32/a64 
  backends is necessary. On the flip-side, the instruction selection tables are rather large. 
