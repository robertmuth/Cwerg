# C-Lite Frontend For Cwerg

This simplified C compiler frontend was the original starting point of the Cwerg project.
 
Most of the heavy lifting is done by Eli Bendersky's 
(pycparser)[https://github.com/eliben/pycparser] lexer/parser for C99.

This component is unlikely to get much love in the foreseeable future. 
If you are looking for something more mature, you might save yourself some time by looking at the survey of other C-compilers which  can be found below.

## Project Status

* the supported part of the C language is whatever is in `TestData/*c`
  (this implies that the development is test driven) 
  Expect the following **not** to work
  * typedefs 
  * bitfields
  * vararg (except for limited support of printf)
  * post --/++
* the canonicalizer is already useful. It transforms C programs into
  equivalents programs that use a smaller subset of the C language. 
  For example, canonicalized programs do not
  use pre/post in-/decrement and do not have for or while loops. 
* translate.py contains a somewhat hacky Cwerg backend

Note: the tests in this directory are only testing the canonicalizer

The Cwerg code generation is exercised by ../Makefile.integration

## High Level Overview

The compilation is split into the following phases:

* Parse the code with pycparser into an AST

* Extract symbol and type information from the AST so that we can map
  each ID node to a declaration and each expression node to a type.
  
  This is currently done by creating edges from nodes within the AST
  to other nodes inside the AST and new nodes.
  
  Instead of inventing a new type system we use the nodes from pycparser
  
 * Canonicalize the c code so we can keep the backend simple
  
   This effectively de-sugars some syntax like compound assigns and 
   pre/post increment/decrement, loops, etc.
  
   We can test the canonicalization transformations by re-emitting c-code
   and ensuring that the transformed code has the same output as the original 
   code.
  
 * Code emission
  
## Useful References

* Some things every C programmer should know about C
  https://web.archive.org/web/20030812081713/http://klausler.com/cnotes.txt
 
## Survey of other open source c-compiler projects

### A Compiler Writing Journey

* implements a subset of C

Links

https://github.com/DoctorWkt/acwj

### chibicc

* implemented in C by Rui Ueyama et el
* very compact, only 5 .c files
* bring you own pre-processor and libc
* target: x86-64
* successor of [8cc](https://github.com/rui314/8cc) and [9cc](https://github.com/rui314/9cc)

Links

* book (japanese only) https://www.sigbus.info/compilerbook
* https://github.com/rui314/chibicc

### clang

* implemented in C++
* sort of today's gold standard for C compilers
* enormously versatile
* rather steep learning curve
* very actively developed
* includes pre-processor 
* llvm backend (supports all llvm targets)

Links

https://clang.llvm.org/

### cproc

* implemented in C (self hosting) by Michael Forney et al
* actively developed
* [QBE backend](https://c9x.me/compile/) supporting aarch64 and x86-64
* successor (?) of [Andrew Chamber's C Suite](https://github.com/andrewchambers/c)

Links

* https://git.sr.ht/~mcf/cproc

### firm

* Intermediate code system using SSA and written in C
* Started as research project at uni-karlsruhe.de 
* C99 Compiler. CParser
* targets: amd64, ia32, arm32, mips, riscv,sparc

Links:

* about: https://pp.ipd.kit.edu/firm/index.html
* code: https://github.com/libfirm/libfirm
* Comparison with LLVM: https://pp.ipd.kit.edu/firm/LLVM.html
* cparser: https://github.com/libfirm/cparser/
  
### gcc

* gold standard for C on Unix before clang came along
* definitely not suitable for casual hacking
* implemented in C (and nowadays C++)
* includes pre-processor 
* very steep learning curve
* Information below may be dated (I am too traumatized to try again):
* many many targets but not simultaneously 
* configuration and building (especially cross compiles) very painful 

Links

https://gcc.gnu.org/

### lacc

* implemented in C (self hosting)  by Lars Kirkholt Melhus
* x86-64 only but can emit elf object files


Links

* https://github.com/larmel/lacc

### lcc

* written in C by Dave Hanson, Chris Fraser et al
* very well documented compiler 
* partially aimed at education
* feels a bit dated, front and backend are not separate programs
* not actively developed any more (pelles c is based on it but not open source)
* bring you own pre-processor and libc
* mutliple targets: x86, mips, sparc

Links

* https://en.wikipedia.org/wiki/LCC_(compiler)
* book https://www.amazon.com/Retargetable-Compiler-Design-Implementation/dp/0805316701
* https://github.com/drh/lcc

### mir

* written in C by Vladimir Makarov
* A light-weight JIT compiler based on MIR (Medium Internal Representation)
* c2mir C11 Compiler 
* targets: arm64, ppc63, amd64

Links

* https://github.com/vnmakarov/mir
* https://github.com/vnmakarov/mir/tree/master/c2mir

### pacc

* written in Delphi by Benjamin Rosseaux
* uses qbe inspired backend

Links

https://github.com/BeRo1985/pacc

### pcc

* written in C by Anders Magnusson et al
* based on the original Portable C Compiler by S. C. Johnson 
* much improved though
* actively maintained
* easy to configure
* multiple targets: x86 x86-64 mips mips64 68k power sparc pdp10 pdp11
* clear separation between front and backend 

Links

* http://pcc.ludd.ltu.se/
* (original paper) ftp://pcc.ludd.ltu.se/pub/pcc-docs/porttour.ps
* http://pcc.ludd.ltu.se/ftp/pub/pcc-docs/targdocs.txt
* cvs -d :pserver:anonymous@pcc.ludd.ltu.se:/cvsroot co pcc

### plan 9 cc

* implemented in C 
* had trouble configuring but did not spend a lot of time with it
* multiple target: x86, x86-64, sparc, power, power-64, mips, arm


Links

https://9p.io/sys/doc/compiler.html
https://9p.io/wiki/plan9/Sources_repository/index.html
https://github.com/huangguiyang/plan9-cc (not official?)

### scc

* implemnted in C by Roberto E. Vargas Caballero et al
* actively developed
* backends for arm32, x86-64, qbe and possibly others
* may (?) also use the qbe backend

Links


http://www.simple-cc.org/

http://git.simple-cc.org/scc/file/README.html

mirror: https://github.com/k0gaMSX/scc

### shivyc

* implemented in Python
* target: x86-64

Links

https://github.com/ShivamSarodia/ShivyC


## SmallerC

* implemented in C (self-hosting)
* targets: x86 (32 + 16bit), Mips
* includes libc

Links

https://github.com/alexfru/SmallerC

## tcc

* written in C (self hosting) by Fabrice Bellard et al
* small code base  but not for the faint of heart
* everything included approach (including linker)
* multiple targets: x86, x86-64, arm 
* emits elf object files

Links

* https://bellard.org/tcc/
* http://download.savannah.gnu.org/releases/tinycc/







