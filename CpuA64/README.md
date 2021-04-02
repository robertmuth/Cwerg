# A64 (AArch64) Encoder/Decoder

This directory contains code for encoding and decoding A64 instructions.

The implementation is far more complete than what is needed by [../CodeGenA64]
and might be useful by itself.

It also contains an assembler that can directly generate Elf executables.

## Concepts

An instruction consists of two parts:
1. a template describing its format, aka `Opcode`,
   which breaks down the instruction into the fixed bits a list of `Operands`.  
2. a list of integers, one for each `Operand` in the `Opcode`.

The integers are usually just the bits used by the operand shifted all the 
way to the right but for some immediate operands we decode the operand for
ergonomic reasons. 
 
A list of all opcodes and their operands can be obtained by running
```
./opcode_tab.py 
```

To look up the concrete decomposition of an instruction word run
```
 ./disassembler.py f11fe29f
```
which will print 
```
f11fe29f subs_x_imm xzr x20 0x7f8
OPCODE subs x_imm
    XREG_0_4                            xzr        (31)
    XREG_5_9                            x20        (20)
    IMM_SHIFTED_10_21_22                0x7f8      (2040)
```

### Opcode Names

The opcode name consists of a basename plus one or more variant suffices separated
by underscores. We re-use the "official" instruction names as base names as much as
possible. 
The variant component is necessary for disambiguation since the official 
instruction names are heavily overloaded.

When unsure about the name and variant 
* grep for a similar instruction in  TestData/a64_test.*dis and
* feed the 32 bit hexcode into ./disassembler.py as above 

### Operands

An `Operand` represents:
* a register
* an immediate value
* a shift direction
* etc.

The order of the `Operands` roughly corresponds to the order in the
assembler notation with the following exceptions:
* written registers precede read registers. This primarily affects `str`
  instructions where the "storee" is moved to the end, and (v)ldm instructions where the register masks is moved to the front.
* the `lr` register in `bl` and `ret` instruction is made explicit
* `str` and `ldr` instruction do not use square brackets, exclamation marks, minus signs
  to indicate the various addressing modes as this is already encoded in the opcode variant
* some feature like sign extension modes and addressing modes which
  look like operands in the official syntax are expressed as opcode variants 
 
### API

`opcode_tab.Assemble()` converts and int to an `opcode_tab.Ins`.
`opcode_tab.Disasemble()` does the inverse.

`symbolic.InsSymbolize()` converts an `opcode_tab.Ins` into a more 
human friendly form. (Reminder: we deviate from the official notation.).
`symbolic.InsFromSybolized()` does the inverse.


## References

* Quick Reference
  https://courses.cs.washington.edu/courses/cse469/19wi/arm64.pdf

* Official Documentation  

  https://developer.arm.com/documentation/ddi0487/latest/  
  
* Awesome online assembler/disassembler based on Keystone/Capstone 
  (based on LLVM's  machine description)
  
  http://shell-storm.org/online/Online-Assembler-and-Disassembler/?inst=%09scvtf%09s1%2C+w0&arch=arm64&as_format=inline#assembly

* iOSGod's online assembler 

  https://armconverter.com/

* Machine readable encoding tables

  https://github.com/CAS-Atlantic/AArch64-Encoding

* ISA Overview Talk

  https://ra.ziti.uni-heidelberg.de/cag/images/seminars/ss14/2014-hochstrasser-talk.pdf
  

* Goldbolt's explorer for compiler generated code 

  https://godbolt.org/ 


* AsmJIT's Encoding/Decoding tables for misc ISAs (A64 does not seem fully supported)

  tables https://github.com/asmjit/asmdb/blob/master/armdata.js
  
  asmgrid (online explorer) https://asmjit.com/asmgrid/
  
