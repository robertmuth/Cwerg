# Cwerg

This Project aims at building a re-targetable C compiler that is easy
to understand and modify.

It is currently developed in Python on top of Eli Bendersky 
(pycparser)[https://github.com/eliben/pycparser] lexer/parser for C99.

The project still has a along way to go. If you are looking for something more
mature, you might save yourself some time by looking at the survey of other C-compilers which 
can be found below.

## Highlevel Overview

The compilation can be split into the following phases:

* Parse the code with pycparser into an AST

* Extract symbol and type information from the AST so that we can map
  each ID node to a declaration and each expression node to a type.
  
  This is currently done by creating edges from nodes within the AST
  to other nodes inside the AST and new nodes.
  
  Instead of inventing a new type system we use the nodes from pycparser
  
 * Canonicalize the c code so we can keep the backend simple
  
  This effectively de-sugars some syntax like compound assigns and 
  pre/post increment/decrement.
  
  We can test the canonicalization transformations by re-emitting c-code
  and ensuring that the transformed code has the same output as the original 
  code
  
 * Code emission
  
## Project Status

* the supported part of the C language is whatever is in Tests/*c
* no backend yet


## Survey of other open source c-compiler projects

## chibicc

* implemented in C
* very compact, only 5 .c files
* bring you own pre-processor and libc
* target: x86-64


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

### lcc

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

## pcc

* based on the original Portable C Compiler by S. C. Johnson 
* much improved and actively maintained
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

## shivyc

* implemented in Python
* target: x86-64

Links

https://github.com/ShivamSarodia/ShivyC

## tcc

* small code base  but not for the faint of heart
* everything included approach (including linker)
* mutliple targets: x86, x86-64, arm 
* emits elf object files

Links

* https://bellard.org/tcc/
* http://download.savannah.gnu.org/releases/tinycc/







