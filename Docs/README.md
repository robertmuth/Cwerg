
## General

[Intro](../README.md)

[Getting Started](getting_started.md)

[Why Python](why_python.md)

[TODOs](todo.md)

[FAQ](FAQ.md)

[Debugging Hints](debugging.md)


## Frontend

[Intro](../FrontEnd/README.md)

[AST Node Description](ast.md)

## Backend

[Opcode Description](opcodes.md)


### Implementation Details

[Liveness Analysis](liveness.md)

[Reaching Defs](use_def.md)

[Instruction Selection](instruction_selection.md)


## Directory Organization

### Examples

[Examples](../Examples/README.md)

### Frontends

Emit Cwerg IR from input languages.

[Cwerg Frontend](../FrontEnd/README.md),
[C (Lite) Frontend](../FrontEndC/README.md), 
[WASM/WASI Frontend](../FrontEndWASM/README.md)

### Backends

Generate a target (machine) code from Cwerg IR code.

Implementations: Python, C++ (except for C Backend which is Python only)

[C Backend](../CodeGenC/README.md), 
[Arm32 (A32) Backend](../CodeGenA32/README.md), 
[Aarch64 (A64) Backend](../CodeGenA64/README.md), 
[X64-64 (X64) Backend](../CodeGenX64/README.md), 

### Target ISAs (Assembler/Disassembler)

Can be used standalone (without the rest of Cwerg)

Implementations: Python, C++ 

[Arm32 (A32) ISA](../CpuA32/README.md),
[AArch64 (A64)) ISA](../CpuA64/README.md), 
[X86-64 (X64)) ISA](../CpuX64/README.md) 


### Object File Format Suuport

Can be used standalone (without the rest of Cwerg)

Implementations: Python, C++ 

[ELF](../Elf/README.md) - 32 and 64 bit Elf support

### Runtime Library

Very basic standard lib

[StdLib](../StdLib/README.md)


### Misc

[TestQemu/](../TestQemu) tests the cross development environment setup

[Util](../Util) contains basic helpers for parsing and elementary datastructures

[Tools/](../Tools) misc tools, primarily for debugging