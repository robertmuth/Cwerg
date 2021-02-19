# Cwerg

[[Getting Started]](Docs/getting_started.md) [[Documention]](Docs/) ![Status](../../workflows/cwerg-tests/badge.svg)



Cwerg started off as an experimental C compiler but has morphed into a
lightweight compiler backend aimed at experimental programming 
language implementations that want to avoid heavy dependencies like
[LLVM](https://llvm.org).

The project is very much "work in progress" and  currently consists of:

* RICS like [Intermediate Representation (IR)](Docs/opcodes.md) 
* Optimizer for the IR
* [C frontend](FrontEndC/README.md)  (supports a subset of C)
* [Elf Support Lib](Elf/README.md)   ((de-)compiler for ELF files)
* [A32 Support Lib](CpuA32/README.md) ((dis-) assembler for ARM32 instructions)
* [A32 backend](CodeGenA32/README.md) (code generator emitting ARM32 instructions)
* [C backend](CodeGenC/README.md) (code generator emitting C code)

It can be used for both AOT compilation and JITing.

Most components are implemented twice (see [rationale](Docs/why_python.md)):
1. spec/reference implementation: Python 3.8
2. high performance implementation: C++17 (with limited STL usage)

Re-implementations in other languages are explicitly encouraged. A lot of
code is table driven to facilitate that.

Cwerg de-emphasizes quality of the generated code (we hope to come within 30%
of state of the art  compilers) in favor of a small code base that can be
understood by a single developer and  very fast translation times.

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
explicit design goals for the c++ implementations.

## Intentional Limitations

To keep the project lightweight the feature set must be curtailed.
Since the project is still evolving, these are not entirely cast in stone but 
the following features are unlikely to be supported (contact us before starting 
any work on these):

* Instruction sets other than little endian (host and target) with 
  2's complement integers.
* Variable number of function parameters (var-args). Basically only used for
  printf/scanf and responsible for a disproportionate amount of complexity in 
   ABIs
* Full-blown dwarf debug info. The standard is over 300 pages long and unlikely
  to fit into the complexity budget. Line numbers will likely be supported.
* C++ exception. A lot of code and complexity that only benefits one language.
* Linking against code produced with other toolchains.
* Shared libs. The extra indirection and
  PC relative addressing adds complexity and slows programs down, not
  to mention the DLL hell problem.
* Sophisticated instruction scheduling which is less important from memory 
  bound code and out-of-order CPUs.
* Sophisticated loop optimizations.
* Variable sized stack frames (alloca). This
  would require a frame pointer and makes it more difficult to reason about
  stack overflows.
* Tail call optimizations 
* A standard library with unicode and locale support. Those add a lot of 
  complexity and are better left to dedicated libraries.
 
It is not clear if an [X86-64 backend](CpuX64/README.md) will fit into the 
complexity budget, especially since X64-64 idiosyncrasies tend to leak 
complexity into the generic layers.

The IR optimizer currently does not use a full-blown Single Static Assigment
(SSA) form. Instead it uses a [modified use-def chain approach](Docs/use_def.md)
to get some of the benefits of SSA.

## Dependencies

Cwerg controls dependencies carefully to keep them at a bare minimum:
 
* [pycparser](https://github.com/eliben/pycparser) used by the (optional) C frontend

## Inspirations

* [LLVM](https://llvm.org) 
* [QBE](https://c9x.me/compile/) ([QBE vs LLVM](https://c9x.me/compile/doc/llvm.html))
* [Mir](https://github.com/vnmakarov/mir) ([blog post](https://developers.redhat.com/blog/2020/01/20/mir-a-lightweight-jit-compiler-project/))
* [Oberon](http://www.projectoberon.com/) ([compiler implementation](http://www.inf.ethz.ch/personal/wirth/ProjectOberon/PO.System.pdf)) 
* [Delphi's compilation speed](https://news.ycombinator.com/item?id=24735366)
* [gcc code size](https://www.phoronix.com/scan.php?page=news_item&px=MTg3OTQ)



