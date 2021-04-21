# Getting Started

### Setup

For simplicity we assume you are running on an x86-64 system with a recent Debian 
based Linux distributions.

To setup the python environment run this inside the
top level repo directory.
```
# make sure all the packages defined by Cwerg can be imported
export PYTHONPATH=$(pwd)

# confirm python interpreter version, you need at least Python 3.7
python3 -V

# install the c-parser if you want to use the code in FrontEndC/
sudo apt install python3-pycparser
```

To prepare the c++ build (you need at least a C++17 compatible compiler) run his inside the top level repo directory.
```

sudo apt install cmake

mkdir build
cd build
cmake ..
cd ..

# you may need to install the unwind library (used by the ASSERT macro
sudo apt install libunwind-dev

# in order to use the 32bit memory model ("-m32") on x86-64 you need to install

sudo apt install gcc-multilib


```

To set up and an Arm cross-compilation and testing environment please check
[TestQemu/README.md](../TestQemu/README.md)

### Testing

A good way to find yourself around the project is to start with
the top level Makefile. Just running 
```
make
```
will run a battery of self tests and confirm your set up is working properly

We currently use simple recursive Makefiles. The C++ implementation
is built via CMake which works better with IDEs.

The Python implementation contains the authoritative comments.
The C++ implementation re-uses the Python function names as much as possible.
The Python function comments apply to the C++ functions as well in this case.

### Directory Organization

The directory organization reflects the architecture of the Cwerg:

#### [Base/](../Base) 

contains the [IR](opcodes.md) definitions, (de-)serialization code, 
transformation and optimization passes.

Implementations: Python, C++ 
 
#### [CodeGenA32/](../CodeGenA32)

contains the Arm 32-bit backends which converts the IR to Arm32 machine Code.

Implementations: Python, C++ 

#### [CodeGenC/](../CodeGenC)
 
contains the C backend which converts the IR to equivalent C code
 
Implementations: Python
 
#### [CpuA32/](../CpuA32)

contains the (dis-)assemblers for the Arm 32-bit ISA. They are based
on a tabular description of the ISA which is also used by 
and may be useful for other projects as well.

Implementations: Python, C++ 

#### [CpuA64/](../CpuA64)  (work in progress)

contains the (dis-)assemblers for the Arm 64-bit ISA. They are based
on a tabular description of the ISA which is also used by 
and may be useful for other projects as well.

Implementations: Python, C++ 

#### [Elf/](../Elf)

contains the (dis-)assemblers for the Elf object code format.
Currently, only basic features necessary to deal with static executables
are supported but it is more or less "standalone" and may be useful for
 other projects as well
 
Implementations: Python, C++ 

#### [FrontEndC/](../FrontEndC)
 
contains a C frontend that translates a subset of the C language to the IR.
 
Implementations: Python
 

#### [TestQemu/](../TestQemu)

tests the cross development environment setup. 

#### [Tools/](../Tools)

misc tools

Implementations: Python

#### [Util](../Util)

contains basic helpers for parsing and elementary datastructures

Implementations: Python, C++

## Vaporware


#### [CpuX64/](../CpuX64)

future home of the  (dis-)assemblers for X86-64 ISA


#### [FrontEndLLVM/](../FrontEndLLVM)

future home of a LLVM to IR translator.


#### [FrontEndWASM/](../FrontEndWASM)

future home of a WASM to IR translator.

