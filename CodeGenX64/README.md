# X64 (aka x86-64) Backend

Limitations

* expected instruction set extensions: sse, lzcnt, tzcnt, ...
* one xmm registers for floating point 

## Code Selection Plan

Most x86 instructions for binary ops come in the following variants:

* `ins-x86` `mem_or_regA` `regB` (MR)

   (3 op equivalent: `ins-x86` `mem_or_regA` `mem_or_regA` `regB`)
* `ins-x86` `regA` `mem_or_regB` (RM) 

   (3 op equivalent `ins-x86` `regA` `regA` `mem_or_regB`)
* `ins-x86` `mem_or_regA` `imm` (MI)

   (3 op equivalent `ins-x86` `mem_or_regA` `mem_or_regA` `imm`)
   

### Legalization

The fact that memory operands can be directly encoded means that spilled 
registers do not need to be explicitly rewritten before instruction selection.

On the other hand we need to rewrite cwerg instructions if
1. three different registers are used
2. two different registers and an immediate are used
3. two registers are used in an `regA regB regA` pattern 
4. more than one memory operand is used

For commutative ops 3 is not an issue as we can simply flip the last two operands.

Issues 1 - 3 are addressed by a legalization pass BEFORE spill decisions are made:
1. `ins-cwerg` `regA` `regB` `regC` => rewrite

   `mov-cwerg` `tmp` `regB`; `ins-cwerg` `tmp` `tmp` `regC`; `mov-cwerg` `regA` `tmp`
2. `ins-cwerg` `regA` `regB` `imm` => rewrite

   `mov-cwerg` `tmp` `regB`;  `ins-cwerg` `tmp` `tmp` `imm`; `mov-cwerg` `regA` `tmp`
3. `ins-cwerg` `regA` `regB` `regA` => rewrite (with tmp reg)

    `mov-cwerg` `tmp` `regB`; `ins=cwerg` `tmp` `tmp` `regA`; `mov-cwerg` `regA` `tmp`


Issue 4 will become an issue after spilling is introduced by the register allocator.

Legalization will also rewrite instructions so that there is at most one immediate
and that immediate is in the last slot. 

### Pattern based instruction expansion after register allocation

After register allocation a register, `regX`, will either be assigned to an x86-64 
register, in which case we keep referring to  it as `regX`, or it will be spilled, 
in which case we refer to it as `spillX`.


Patterns involving immediates:

* `ins-cwerg` `regA` `regA` `imm` => direct expansion (MI)
* `ins-cwerg` `spillA` `spillA` `imm` => direct expansion (MI)
* `ins-cwerg` `regA` `regB` `imm` => complex expansion 

  `mov-x86` `regA` `regB`; `ins-x86` `regA` `imm` (MI)

* `ins-cwerg` `regA` `spillB` `imm` => complex expansion 

   `mov-x86` `regA` `spillB`; `ins-x86` `regA` `imm` (MI)
   
* `ins-cwerg` `spillA` `regB` `imm` => complex expansion 

  `mov-x86` `regA` `regB`; `ins-x86` `regA` `imm` (MI)


Patterns without immediates (AAB):


* `ins-cwerg` `regA` `regA` `regA` => direct expansion (RM) or (MR)
* `ins-cwerg` `regA` `regA` `regB` => direct expansion (RM) or (MR)
* `ins-cwerg` `regA` `regA` `spillB` => direct expansion (RM)
* `ins-cwerg` `spillA` `spillA` `regB` => direct expansion (MR)
* `ins-cwerg` `spillA` `spillA` `spillB` => complex expansion (with tmp reg)
 
   `mov-x86` `tmp` `spillB`; `ins-x86` `spillA` `tmp` (MR)

Patterns without immediates (ABB):

(Note: the ABB pattern occurs less often because strength reduction is often possible.)

* `ins-cwerg` `regA` `regB` `regB` => complex expansion 
  
  `mov-x86` `regA` `regB`; `ins-x86` `regA` `regB` (MR) or (RM)

* `ins-cwerg` `regA` `spillB` `spillB` => complex expansion
  
  `mov-x86` `regA` `spillB`; `ins-x86` `regA` `spillB` (RM)

* `ins-cwerg` `spillA` `regB` `regB` => complex expansion

  `mov-x86` `spillA` `regB`; `ins-x86` `spillA` `regB` (MR)
 
* `ins-cwerg` `spillA` `spillB` `spillB` => complex expansion (needs tmp)
   
   `mov-x86` `tmp` `spillB`; `ins-x86` `tmp` `spillB` (RM); `mov-x86` `spillA` `tmp`


### Misc other Issues:

* `Pro`: most immediates can be encoded directly without size restrictions
         in particular memory offsets can be up to 32 bit.
* `Con`: div/mul/shl/shr instructions use implicit registers

