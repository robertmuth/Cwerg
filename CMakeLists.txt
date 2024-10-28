cmake_minimum_required(VERSION 3.10)
project(Cwerg)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "-fno-exceptions -O3 -g -Wall -Werror -pedantic -Wno-class-memaccess -Wno-sign-compare ${CWERG_FLAGS}")
# lto is broke in 22.04: "bytecode mismatch 11.2 vs 11.3"
set(CMAKE_EXE_LINKER_FLAGS "-static -fno-lto")

# with static linking, see
# https://gcc.gnu.org/bugzilla/show_bug.cgi?id=58909
# Everything here is super brittle:  the order of libs matter
set(CMAKE_CXX_STANDARD_LIBRARIES "${CWERG_LIBS} -Wl,--whole-archive -lpthread -Wl,--no-whole-archive ")

# The must come AFTER their use or be commented out to be picked up from the environment
set(CWERG_LIBS "")
set(CWERG_FLAGS "")

include_directories(./)

add_library(UTIL_LIB OBJECT
        Util/assert.cc
        Util/assert.h
        Util/breakpoint.cc
        Util/breakpoint.h
        Util/bitvec.cc
        Util/bitvec.h
        Util/bst.cc
        Util/bst.h
        Util/handle.h
        Util/handle.cc
        Util/handlevec.cc
        Util/handlevec.h
        Util/immutable.cc
        Util/immutable.h
        Util/list.h
        Util/mem_pool.h
        Util/parse.cc
        Util/parse.h
        Util/stripe.cc
        Util/stripe.h
        Util/switch.cc
        Util/switch.h
        Util/webserver.cc
        Util/webserver.h
)

add_executable(immutable_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/immutable_test.cc
)

add_executable(bitvec_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/bitvec_test.cc
)

add_executable(handle_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/handle_test.cc
)

add_executable(handlevec_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/handlevec_test.cc
)

add_executable(parse_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/parse_test.cc
)

add_executable(mem_pool_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/mem_pool_test.cc
)

add_library(CPUA32_LIB OBJECT
        CpuA32/symbolic.cc
        CpuA32/symbolic.h
        CpuA32/assembler.cc
        CpuA32/assembler.h
        CpuA32/opcode_gen.cc
        CpuA32/opcode_gen.h
)

add_library(CPUA32_LITE_LIB OBJECT
        CpuA32/symbolic.cc
        CpuA32/symbolic.h
        CpuA32/opcode_gen.cc
        CpuA32/opcode_gen.h
)

add_library(CPUA64_LIB OBJECT
        BE/CpuA64/symbolic.cc
        BE/CpuA64/symbolic.h
        BE/CpuA64/assembler.cc
        BE/CpuA64/assembler.h
        BE/CpuA64/opcode_gen.cc
        BE/CpuA64/opcode_gen.h
)

add_library(CPUA64_LITE_LIB OBJECT
        BE/CpuA64/symbolic.cc
        BE/CpuA64/symbolic.h
        BE/CpuA64/opcode_gen.cc
        BE/CpuA64/opcode_gen.h
)

add_library(CPUX64_LIB OBJECT
        BE/CpuX64/symbolic.cc
        BE/CpuX64/symbolic.h
        BE/CpuX64/assembler.cc
        BE/CpuX64/assembler.h
        BE/CpuX64/opcode_gen.cc
        BE/CpuX64/opcode_gen.h
)

add_library(CPUX64_LITE_LIB OBJECT
        BE/CpuX64/symbolic.cc
        BE/CpuX64/symbolic.h
        BE/CpuX64/opcode_gen.cc
        BE/CpuX64/opcode_gen.h
)

add_executable(a64_opcode_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA64_LITE_LIB>
        BE/CpuA64/opcode_test.cc
)

add_executable(a64_disassembler_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA64_LITE_LIB>
        BE/CpuA64/disassembler_tool.cc
)

add_executable(a64_assembler_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA64_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        BE/CpuA64/assembler_tool.cc
)

add_executable(x64_disassembler_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUX64_LITE_LIB>
        BE/CpuX64/disassembler_tool.cc
)

add_executable(x64_assembler_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUX64_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        BE/CpuX64/assembler_tool.cc
)

add_library(ELF_LIB OBJECT
        BE/Elf/enum_gen.cc
        BE/Elf/enum_gen.h
        BE/Elf/elfhelper.cc
        BE/Elf/elfhelper.h
        BE/Elf/elf_unit.h)

add_library(BASE_LIB OBJECT
        Base/canonicalize.cc
        Base/canonicalize.h
        Base/cfg.cc
        Base/cfg.h
        Base/eval.cc
        Base/eval.h
        Base/ir.cc
        Base/ir.h
        Base/liveness.cc
        Base/liveness.h
        Base/lowering.cc
        Base/lowering.h
        Base/opcode_gen.cc
        Base/opcode_gen.h
        Base/sanity.cc
        Base/sanity.h
        Base/serialize.cc
        Base/serialize.h
        Base/reaching_defs.cc
        Base/reaching_defs.h
        Base/reg_stats.cc
        Base/reg_stats.h
        Base/reg_alloc.cc
        Base/reg_alloc.h
        Base/optimize.cc
        Base/optimize.h
)

add_executable(optimize_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        Base/optimize_tool.cc
)

add_executable(elf_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        BE/Elf/elf_tool.cc
)

add_executable(gen_elf_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        BE/Elf/gen_elf_test.cc
)

add_executable(a32_assembler_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA32_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        CpuA32/assembler_tool.cc
)

add_executable(a32_disassembler_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA32_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        CpuA32/disassembler_tool.cc
)

add_library(CODEGENA32_LIB OBJECT
        CodeGenA32/isel_gen.cc
        CodeGenA32/isel_gen.h
        CodeGenA32/codegen.cc
        CodeGenA32/codegen.h
        CodeGenA32/legalize.cc
        CodeGenA32/legalize.h
        CodeGenA32/regs.cc
        CodeGenA32/regs.h
)

add_executable(a32_isel_tester.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA32_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CODEGENA32_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        CodeGenA32/isel_tester.cc
)

add_executable(a32_codegen_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA32_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CODEGENA32_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        CodeGenA32/codegen_tool.cc
)

add_library(CODEGENA64_LIB OBJECT
        CodeGenA64/isel_gen.cc
        CodeGenA64/isel_gen.h
        CodeGenA64/codegen.cc
        CodeGenA64/codegen.cc
        CodeGenA64/codegen.h
        CodeGenA64/legalize.cc
        CodeGenA64/legalize.h
        CodeGenA64/regs.cc
        CodeGenA64/regs.h
)

add_executable(a64_isel_tester.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA64_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CODEGENA64_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        CodeGenA64/isel_tester.cc
)

add_executable(a64_codegen_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA64_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CODEGENA64_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        CodeGenA64/codegen_tool.cc
)

add_library(CODEGENX64_LIB OBJECT
        CodeGenX64/isel_gen.cc
        CodeGenX64/isel_gen.h
        CodeGenX64/isel_gen_patterns.h
        CodeGenX64/codegen.cc
        CodeGenX64/codegen.h
        CodeGenX64/legalize.cc
        CodeGenX64/legalize.h
        CodeGenX64/regs.cc
        CodeGenX64/regs.h
)

add_executable(x64_isel_tester.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUX64_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CODEGENX64_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        CodeGenX64/isel_tester.cc
)

add_executable(x64_codegen_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUX64_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CODEGENX64_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        CodeGenX64/codegen_tool.cc
)

add_executable(builder_example.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        Examples/fib_ir.h
        Examples/builder_example.cc
)

# this only works when (cross) compiled for a32
add_executable(jit_cpu_a32.exe EXCLUDE_FROM_ALL
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CPUA32_LIB>
        Examples/jit_cpu_a32.cc
)

# this only works when (cross) compiled for a32
add_executable(jit_ir_a32.exe EXCLUDE_FROM_ALL
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CPUA32_LIB>
        $<TARGET_OBJECTS:CODEGENA32_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        Examples/fib_ir.h
        Examples/jit_ir_a32.cc
)

# this only works when (cross) compiled for a64
add_executable(jit_cpu_a64.exe EXCLUDE_FROM_ALL
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CPUA64_LIB>
        Examples/jit_cpu_a64.cc
)

# this only works when (cross) compiled for a64
add_executable(jit_ir_a64.exe EXCLUDE_FROM_ALL
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CPUA64_LIB>
        $<TARGET_OBJECTS:CODEGENA64_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        Examples/fib_ir.h
        Examples/jit_ir_a64.cc
)

# this only works when (cross) compiled for x64
add_executable(jit_cpu_x64.exe EXCLUDE_FROM_ALL
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CPUX64_LIB>
        Examples/jit_cpu_x64.cc
)

# this only works when (cross) compiled for x64
add_executable(jit_ir_x64.exe EXCLUDE_FROM_ALL
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CPUX64_LIB>
        $<TARGET_OBJECTS:CODEGENX64_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        Examples/fib_ir.h
        Examples/jit_ir_x64.cc
)

add_executable(example_c_fib
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CPUX64_LIB>
        $<TARGET_OBJECTS:CODEGENX64_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        BindingsC/cwerg.h
        BindingsC/cwerg.cc
        BindingsC/example_fib.c
)
