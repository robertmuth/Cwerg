# Cwerg

## The best C-like language that can be implemented in 10kLOC

![Status](../../workflows/cwerg-tests/badge.svg)
[![GitHub stars](https://img.shields.io/github/stars/robertmuth/Cwerg.svg?label=github%20stars)](https://github.com/robertmuth/Cwerg/stargazers)
[![Discord](https://img.shields.io/discord/1266057429091881011?logo=discord&style=flat)](https://discord.com/channels/1266057429091881011/)

Cwerg aims to be a complete, compact and fast "from-scratch" compiler for a C-like language.
It has no dependencies and consists of the following components:
* **Frontend**: [Overview](FE/Docs/tutorial.md), [Additional Docs](FE/Docs/)

  A low-level C-like language with a Python inspired concrete syntax.
  Still actively development


* **Backend**: [Overview](BE/Docs/intro.md),  [Backend IR](BE/Docs/opcodes.md), [Additional Docs](BE/Docs/)

  Muti-target (currently: X86-64, Aarch64, Arm32).

  Also suitable for other compilers and as a JIT.

  Defines an IR that serves as the interface between frontend and backend.

* [Deprecated WASM Frontend](FE_WASM/) (translates WASM/WASI coded to Cwerg IR)

To get started hacking on Cwerg please read [getting_started.md](getting_started.md).

## Philosophy

Most components are implemented twice (see [rationale](why_python.md)):
1. spec/reference implementation: Python 3.9
2. high performance implementation: C++17 (with limited STL usage)

Re-implementations in other languages are explicitly encouraged.
A lot of code is table driven to facilitate that.

Cwerg de-emphasizes quality of the generated code (the hope is to come within 50%
of state of the art compilers) in favor of a small code base that can be
understood by a single developer and very fast translation times.
Explicit line number targets are in place to prevent feature creep:
* frontend: 10kLOC
* backend 10kLOC (target independent code) + 5kLOC (per target)

 ## Intentional Limitations

  To keep the project lightweight the feature set must be curtailed.
  Since the project is still evolving, the details are not entirely cast in stone but
  **the following features are unlikely to be supported** (contact us before starting
  any work on these):

  * Instruction sets other than [little endian](https://en.wikipedia.org/wiki/Comparison_of_instructio  n_set_architectures) (host and target) with 2's complement integers and IEEE floats.
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
    of slower code idioms and prevention of optimizations), not
    to mention the DLL hell problem. (see also: https://drewdevault.com/dynlib,
    https://www.kix.in/2008/06/19/an-alternative-to-shared-libraries/)
    (Lack of shared lib support likely precludes Windows as a target platform.)
  * Sophisticated instruction scheduling in the backend which is less important for memory
    bound code and out-of-order CPUs.
  * Sophisticated optimizations in the backend, like loop optimization.
    These are best left to the frontend.
  * Variable sized stack frames (alloca). This requires a frame pointer, wasting a register,
    and makes it more difficult to reason about stack overflows.
  * A large standard library with unicode and locale support. Those add a lot of
    complexity and are better left to dedicated libraries.
  * Sophisticated DSLs like LLVM's [Tablegen](https://llvm.org/docs/TableGen/).
    DSLs increase cognitive load and require additional infrastructure like parsers
    which eat into our size targets. Instead we leverage the expressiveness of Python.


## Inspirations

* [LLVM](https://llvm.org)
* [QBE](https://c9x.me/compile/) ([QBE vs LLVM](https://c9x.me/compile/doc/llvm.html))
* [Mir](https://github.com/vnmakarov/mir) ([blog post](https://developers.redhat.com/blog/2020/01/20/mir-a-lightweight-jit-compiler-project/))
* [Wirth: A Plea for Lean Software](https://cr.yp.to/bib/1995/wirth.pdf),
  [Oberon](http://www.projectoberon.com/) ([compiler implementation](http://www.inf.ethz.ch/personal/wirth/ProjectOberon/PO.System.pdf))
* [Delphi's compilation speed](https://news.ycombinator.com/item?id=24735366)
* [gcc code size](https://www.phoronix.com/scan.php?page=news_item&px=MTg3OTQ)
