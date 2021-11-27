# Cwerg

[[Documentation]](Docs/) ![Status](../../workflows/cwerg-tests/badge.svg)



Cwerg is a lightweight compiler backend aimed at experimental programming 
language implementations that want to avoid heavy dependencies like
[LLVM](https://llvm.org). It has no dependencies and can directly generate
ELF executables for Arm32 and Arm64 ISAs.
Besides AOT compilation, (one-shot) JITing is also supported.

The project is very much "work in progress" and  currently consists of:

* RICS like [Intermediate Representation (IR)](Docs/opcodes.md) 
* Optimizer for the IR
* [C Frontend](FrontEndC/)  (supports a subset of C)
* [WASM Frontend](FrontEndWASM/) (transpiler WASM to Cwerg)
* [Elf Support Lib](Elf/)   ((de-)compiler for ELF object files)
* [A32 Support Lib](CpuA32/) ((dis-) assembler for ARM32 instructions)
* [A64 Support Lib](CpuA64/) ((dis-) assembler for ARM64 instructions)
* [X64 Support Lib](CpuX64/) ((dis-) assembler for X64-64 instructions - WIP)
* [A32 Backend](CodeGenA32/) (code generator emitting ARM32 instructions)
* [A64 Backend](CodeGenA64/) (code generator emitting ARM64 instructions)
* [C Backend](CodeGenC/) (code generator emitting C code)

Most components are implemented twice (see [rationale](Docs/why_python.md)):
1. spec/reference implementation: Python 3.7
2. high performance implementation: C++17 (with limited STL usage)

Re-implementations in other languages are explicitly encouraged. A lot of
code is table driven to facilitate that.

Cwerg de-emphasizes quality of the generated code (we hope to come within 50%
of state of the art  compilers) in favor of a small code base that can be
understood by a single developer and very fast translation times.

### Size Targets

The project tracks code size in [LOC](CLOC.txt) carefully. The goal is to limit 
the IR optimizer to 10kLOC and an additional 5kLOC for each supported target 
[ISA](https://en.wikipedia.org/wiki/Instruction_set_architecture) 
(per implementation language).
Note, that code generated from tables is not counted but the tables (written in Python) are.

### Speed Targets

The goal for the c++ implementation is to translate the IR to an Elf executable at a speed of 
500k IR instructions per sec using at most 4 cores on a 2020 era midrange desktop or high end laptop.

Whole program translation and parallel translation at the function level are 
explicit design goals for the C++ implementations.

Cwerg does not have a linker. Instead the responsibility of 
generating executables and resolving relocations rests with the assembler
components of the various backends. An ELF library helps with the generation of
ELF executables, which is the only object format currently supported.

## Intentional Limitations

To keep the project lightweight the feature set must be curtailed.
Since the project is still evolving, the details are not entirely cast in stone but 
**the following features are unlikely to be supported** (contact us before starting 
any work on these):

* Instruction sets other than [little endian](https://en.wikipedia.org/wiki/Comparison_of_instruction_set_architectures) (host and target) with 
  2's complement integers.
* Variable number of function parameters (var-args). Basically only used for
  printf/scanf and responsible for a disproportionate amount of complexity in 
  ABIs. (Note, this precludes a proper C frontend.)
* Full-blown dwarf debug info. The standard is over 300 pages long and unlikely
  to fit into the complexity budget. Line numbers will likely be supported.
* C++ exception/unwind tables. A lot of code and complexity that only benefits one language.
* Linking against code produced with other toolchains. There are currently no plans
  to emit linkable object code. And there is no ABI compatibility except for simple cases. 
* Shared libs/dynamic linking adds complexity and slows programs down (both because
  of slower code idioms and prevention of optimizations), not
  to mention the DLL hell problem. (see also: https://drewdevault.com/dynlib, 
  https://www.kix.in/2008/06/19/an-alternative-to-shared-libraries/)
* Sophisticated instruction scheduling which is less important for memory 
  bound code and out-of-order CPUs.
* Sophisticated loop optimizations. Probably best left to the frontend.
* Variable sized stack frames (alloca). This requires a frame pointer, wasting a register,
  and makes it more difficult to reason about stack overflows.
* A large standard library with unicode and locale support. Those add a lot of 
  complexity and are better left to dedicated libraries.
 


The IR optimizer currently does not use a full-blown Single Static Assigment
(SSA) form. Instead it uses a [modified use-def chain approach](Docs/use_def.md)
to get some of the benefits of SSA. 

## Porting to other Architectures

A port to X86-64 is currently WIP.

Ports for more regular architectures, e.g. RISC V, should be straight forward to implement [(see porting hints)](Docs/backend_porting.md).

## Dependencies

Cwerg controls dependencies carefully to keep them at a bare minimum:
 
* [pycparser](https://github.com/eliben/pycparser) used by the (optional) C frontend

## Inspirations

* [LLVM](https://llvm.org) 
* [QBE](https://c9x.me/compile/) ([QBE vs LLVM](https://c9x.me/compile/doc/llvm.html))
* [Mir](https://github.com/vnmakarov/mir) ([blog post](https://developers.redhat.com/blog/2020/01/20/mir-a-lightweight-jit-compiler-project/))
* [Wirth: A Plea for Lean Software](https://cr.yp.to/bib/1995/wirth.pdf),
  [Oberon](http://www.projectoberon.com/) ([compiler implementation](http://www.inf.ethz.ch/personal/wirth/ProjectOberon/PO.System.pdf)) 
* [Delphi's compilation speed](https://news.ycombinator.com/item?id=24735366)
* [gcc code size](https://www.phoronix.com/scan.php?page=news_item&px=MTg3OTQ)



