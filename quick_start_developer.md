# Getting Started


### Setup

For simplicity we assume you are running on an x86-64 system with a **recent** Debian
based Linux distributions like Ubuntu 24.04


First you need to install (cross) tool chains and emulators.

Cwerg requires C++20 compatible compilers and Python 3.12 or higher.

The emulators are needed for testing of ARM executables produced by Cwerg.


```
sudo apt install cmake
sudo apt install gcc g++
sudo apt install gcc-multilib
sudo apt-get install libunwind-dev gcc-multilib
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
sudo apt install qemu-user-static
```

Run the following command to see if everything is setup properly:
```
make test_setup
```

If the steps do not work, the instructions may be out of date.
Check how the continous integration sets up its enviroment in
[.github/workflows/ci.yml](.github/workflows/ci.yml).


### Orientation

To test everything run
```
make tests
```
This will take several minutes.

The [Makefile](Makefile) target `tests` primarily invokes other nested
Makefiles and is good starting point for exploring the project.

If you want to invoke nested Makefiles directly, always set:
```
export PYTHONPATH=$(pwd)
```
The toplevel Makefile will do this implicitly but the nested Makefiles
do not.

The component that have been ported to C++ use `CMake`
which works better with IDEs. All the build-artifacts are kept
in the toplevel `build/` directory.

The source code is organized into the following directories:
* [BE/](BE/) - the backend Code
* [FE/](FE/) - the frontend Code
* [IR/](IR/) - the IR which represents that inteface between FE and BE
* [Util/](Util/) - code shared by frontend and backend
* [TestQemu/](TestQemu/) - cross compilation and emulation tests

Almost all compoents are implemented both in Python and C++.
The Python implementation contains the authoritative comments.
The C++ implementation re-uses the Python function names as much as possible.
The Python function comments apply to the C++ functions as well in this case.


### Simple Example: Sieve of Eratosthenes


Cwerg code for Sieve:

[Cwerg source code](FE/LangTest/sieve_test.cw)


Compiling this to Cwerg IR (flavored for a32) is accomplished via:
```
FE/compiler.py -shake_tree -stdlib FE/Lib -arch a32 FE/LangTest/sieve_test.cw > sieve.a32.ir
```

[sieve.a32.ir](FE/Docs/sieve.a32.ir)


From here we can generate an A32 executable with:

```
BE/CodeGenA32/codegen.py -mode binary BE/StdLib/startup.a32.asm BE/StdLib/syscall.a32.asm sieve.a32.ir sieve.a32.exe
```

And, assuming you have installed qemu or run on an Arm system, you can run this executable like so
`./sieve.a32.exe`


Instead of generating an executable we can also generate Cwergs flavor or A32 assembly like so:

BE/CodeGenA32/codegen.py -mode normal BE/StdLib/startup.a32.asm BE/StdLib/syscall.a32.asm sieve.a32.ir sieve.a32.cw_dis

[sieve.a32.cw_dis](FE/Docs/sieve.a32.cw_dis)

This assembly is rather non standard.
Disassembling the executable provides the more standard Arm32 assembler via:
```
arm-linux-gnueabihf-objdump -d ./sieve.a32.exe > sieve.a32.dis
```

[sieve.a32.dis](FE/Docs/sieve.a32.dis)


### Summary Of Commands For Generating an Executable

#### X64 (X86-64)

```
FE/compiler.py -shake_tree -stdlib FE/Lib -arch x64 FE/LangTest/sieve_test.cw > sieve.x64.ir
BE/CodeGenX64/codegen.py -mode binary  BE/StdLib/startup.x64.asm BE/StdLib/syscall.x64.asm sieve.x64.ir sieve.x64.exe

./sieve.x64.exe

objdump -d sieve.x64.exe
```

#### A32 (Arm32)

```
FE/compiler.py -shake_tree -stdlib FE/Lib -arch a32 FE/LangTest/sieve_test.cw > sieve.a32.ir
BE/CodeGenA32/codegen.py -mode binary BE/StdLib/startup.a32.asm BE/StdLib/syscall.a32.asm sieve.a32.ir  sieve.a32.exe

./sieve.a32.exe

arm-linux-gnueabihf-objdump -d sieve.a32.exe
```

#### A64 (Aarch64))

```
FE/compiler.py -shake_tree -stdlib FE/Lib -arch a64 FE/LangTest/sieve_test.cw > sieve.a64.ir
BE/CodeGenA64/codegen.py -mode binary BE/StdLib/startup.a64.asm BE/StdLib/syscall.a64.asm sieve.a64.ir sieve.a64.exe


./sieve.a64.exe

aarch64-linux-gnu-objdump -d sieve.a64.exe
```
