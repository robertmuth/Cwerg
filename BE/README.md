## Cwerg Backend

## Directory Organization

* [ApiDemo/](ApiDemo/) shows how to use the backend for AOT and JITing.
* [CpuA32/](CpuA32/) assembler/disassembler for A32 (Arm32)
* [CpuA64/](CpuA64/) assembler/disassembler for A64 (Arm32)
* [CpuX64/](CpuX64/) assembler/disassembler for X64 (X86-64))
* [CodeGenA32/](CodeGenA32/) code generator. register allocator, etc. for A32
* [CodeGenA64/](CodeGenA64/) code generator. register allocator, etc. for A64
* [CodeGenX64/](CodeGenX64/) code generator. register allocator, etc. for X64
* [CodeGenC/](CodeGenC/) code generator transpiling to C
* [ELF/](Elf/) Elf support (32 and 64 bit)
* [StdLib/](StdLib/) basic runtime library written in Cwerg IR
* [Tools/](Tools/) misc tools, primarily for debugging

## Misc

* [IR Opcode Description](Docs/opcodes.md)
* [TODOs](Docs/todo.md)
* [FAQ](Docs/FAQ.md)
* [Debugging Hints](Docs/debugging.md)
* [Liveness Analysis](Docs/liveness.md)
* [Reaching Defs](Docs/use_def.md)
* [Instruction Selection](Docs/instruction_selection.md)
* [Backend Porting](backend_porting.md)