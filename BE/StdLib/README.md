## StdLib 

Currently a very thin wrapper around a small number of Linux syscalls

## Usage Idioms

### FrontEndC - Generation of IR From C (C -> IR)

Use this include instead of the usual libc includes.
```
 #include "std_lib.h"
```
This includes the prototypes for StdLib.

### CodeGenC - Generation of Executables via C (IR -> C -> EXE)

Assuming `test.asm` contains the IR, we need to concatenate library files
to simulated linking, e.g.
```
cat syscall.extern32.asm  std_lib.32.asm test.asm | CodeGenC/codegen.py - > test.32.c

or

cat syscall.extern64.asm  std_lib.64.asm test.asm | CodeGenC/codegen.py - > test.64.c
```


`syscall.externXX.asm` are just stubs that need to be replaced in the final link 
with `syscall.c` which contain the actual syscall implementation.

```
gcc -O -static -m32 -nostdlib StdLib/syscall.c test.32.c -o test.32.exe

or

gcc -O -static -m64 -nostdlib StdLib/syscall.c test.64.c -o test.64.exe
```

By going to C code as an intermediate step we can generate code for X86-32 and X86-64.

### CodeGenA32/CodeGenA64 - Direct Generation of Executables (IR -> EXE)

```
cat syscall.a32.asm  std_lib.32.asm test.asm | CodeGenA32/codegen.py  binary - test.a32.exe
```
or 

 ```
cat syscall.a64.asm  std_lib.64.asm test.asm | CodeGenA64/codegen.py  binary - test.a64.exe
```

This is fully hermetic in that we also provide actual syscall implementations via 
`syscall.a32.asm` or `syscall.a64.asm`.

## References

See `syscall.c` for experiments.

Linux syscall overview (covers multiple architectures)
https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md

Linux nolibc
https://github.com/torvalds/linux/blob/master/tools/include/nolibc/nolibc.h

Calling conventions for Linux syscall
https://stackoverflow.com/questions/2535989/what-are-the-calling-conventions-for-unix-linux-system-calls-and-user-space-f

Error codes:
https://mariadb.com/kb/en/operating-system-error-codes/
