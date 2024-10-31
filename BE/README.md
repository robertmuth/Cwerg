## Cwerg Backend

While primarily developed for the Cwerg Language,
the Cwerg backend is suitable for any new (C-like) programming
language implementation that wants to avoid heavy dependencies like
[LLVM](https://llvm.org). It has no dependencies and can directly generate
ELF executables for Arm32, Arm64 and X86-64 ISAs.

Besides AOT compilation, (one-shot) JITing is also supported.

If you are interested in using Cwerg as backend for your own compiler
project, please check out [Interfacing with Cwerg](Docs/interfacing_with_cwerg.md)
and/or reach out to the author.

Some API usage examples, including JITing, can be found in [ApiDemo](ApiDemo/).

Implementing support for new (regular) ISAs like  RISC V should be straightforward to [(see porting hints)](Docs/backend_porting.md).

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

## Comlexity Budget

* 10kLOC (target independent code)
* 5kLOC (per target)

## Intentional Limitations

To keep the backend lightweight the feature set must be curtailed.
Since the project is still evolving, the details are not entirely cast in stone but
**the following features are unlikely to be supported** (contact us before starting
any work on these):

* Instruction sets other than [little endian](https://en.wikipedia.org/wiki/Comparison_of_instruction_set_architectures) (host and target) with 2's complement integers and IEEE floats.
* Variable number of function parameters (var-args). Basically only used for
  printf/scanf and responsible for a disproportionate amount of complexity in
  ABIs. (Note, this precludes a proper C frontend.)
* Full-blown dwarf debug info. The standard is over 300 pages long and unlikely
  to fit into the complexity budget. Line numbers will likely be supported.
* Exceptions. A lot of complexity especially at object level e.g. unwind tables.
  Backtraces will be supported since they are crucial for debugging.
* Linking against code produced with other toolchains. There are currently no plans
  to emit linkable object code. And there is no ABI compatibility except for simple cases and syscal  ls.
* Shared libs/dynamic linking adds complexity and slows programs down (both because
  of slower code idioms and prevention of optimizations), not to mention the DLL hell problem. (see also: https://drewdevault.com/dynlib,
  https://www.kix.in/2008/06/19/an-alternative-to-shared-libraries/)
  (Lack of shared lib support likely precludes Windows as a target platform.)
* Sophisticated instruction scheduling in the backend which is less important for
  memory bound code and out-of-order CPUs.
* Sophisticated optimizations in the backend, like loop optimization.
  These are best left to the frontend.
* Variable sized stack frames (alloca). This requires a frame pointer, wasting a
  register, and makes it more difficult to reason about stack overflows.
* A large standard library with unicode and locale support. Those add a lot of
  complexity and are better left to dedicated libraries.
* Sophisticated DSLs like LLVM's [Tablegen](https://llvm.org/docs/TableGen/).
  DSLs increase cognitive load and require additional infrastructure like parsers
  which eat into our size targets. Instead we leverage the expressiveness of Python.

## Misc Docs

* [IR Opcode Description](Docs/opcodes.md)
* [TODOs](Docs/todo.md)
* [FAQ](Docs/FAQ.md)
* [Debugging Hints](Docs/debugging.md)
* [Liveness Analysis](Docs/liveness.md)
* [Reaching Defs](Docs/use_def.md)
* [Instruction Selection](Docs/instruction_selection.md)
* [Backend Porting](Docs/backend_porting.md)
* [Interfacing with Cwerg](Docs/interfacing_with_cwerg.md)