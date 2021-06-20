# A64 (aka ARM64/AArch64) Backend

The backend has the same structure at [A32 Backend](../CodeGenA32).

It also uses the same approach to [Instruction Selection](../Docs/instruction_selection.md)

## Comparing against gcc's instruction selector
```
aarch64-linux-gnu-gcc-8 test.c -c -O3  -o test.o ; aarch64-linux-gnu-objdump -D test.o
```
