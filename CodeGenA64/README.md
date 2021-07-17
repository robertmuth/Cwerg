# A64 (aka ARM64/AArch64) Backend

The backend has the same structure at [A32 Backend](../CodeGenA32).

It also uses the same approach to [Instruction Selection](../Docs/instruction_selection.md)
which is a straight forward expansion of the IR opcodes into zero or more A64 opcodes.

[isel_tab.py](isel_tab.py) contains the necessary tables which 
are also use to generate C++ code.

## Comparing against gcc's instruction selector
```
aarch64-linux-gnu-gcc-8 test.c -c -O3  -o test.o ; aarch64-linux-gnu-objdump -D test.o
```
