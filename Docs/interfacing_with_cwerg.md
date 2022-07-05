# Interfacing With Cwerg

Cwerg includes several components that might be helpful for other compiler projects:

* the full backend
* the Arm32 assembler (A32)
* the Aarch64 assembler (A64)
* the X86-64 assembler (X64)


All 4 components have Python3 and C++ implementations which can be used as libraries. C bindigs wrapping parts of the C++ API also exist.

The components can be used AOT style and emit ELF images or JIT style and emit to memory where the code be called directly.
In addition, the full backend can emit testual assembler.


Besides using the components programmatically as libraries, there are also standalone exectuables that accept textual input.


Ports to other languages should be straight forward as all components are heavily
table driven. Please contact the author if you need help with [porting](backend_porting.md) or have suggestions for making the code base easier to interface.



Examples for JITing can be found in [Examples](../Examples).


The Python3 implementation of the A32 assembler can be found at [CpuA32/assembler_tool.py](../CpuA32/assembler_tool.py).
[CpuA32/Makefile](../CpuA32/Makefile) has many usage examples as part of the `$(DIR)/%.test` target.
 

 The A64 and X64 assemblers follow the same organization.


The full backend comes in 3 variants, one for each target architecture:
 * [CodeGenA32](../CodeGenA32/)
 * [CodeGenA64](../CodeGenA64/)
 * [CodeGenX64](../CodeGenX64/)

The Python3 implementation of the codegenerator (Cwert IR -> target code)
lives in `codegen.py`. Usage examples are provided by the `$(DIR)/%.asm.exe` 
targets in the `Makefile`.



