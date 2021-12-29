# X64 (aka x86-64) Backend

We follow the model of the A32/A64 backend of a simple expansion of Cwerg
instruction to x86-64 instruction.
Since x86-64 is essentially a two address ISA some legalization work is necessary
to convert from Cwerg's three address code.

Limitations:

* avoid  3now, mmx or x87 instructions 
* floating point handled via SSE xmmX registers 
* expect certain instruction set extensions: SSE, lzcnt, tzcnt, ...

## Legalization

Most x86 instructions for binary ops come in the following variants:

* `ins-x86` `mem_or_regA` `regB` (MR)

   (3 op equivalent: `ins-x86` `mem_or_regA` `mem_or_regA` `regB`)
* `ins-x86` `regA` `mem_or_regB` (RM) 

   (3 op equivalent `ins-x86` `regA` `regA` `mem_or_regB`)
* `ins-x86` `mem_or_regA` `imm` (MI)

   (3 op equivalent `ins-x86` `mem_or_regA` `mem_or_regA` `imm`)
   


Because memory operands can be directly encoded, spilled registers do not
always need to be explicitly rewritten before instruction selection.
However, we will need to reserve registers for some of the rewrites.
The current plan is to use `rax` and `xmm0`

### Legalization (before regalloc): conversions to two address form

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
