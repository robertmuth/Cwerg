## Basic Dwarf Support


This directory contains basic Dwarf support for source line numbers

## References

objdump command for dumping line number info
* objdump -Wl build/optimize_tool.exe

Dwarf 5 Stanard: https://dwarfstd.org/doc/DWARF5.pdf 

* 6.2.4 The Line Number Program Header
* 7.22 Line Number Information

https://github.com/CyberGrandChallenge/binutils/blob/master/bfd/dwarf2.c


Binutils/bfd code:
* https://github.com/CyberGrandChallenge/binutils/blob/master/bfd/dwarf2.c