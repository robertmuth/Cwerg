# Cwerg

## The best C-like language that can be implemented in 10kLOC

![Status](../../workflows/cwerg-tests/badge.svg)
[![GitHub stars](https://img.shields.io/github/stars/robertmuth/Cwerg.svg?label=github%20stars)](https://github.com/robertmuth/Cwerg/stargazers)
[![Discord](https://img.shields.io/discord/1266057429091881011?logo=discord&style=flat)](https://discord.com/channels/1266057429091881011/)

Cwerg aims to be a complete, compact and fast "from-scratch" compiler for a C-like language.
It consists of the following components:
* **Frontend**: [Overview](FrontEndDocs/tutorial.md), [Additional Docs](FrontEndDocs/)

  A low-level C-like language with a Python inspired concrete syntax.
  Still actively development


* **Backend**: [Overview](Docs/intro.md),  [Backend IR](Docs/opcodes.md), [Additional Docs](Docs/)

  Muti-target (currently: X86-64, Aarch64, Arm32).

  Also suitable for other compilers and as a JIT.

  Defines an IR that serves as the interface between frontend and backend.

* [Deprecated C Frontend](FrontEndC/)  (translates a subset of C to Cwerg IR)
* [Deprecated WASM Frontend](FrontEndWASM/) (translates WASM/WASI coded to Cwerg IR)


Most components are implemented twice (see [rationale](Docs/why_python.md)):
1. spec/reference implementation: Python 3.9
2. high performance implementation: C++17 (with limited STL usage)

Re-implementations in other languages are explicitly encouraged. A lot of
code is table driven to facilitate that.

Cwerg de-emphasizes quality of the generated code (the hope is to come within 50%
of state of the art compilers) in favor of a small code base that can be
understood by a single developer and very fast translation times.
Explicit line number targets are in place to prevent feature creep:
* frontend: 10kLOC
* backend 10kLOC (target independent code) + 5kLOC (per target)



## Inspirations

* [LLVM](https://llvm.org)
* [QBE](https://c9x.me/compile/) ([QBE vs LLVM](https://c9x.me/compile/doc/llvm.html))
* [Mir](https://github.com/vnmakarov/mir) ([blog post](https://developers.redhat.com/blog/2020/01/20/mir-a-lightweight-jit-compiler-project/))
* [Wirth: A Plea for Lean Software](https://cr.yp.to/bib/1995/wirth.pdf),
  [Oberon](http://www.projectoberon.com/) ([compiler implementation](http://www.inf.ethz.ch/personal/wirth/ProjectOberon/PO.System.pdf))
* [Delphi's compilation speed](https://news.ycombinator.com/item?id=24735366)
* [gcc code size](https://www.phoronix.com/scan.php?page=news_item&px=MTg3OTQ)
